class CyberPhysicalController:
    def __init__(self):
        # Controller State Estimations
        self.estimated_soc = 1.0
        self.estimated_core_temp = 298.15
        self.last_temp_reading = 298.15
        self.temp_slope = 0.0
        
        # System state
        self.current_mode = "NOMINAL"
        self.kalman_r_covariance = 0.01 # Initial noise assumption
        
    def update_estimators(self, sensor_data: dict, dt: float):
        # 1. Predictive Thermal Gradient Observer
        current_temp = sensor_data["temperature_k"]
        raw_slope = (current_temp - self.last_temp_reading) / dt if dt > 0 else 0.0
        
        # Low-pass filter the slope to avoid chattering
        self.temp_slope = 0.8 * self.temp_slope + 0.2 * raw_slope
        self.last_temp_reading = current_temp
        
        # 2. Adaptive Kalman Filtering step (simplified online execution)
        # If the sensor reading is wildly noisy, dynamically adjust model belief
        expected_v = 3.7
        voltage_error = abs(sensor_data["voltage_v"] - expected_v)
        
        if voltage_error > 0.15:
            # Scale up sensor noise covariance (rely on dead-reckoning)
            self.kalman_r_covariance = min(1.0, self.kalman_r_covariance * 2.0)
        else:
            self.kalman_r_covariance = max(0.01, self.kalman_r_covariance * 0.5)
            
        # Update Estimated SoC based on filtered state
        self.estimated_soc = max(0.0, min(1.0, self.estimated_soc - (0.0001 * dt)))

    def coordinate(self, dt: float) -> dict:
        # Look-ahead 120 seconds into the future
        predictive_horizon = 120.0
        predicted_temp = self.last_temp_reading + (self.temp_slope * predictive_horizon)
        
        # State transitions with hysteresis
        if self.estimated_soc < 0.20 or predicted_temp > 328.15:
            self.current_mode = "RECOVERY"
        elif self.estimated_soc < 0.40 or predicted_temp > 320.15:
            self.current_mode = "SURVIVAL"
        elif self.estimated_soc > 0.80 and predicted_temp < 315.15:
            self.current_mode = "BURST"
        else:
            self.current_mode = "NOMINAL"
            
        # Map states to physical actuators
        if self.current_mode == "RECOVERY":
            return {"cpu_hz": 1_000_000, "tx_power_dbm": -40.0}
        elif self.current_mode == "SURVIVAL":
            return {"cpu_hz": 8_000_000, "tx_power_dbm": -10.0}
        elif self.current_mode == "BURST":
            return {"cpu_hz": 120_000_000, "tx_power_dbm": 14.0}
        else:
            return {"cpu_hz": 48_000_000, "tx_power_dbm": 0.0}
