class ProportionalPID:
    def __init__(self, kp=0.5, ki=0.1, kd=0.2, deadband=0.1, max_output=127):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.deadband = deadband
        self.max_output = max_output
        
        self.error_sum = 0  # 积分项累加值
        self.last_error = 0  # 上一次的误差值
        self.last_output = 127  # 初始中值
    
    def update(self, current: float, target=0.0):
        error = target - current  # 误差计算对称（正负误差同等处理）
        
        if abs(error) <= self.deadband:
            self.error_sum = 0
            return self.last_output
        
        # 比例项：正负误差对称放大（左侧误差正→输出正；右侧误差负→输出负）
        p_term = self.kp * error
        
        # 积分项：正负误差累积对称（左侧正误差累积→输出增加；右侧负误差累积→输出减少）
        self.error_sum += error
        self.error_sum = max(-1000, min(self.error_sum, 1000))  # 积分限幅（对称范围）
        i_term = self.ki * self.error_sum
        
        # 微分项：正负变化率对称抑制（左侧向中心移动→误差减小→微分负；右侧向中心移动→误差增大→微分正）
        d_term = self.kd * (error - self.last_error)
        self.last_error = error
        
        # 输出：允许正负值（左侧输出正，右侧输出负）
        # output = p_term + i_term + d_term
        # output = max(-self.max_output, min(output, self.max_output))  # 对称限幅
        # 在pid_new.py的update方法中，确保输出仅受max_output限制
        output = p_term + i_term + d_term
        output = max(-self.max_output, min(output, self.max_output))  # 仅限制在[-128, 128]
        
        self.last_output = output
        return output
    
    def reset(self):
        self.error_sum = 0
        self.last_error = 0
        self.last_output = 127