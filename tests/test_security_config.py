"""Checks that security automation matches this repository.

CodeQL is limited to Python with build-mode none. Dependabot lists only
package ecosystems that have something real to update. A Python import with
no manifest does not count.
"""

import os
import re
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}
SHA_USE = re.compile(
    r"^uses:\s+[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@[0-9a-f]{40}\s+#\s+v\d+\.\d+\.\d+\s*$"
)
CRON = re.compile(r"^(\S+\s+){4}\S+$")
PIP_FILENAMES = {
    "requirements.txt",
    "pyproject.toml",
    "pipfile",
    "pipfile.lock",
    "setup.py",
}
OTHER_MANIFESTS = {
    "package.json": "npm",
    "package-lock.json": "npm",
    "npm-shrinkwrap.json": "npm",
    "go.mod": "gomod",
    "cargo.toml": "cargo",
    "pom.xml": "maven",
    "gemfile": "bundler",
    "composer.json": "composer",
    "dockerfile": "docker",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
}


def strip_comment(line):
    in_single = in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return line[:i]
    return line


def parse_scalar(raw):
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    if s == "true":
        return True
    if s == "false":
        return False
    if s in ("null", "~", ""):
        return None
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    return s


def split_key(content):
    match = re.match(r"^([A-Za-z0-9_-]+):(.*)$", content)
    if not match:
        raise ValueError(f"expected key: value, got {content!r}")
    rest = match.group(2)
    if rest != "" and not rest.startswith(" "):
        raise ValueError(f"colon is not a key separator in {content!r}")
    return match.group(1), rest.strip()


def meaningful_lines(text):
    lines = []
    for raw in text.splitlines():
        code = strip_comment(raw).rstrip()
        if not code.strip():
            continue
        indent = len(code) - len(code.lstrip(" "))
        if code[:indent] != " " * indent:
            raise ValueError("tabs are not allowed in the security YAML")
        lines.append((indent, code.strip()))
    return lines


def parse_yaml(text):
    lines = meaningful_lines(text)
    if not lines:
        raise ValueError("empty YAML")
    value, idx = parse_node(lines, 0)
    if idx != len(lines):
        raise ValueError(f"unparsed YAML at {lines[idx][1]!r}")
    return value


def parse_node(lines, idx):
    indent, content = lines[idx]
    if content.startswith("-"):
        return parse_list(lines, idx, indent)
    return parse_map(lines, idx, indent)


def parse_map(lines, idx, indent):
    result = {}
    while idx < len(lines) and lines[idx][0] == indent:
        content = lines[idx][1]
        if content.startswith("-"):
            break
        key, val = split_key(content)
        if key in result:
            raise ValueError(f"duplicate key {key}")
        idx += 1
        result[key], idx = assign_value(val, lines, idx, indent)
    return result, idx


def assign_value(val, lines, idx, parent_indent):
    if val != "":
        return parse_scalar(val), idx
    if idx >= len(lines) or lines[idx][0] <= parent_indent:
        return None, idx
    return parse_node(lines, idx)


def parse_list(lines, idx, indent):
    items = []
    while idx < len(lines) and lines[idx][0] == indent and lines[idx][1].startswith("-"):
        rest = lines[idx][1][1:].strip()
        idx += 1
        if rest == "":
            node, idx = parse_node(lines, idx)
            items.append(node)
        elif re.match(r"^[A-Za-z0-9_-]+:", rest):
            item, idx = parse_list_item_map(rest, lines, idx, indent)
            items.append(item)
        else:
            items.append(parse_scalar(rest))
    return items, idx


def parse_list_item_map(first, lines, idx, dash_indent):
    key, val = split_key(first)
    item = {}
    item[key], idx = assign_value(val, lines, idx, dash_indent)
    key_indent = None
    while idx < len(lines) and lines[idx][0] > dash_indent:
        ind, content = lines[idx]
        if content.startswith("-"):
            break
        if key_indent is None:
            key_indent = ind
        if ind != key_indent:
            raise ValueError(f"unexpected indent before {content!r}")
        child, child_val = split_key(content)
        if child in item:
            raise ValueError(f"duplicate key {child}")
        idx += 1
        item[child], idx = assign_value(child_val, lines, idx, ind)
    return item, idx


def workflows(root):
    directory = Path(root) / ".github" / "workflows"
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.yml")) + sorted(directory.glob("*.yaml"))


def uses_published_action(text):
    return re.search(
        r"(?m)^\s*-?\s*uses:\s*[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@",
        text,
    ) is not None


def applicable_ecosystems(root):
    found = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        lowered = {name.lower() for name in filenames}
        if lowered & PIP_FILENAMES or any(
            name.lower().startswith("requirements") and name.lower().endswith(".txt")
            for name in filenames
        ):
            found.add("pip")
        for filename, ecosystem in OTHER_MANIFESTS.items():
            if filename in lowered:
                found.add(ecosystem)
    if any(uses_published_action(path.read_text()) for path in workflows(root)):
        found.add("github-actions")
    return found


def load(path):
    return parse_yaml(Path(path).read_text())


def steps_using(job, prefix):
    return [step for step in job["steps"] if str(step.get("uses", "")).startswith(prefix)]


class TestYamlParser(unittest.TestCase):
    def test_dependabot_shape(self):
        parsed = parse_yaml(
            """
version: 2
updates:
  - package-ecosystem: github-actions
    directory: "/"
    schedule:
      interval: weekly
    groups:
      actions:
        patterns:
          - "*"
"""
        )
        self.assertEqual(parsed["version"], 2)
        update = parsed["updates"][0]
        self.assertEqual(update["package-ecosystem"], "github-actions")
        self.assertEqual(update["directory"], "/")
        self.assertEqual(update["schedule"]["interval"], "weekly")
        self.assertEqual(update["groups"]["actions"]["patterns"], ["*"])

    def test_workflow_shape_keeps_on_key(self):
        parsed = parse_yaml(
            """
name: Example
on:
  push:
    branches:
      - main
jobs:
  analyze:
    steps:
      - name: Initialize CodeQL
        uses: github/codeql-action/init@0123456789abcdef0123456789abcdef01234567 # v4.39.3
        with:
          languages: python
          build-mode: none
"""
        )
        self.assertIn("on", parsed)
        self.assertEqual(parsed["on"]["push"]["branches"], ["main"])
        step = parsed["jobs"]["analyze"]["steps"][0]
        self.assertEqual(step["with"]["languages"], "python")
        self.assertEqual(step["with"]["build-mode"], "none")


class TestApplicabilityRules(unittest.TestCase):
    def test_empty_tree_has_no_ecosystem(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(applicable_ecosystems(tmp), set())

    def test_action_use_is_github_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            workflow = Path(tmp) / ".github" / "workflows"
            workflow.mkdir(parents=True)
            (workflow / "ci.yml").write_text(
                "jobs:\n  t:\n    steps:\n      - uses: actions/checkout@0123456789abcdef0123456789abcdef01234567 # v7.0.1\n"
            )
            self.assertEqual(applicable_ecosystems(tmp), {"github-actions"})

    def test_run_only_workflow_is_not_an_action_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            workflow = Path(tmp) / ".github" / "workflows"
            workflow.mkdir(parents=True)
            (workflow / "ci.yml").write_text("jobs:\n  t:\n    steps:\n      - run: python3 -m unittest\n")
            self.assertEqual(applicable_ecosystems(tmp), set())

    def test_requirements_file_is_pip(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "requirements.txt").write_text("numpy==1.26.4\n")
            self.assertEqual(applicable_ecosystems(tmp), {"pip"})

    def test_import_without_manifest_is_not_pip(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "src"
            source.mkdir()
            (source / "model.py").write_text("import numpy\nfrom exposan.adm import system\n")
            self.assertEqual(applicable_ecosystems(tmp), set())


class TestRepoSecurityConfig(unittest.TestCase):
    def test_dependabot_matches_real_ecosystems_only(self):
        applicable = applicable_ecosystems(REPO)
        self.assertEqual(applicable, {"github-actions"})
        config = load(REPO / ".github" / "dependabot.yml")
        self.assertEqual(config["version"], 2)
        updates = config["updates"]
        self.assertTrue(updates)
        self.assertEqual({item["package-ecosystem"] for item in updates}, applicable)
        for item in updates:
            self.assertTrue(item["directory"])
            self.assertIn(item["schedule"]["interval"], {"daily", "weekly", "monthly"})
        actions = next(item for item in updates if item["package-ecosystem"] == "github-actions")
        self.assertEqual(actions["directory"], "/")
        self.assertEqual(actions["schedule"]["interval"], "weekly")

    def test_codeql_is_python_without_a_build(self):
        path = REPO / ".github" / "workflows" / "codeql.yml"
        text = path.read_text()
        workflow = parse_yaml(text)
        self.assertEqual(workflow["on"]["push"]["branches"], ["main"])
        self.assertEqual(workflow["on"]["pull_request"]["branches"], ["main"])
        cron = workflow["on"]["schedule"][0]["cron"]
        self.assertRegex(cron, CRON)
        self.assertNotIn("pull_request_target", text)
        self.assertNotIn("secrets.", text)

        job = workflow["jobs"]["analyze"]
        self.assertEqual(
            job["permissions"],
            {
                "security-events": "write",
                "packages": "read",
                "actions": "read",
                "contents": "read",
            },
        )
        init = steps_using(job, "github/codeql-action/init@")
        analyze = steps_using(job, "github/codeql-action/analyze@")
        self.assertEqual(len(init), 1)
        self.assertEqual(len(analyze), 1)
        self.assertEqual(init[0]["with"], {"languages": "python", "build-mode": "none"})
        self.assertEqual(analyze[0]["with"]["category"], "/language:python")
        self.assertFalse(steps_using(job, "github/codeql-action/autobuild@"))
        joined = " ".join(str(step.get("run", "")) for step in job["steps"])
        self.assertNotIn("pip install", joined)
        self.assertNotIn("python,javascript", text)

    def test_tests_workflow_runs_both_suites_read_only(self):
        path = REPO / ".github" / "workflows" / "tests.yml"
        text = path.read_text()
        workflow = parse_yaml(text)
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        self.assertEqual(workflow["on"]["pull_request"]["branches"], ["main"])
        self.assertNotIn("pull_request_target", text)
        self.assertNotIn("secrets.", text)
        runs = [step["run"] for step in workflow["jobs"]["unit"]["steps"] if "run" in step]
        self.assertIn("python3 -m unittest discover -s tests -v", runs)
        diy = [
            step
            for step in workflow["jobs"]["unit"]["steps"]
            if step.get("working-directory") == "diy"
        ]
        self.assertEqual(diy[0]["run"], "python3 -m unittest discover -s tests -v")
        setup = steps_using(workflow["jobs"]["unit"], "actions/setup-python@")
        self.assertEqual(setup[0]["with"]["python-version"], "3.12")

    def test_published_actions_are_sha_pinned(self):
        for path in workflows(REPO):
            for line in path.read_text().splitlines():
                if "uses:" not in strip_comment(line):
                    continue
                self.assertRegex(line.strip(), SHA_USE, path.name)


if __name__ == "__main__":
    unittest.main()
