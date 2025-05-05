import os
import time
import random
import numpy as np

PIPE_PATH = "/tmp/hw_data_pipe"
MODEL_PIPE_PATH = "/tmp/model_data_pipe"
SAMPLE_INTERVAL = 0.1

def ensure_pipe():
    """Create the named pipe if it doesn't exist."""
    if not os.path.exists(PIPE_PATH):
        os.mkfifo(PIPE_PATH)
    if not os.path.exists(MODEL_PIPE_PATH):
        os.mkfifo(MODEL_PIPE_PATH)
    
def pipe(log_entry):
    try:
        with open(PIPE_PATH, 'w') as pipe:
            pipe.write(log_entry)
        with open(MODEL_PIPE_PATH, 'w') as model_pipe:
            model_pipe.write(log_entry)
            
    except BrokenPipeError:
        print("[HW Emulator] Reader disconnected. Waiting to retry...")
        time.sleep(1)
    except Exception as e:
        print(f"[HW Emulator] Error: {e}")
        time.sleep(1)

def generate_sensor_data(sensor_id: int) -> str:
    """Create a single line of sensor data in string format."""
    timestamp = int(time.time() * 1000)
    values = [f"{random.uniform(0, 100):.2f}" for _ in range(2)]
    return f"{sensor_id}{timestamp}{'-'.join(values)}"

def generate_payload() -> str:
    """Generate data for multiple sensors."""
    return generate_sensor_data(random.uniform(0,4)) + "\n"

def test_loop():
    while True:
        time.sleep(SAMPLE_INTERVAL * 10)
        timestamp = str(int(time.time() * 1000))  # 13-digit timestamp in ms
        sensor_lines = ""
        sensor_lines += f"1{timestamp}{int(np.random.uniform(60, 100))}\n"  # Simulated BPM
        sensor_lines += f"2{timestamp}{int(np.random.uniform(90, 100))}\n"  # Simulated SpO2
        sensor_lines += f"3{timestamp}{int(np.random.uniform(36, 38))}\n"  # Simulated Temperature
        sensor_lines += f"4{timestamp}{int(np.random.uniform(0, 1023))}\n"  # Simulated ECG value
        sensor_lines += f"5{timestamp}{np.random.uniform(0, 10)}|{np.random.uniform(-2, 2)}|{np.random.uniform(-2, 2)}|{np.random.uniform(-2, 2)}|{np.random.uniform(-200, 200)}|{np.random.uniform(-200, 200)}\n"
        print(sensor_lines)
        pipe(sensor_lines)
        
def start_hardware_emulator():
    ensure_pipe()
    test_loop()
if __name__ == "__main__":
    start_hardware_emulator()
