import numpy as np
import pandas as pd
import pickle
import time
import requests

hwid = "9334de0b9ebd424d95e40d338953137e"
hwpass = "A1B2C3D4E5F6G7H8"


# Load model
with open('fall_detection_model.pkl', 'rb') as f:
    model = pickle.load(f)

import os
import time

PIPE_PATH = "/tmp/model_data_pipe"  # Replace with your actual pipe path

values = dict()
values['bpm'] = 0.0
values['spo2'] = 0.0
values['jerk'] = 0.0

def ensure_pipe():
    if not os.path.exists(PIPE_PATH):
        os.mkfifo(PIPE_PATH)

def get_real_time_data():
    try:
        with open(PIPE_PATH, 'r') as pipe:
            lines = pipe.read()
            print(lines)
            if not lines:
                time.sleep(0.1)
            for line in lines.split('\n'):
                if not line:
                    continue
                line = line.strip()
                if line:
                    sensor_id = int(line[0])
                    timestamp = int(line[1:14])
                    sensor_data = line[14:].split('|')
                    if sensor_id == 1:
                        values['bpm'] = float(sensor_data[0])
                    elif sensor_id == 2:
                        values['spo2'] = float(sensor_data[0])
                    elif sensor_id == 5:
                        values['jerk'] = float(sensor_data[0])
    except Exception as e:
        print(f"Pipe error: {e}")
        time.sleep(1)
                    
def send_alert(sensor_id, info):
    alert = ""
    alert += hwid
    alert += hwpass
    alert += str(int(time.time() * 1000))  # 13-digit timestamp in ms
    alert += str(sensor_id)
    alert += info    
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
        

outcome_dict = {0: 'No Fall detected', 1: 'Slip detected', 2: 'Definite fall'}
ensure_pipe()
print("Starting real-time data processing...")
while True:
    try:
        get_real_time_data()

        test_data = pd.DataFrame([{
            'HRV': float(values['bpm']),           # Replace with actual value
            'SpO2': float(values['spo2']),          # Replace with actual value
            'Accelerometer': float(values['jerk']) # Replace with actual value
        }])
        print(test_data)
        pred = model.predict(test_data)[0]
        print(f"Prediction: {outcome_dict[pred]}")
        if pred == 2:
            send_alert(1, "Definite fall detected")
        elif pred == 1:
            send_alert(1, "Slip detected")
        else:
            print("No fall detected")


    except KeyboardInterrupt:
        break



