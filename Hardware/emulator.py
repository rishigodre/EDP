import os
import time
import random

PIPE_PATH = "/tmp/hw_data_pipe"

def ensure_pipe():
    """Create the named pipe if it doesn't exist."""
    if not os.path.exists(PIPE_PATH):
        os.mkfifo(PIPE_PATH)


def generate_sensor_data(sensor_id: int) -> str:
    """Create a single line of sensor data in string format."""
    timestamp = int(time.time() * 1000)
    values = [f"{random.uniform(0, 100):.2f}" for _ in range(2)]
    return f"{sensor_id}{timestamp}{'-'.join(values)}"

def generate_payload() -> str:
    """Generate data for multiple sensors."""
    return generate_sensor_data(random.uniform(0,4)) + "\n"

def start_hardware_emulator():
    ensure_pipe()

    print(f"[HW Emulator] Writing to FIFO at {PIPE_PATH}")
    while True:
        try:
            with open(PIPE_PATH, 'w') as pipe:
                while True:
                    payload = generate_payload()
                    pipe.write(payload)
                    pipe.flush()
                    print(f"[HW Emulator] Sent:\n{payload}")
                    time.sleep(0.001)
        except BrokenPipeError:
            print("[HW Emulator] Reader disconnected. Waiting to retry...")
            time.sleep(1)
        except Exception as e:
            print(f"[HW Emulator] Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    start_hardware_emulator()
