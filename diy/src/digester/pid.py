"""Small PID with anti-windup and clamped output 0..1."""


class PID:
    def __init__(self, kp, ki, kd, out_min=0.0, out_max=1.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.out_min, self.out_max = out_min, out_max
        self.integral = 0.0
        self.prev_err = None

    def reset(self):
        self.integral = 0.0
        self.prev_err = None

    def update(self, setpoint, measured, dt):
        if dt <= 0:
            raise ValueError("dt must be > 0")
        err = setpoint - measured
        deriv = 0.0 if self.prev_err is None else (err - self.prev_err) / dt
        self.prev_err = err
        trial_i = self.integral + err * dt
        out = self.kp * err + self.ki * trial_i + self.kd * deriv
        # anti-windup: only integrate if not saturating further
        if self.out_min < out < self.out_max or (out >= self.out_max and err < 0) or (out <= self.out_min and err > 0):
            self.integral = trial_i
        out = self.kp * err + self.ki * self.integral + self.kd * deriv
        return max(self.out_min, min(self.out_max, out))
