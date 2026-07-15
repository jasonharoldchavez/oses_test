import time
import socket
import json
from scenarios.hil_simulation.physics import PhysicalSimulator
from scenarios.hil_simulation.engine import CyberPhysicalController

def run_loop():
    simulator = PhysicalSimulator()
    controller = CyberPhysicalController()
    
    # Optional wireless socket output (UDP broadcast on port 5005)
    # Allows tracking live state updates using any wireless device on your local network
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    addr = ('<broadcast>', 5005)

    print("\n=======================================================")
    print(" INN CYBER-PHYSICAL NODE SIMULATION INITIALIZED")
    print(" Running continuous HIL loop inside Termux environment...")
    print("=======================================================\n")
    
    dt = 1.0  # Real-time resolution cycle step (1-second intervals)
    simulated_hours = 0.0
    
    try:
        while True:
            # 1. Update the environmental simulator inputs
            # Accelerate the passage of time inside simulation to test degradation rates
            accelerated_dt = dt * 100.0  # 1 second real-time = 100 seconds simulation time
            simulated_hours += (accelerated_dt / 3600.0)
            
            # Simulate solar midday peak thermal dynamics
            simulator.ambient_temp_k = 298.15 + 15.0 * math.sin(simulated_hours * 0.26)
            
            # Read actuator states from previous loop step
            actuators = controller.coordinate(accelerated_dt)
            
            # Step the physical world model
            simulator.step(accelerated_dt, actuators["cpu_hz"], actuators["tx_power_dbm"])
            
            # Read the corrupted sensor outputs
            sensors = simulator.read_sensors()
            
            # 2. Feed the digital mind (GPMSM)
            controller.update_estimators(sensors, accelerated_dt)
            
            # 3. Print real-time status telemetry
            print(f"SimHour: {simulated_hours:6.2f} | "
                  f"Mode: {controller.current_mode:8} | "
                  f"TrueCapacity: {simulator.true_battery_capacity_as:7.1f}s | "
                  f"Est_SoC: {controller.estimated_soc*100:5.1f}% | "
                  f"TrueTemp: {simulator.true_core_temp_k - 273.15:5.1f}°C | "
                  f"SensTemp: {sensors['temperature_k'] - 273.15:5.1f}°C | "
                  f"Drift: {simulator.temp_sensor_drift:5.2f}K")
            
            # Assemble telemetry payload
            payload = {
                "simulated_hours": simulated_hours,
                "mode": controller.current_mode,
                "battery_health_pct": (simulator.true_battery_capacity_as / 3600.0) * 100.0,
                "temperature_sensor_drift": simulator.temp_sensor_drift,
                "harvester_degraded": simulator.microcracks_occurred
            }
            
            # Send payload across local network interface
            try:
                sock.sendto(json.dumps(payload).encode(), addr)
            except Exception:
                pass # Fail silently if network interface is temporarily down
                
            time.sleep(dt) # Hold pacing
            
    except KeyboardInterrupt:
        print("\n[+] Simulation halted safely by user.")

if __name__ == "__main__":
    import math
    run_loop()
