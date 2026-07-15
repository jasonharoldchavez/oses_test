import math
import random

class PhysicalSimulator:
    def __init__(self):
        # Hidden Truths (True state of the universe)
        self.true_battery_capacity_as = 3600.0  # 1.0 Ah nominal
        self.true_core_temp_k = 298.15          # Start at room temp (25°C)
        self.true_harvester_efficiency = 1.0    # 100% capacity initially
        self.battery_throughput_ah = 0.0
        
        # Environmental Inputs
        self.ambient_temp_k = 298.15
        self.base_vibration_g = 1.0
        
        # Fault Parameters
        self.temp_sensor_drift = 0.0
        self.microcracks_occurred = False
        
    def step(self, dt_sec: float, cpu_freq_hz: float, tx_power_dbm: float):
        # 1. Calculate Internal Power Consumption based on controller state
        # CPU power model: P = C * V^2 * f
        cpu_power = 0.05 * (cpu_freq_hz / 120_000_000.0)
        # Radio power model
        radio_power = 0.01 if tx_power_dbm < 0 else 0.25 * (10 ** (tx_power_dbm / 10.0)) / 10.0
        total_power_demand = cpu_power + radio_power
        
        # 2. Energy Harvesting Input (Piezoelectric)
        # Non-linear harvesting efficiency decays over high vibration cycles
        harvest_input = 0.15 * self.base_vibration_g * self.true_harvester_efficiency
        
        # 3. Energy Balance on Storage (Supercapacitor/Battery)
        net_current = (total_power_demand - harvest_input) / 3.7 # I = P/V
        self.battery_throughput_ah += abs(net_current) * (dt_sec / 3600.0)
        
        # 4. Battery Capacity Decay (Arrhenius & Power Law)
        # Simulates chemical capacity fade over usage cycles
        arrhenius = math.exp(-3608.0 / self.true_core_temp_k)
        power_law = (self.battery_throughput_ah + 0.01) ** 0.55
        self.true_battery_capacity_as -= 0.015 * power_law * arrhenius * dt_sec
        self.true_battery_capacity_as = max(self.true_battery_capacity_as, 10.0)
        
        # 5. Thermal Dynamics (Conjugate Heat Transfer Approximation)
        # T_dot = Heat_In - Heat_Out
        heat_generated = total_power_demand * 0.15
        heat_dissipated = 0.02 * (self.true_core_temp_k - self.ambient_temp_k)
        self.true_core_temp_k += (heat_generated - heat_dissipated) * dt_sec
        
        # 6. Apply Injected Faults & Material Degradation
        # Temperature sensor drift (slow thermal-cycling walk)
        thermal_cycling_stress = abs(self.true_core_temp_k - 298.15)
        self.temp_sensor_drift += (random.random() - 0.5) * 0.0005 * thermal_cycling_stress * dt_sec
        
        # Harvester decay (Weibull fatigue failure representation)
        if self.battery_throughput_ah > 5.0:  # Threshold after high simulated wear
            self.microcracks_occurred = True
            self.true_harvester_efficiency = max(0.4, self.true_harvester_efficiency - (0.01 * dt_sec))

    def read_sensors(self) -> dict:
        # Add sensor error and drift to physical realities before sending them to the controller
        measured_temp = self.true_core_temp_k + self.temp_sensor_drift
        measured_voltage = 3.7 + (random.random() - 0.5) * 0.05 # Add sensor noise
        
        return {
            "temperature_k": measured_temp,
            "voltage_v": measured_voltage,
            "harvester_active": not self.microcracks_occurred
        }
