# motion_classifier.py
from collections import deque
import numpy as np

WINDOW_SIZE = 5
SAMPLE_RATE = 1  # Hz

# Thresholds
FALL_THRESHOLD = 2      # general jerk threshold
Z_JERK_THRESHOLD = 1.2     # jerk on Z axis threshold
MOTION_ACC_THRESHOLD = 1 # acceleration magnitude for "in motion"
STABLE_JERK_THRESHOLD = 0.3

# Buffers
accel_magnitudes = deque(maxlen=WINDOW_SIZE)
jerk_values = deque(maxlen=WINDOW_SIZE)
last_vector = None
last_z = None

def classify_motion(x, y, z):
    global last_vector, last_z

    current_vector = np.array([x, y, z])
    current_z = z

    magnitude = np.linalg.norm(current_vector)
    accel_magnitudes.append(magnitude)

    # Calculate jerk_z (change in Z)
    jerk_z = 0
    if last_z is not None:
        jerk_z = abs(current_z - last_z) * SAMPLE_RATE
    last_z = current_z

    # Calculate overall jerk (change in full vector)
    if last_vector is not None:
        jerk = np.linalg.norm(current_vector - last_vector) * SAMPLE_RATE
        jerk_values.append(jerk)
    last_vector = current_vector

    if len(accel_magnitudes) < WINDOW_SIZE:
        return "COLLECTING DATA"

    avg_jerk = np.mean(jerk_values) if jerk_values else 0
    sum = 0
    for i in range(len(accel_magnitudes)):
        sum += accel_magnitudes[i] * (i)/len(accel_magnitudes)
    avg_acc = sum / len(accel_magnitudes)

    if jerk_z > Z_JERK_THRESHOLD or avg_jerk > FALL_THRESHOLD:
        return "FELL DOWN"
    elif avg_acc > MOTION_ACC_THRESHOLD:
        return "MOTION"
    elif avg_jerk < STABLE_JERK_THRESHOLD:
        return "STABLE"
    else:
        return "MINOR MOTION"
