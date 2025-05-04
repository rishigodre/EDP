import numpy as np
import pandas as pd
import pickle

# Load model
with open('fall_detection_model.pkl', 'rb') as f:
    model = pickle.load(f)

def get_real_time_data():
     #function for picking data idhar
    pass


outcome_dict = {0: 'No Fall detected', 1: 'Slip detected', 2: 'Definite fall'}

while True:
    try:
        bpm, spo2, jerk = get_real_time_data()

        test_data = pd.DataFrame([{
            'HRV': 50,           # Replace with actual value
            'SpO2': 97,          # Replace with actual value
            'Accelerometer': 1.2 # Replace with actual value
        }])


        pred = model.predict(test_data)[0]
        print(f"Prediction: {outcome_dict[pred]}")


        sleep(1)  

    except KeyboardInterrupt:
        break



