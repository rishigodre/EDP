import os
import time

PIPE_PATH = "/tmp/hw_data_pipe"
MODEL_PIPE_PATH = "/tmp/model_data_pipe"

def ensure_pipes():
    # if not os.path.exists(PIPE_PATH):
    #     os.mkfifo(PIPE_PATH)
    if not os.path.exists(MODEL_PIPE_PATH):
        os.mkfifo(MODEL_PIPE_PATH)

def write_to_pipes(data: str):
    try:
        with open(PIPE_PATH, 'w') as pipe:
            pipe.write(data)
        with open(MODEL_PIPE_PATH, 'w') as model_pipe:
            model_pipe.write(data)
    except BrokenPipeError:
        print("[HW Emulator] Pipe not connected. Retrying...")
        time.sleep(1)
    except Exception as e:
        print(f"[HW Emulator] Error: {e}")
        time.sleep(1)

def format_sensor_data(bpm, spo2, temp, ecg, jerk, accx, accy, accz, gyrox, gyroy, gyroz):
    timestamp = str(int(time.time() * 1000))
    lines = []
    lines.append(f"1{timestamp}{int(bpm)}\n")
    lines.append(f"2{timestamp}{int(spo2)}\n")
    lines.append(f"3{timestamp}{int(temp)}\n")
    lines.append(f"4{timestamp}{int(ecg)}\n")
    lines.append(f"5{timestamp}{jerk:.2f}|{accx:.2f}|{accy:.2f}|{accz:.2f}|{gyrox:.2f}|{gyroy:.2f}|{gyroz:.2f}\n")
    return ''.join(lines)
