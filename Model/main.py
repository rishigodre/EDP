# main.py
import os
import time
import requests
from model1 import classify_motion

PIPE_PATH = "/tmp/model_data_pipe"
hwid = "9334de0b9ebd424d95e40d338953137e"
hwpass = "A1B2C3D4E5F6G7H8"
# 9334de0b9ebd424d95e40d338953137eA1B2C3D4E5F6G7H8register
# 9334de0b9ebd424d95e40d338953137eA1B2C3D4E5F6G7H817464705734541Slipdetected

def ensure_pipe():
    if not os.path.exists(PIPE_PATH):
        os.mkfifo(PIPE_PATH)

def send_alert(sensor_id, info):
    alert = hwid + hwpass + str(int(time.time() * 1000)) + str(sensor_id) + info
    try:
        res = requests.post(
            "http://localhost:3000/api/alert",
            data=alert,
            headers={"Content-Type": "text/plain"}
        )
        if res.status_code == 200:
            print("Alert sent successfully")
        else:
            print(f"Failed to send alert: {res.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending alert: {e}")

def parse_line(line):
    sensor_id = int(line[0])
    timestamp = int(line[1:14])
    sensor_data = line[14:].split('|')
    return sensor_id, timestamp, sensor_data

def get_real_time_data():
    try:
        with open(PIPE_PATH, 'r') as pipe:
            lines = pipe.read()
            for line in lines.split('\n'):
                if not line:
                    continue
                sensor_id, timestamp, sensor_data = parse_line(line.strip())
                if sensor_id == 5:
                    # Accel + gyro data: jerk|x|y|z|gx|gy
                    try:
                        jerk = float(sensor_data[0])
                        x = float(sensor_data[1])
                        y = float(sensor_data[2])
                        z = float(sensor_data[3])
                        print(f"Jerk: {jerk}, Accel: ({x}, {y}, {z})")
                        state = classify_motion(x, y, z)
                        print(f"Motion State: {state}")
                        if state == "FELL DOWN":
                            send_alert(1, "Definite fall detected")
                    except Exception as e:
                        print(f"Parsing error: {e}")
    except Exception as e:
        print(f"Pipe error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    ensure_pipe()
    print("Starting real-time data processing...")
    while True:
        get_real_time_data()
