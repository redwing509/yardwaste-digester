# Rollback
- Repo: `git revert` the commits that added sim/ and membranes/ (or `git rm -r sim membranes`, then commit). Backup tarball of the pre-change repo: /workspace/backups/yardwaste-digester-repo-20261031-pre-sim.tgz on the box.
- Box software: `rm -rf /workspace/venv-ywsim` (self-contained venv; nothing installed system-wide).
- Queue: delete `/workspace/boxqueue/pending/221-yw-sim-baselines.sh` if it hasn't started yet.
