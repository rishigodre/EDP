from collections import deque
import numpy as np

WINDOW_SIZE = 10  # Keep enough data for pattern matching
SAMPLE_RATE = 10  # Hz

# Thresholds for pattern-based fall detection
FREE_FALL_THRESHOLD = 0.5     # Gs
IMPACT_THRESHOLD = 2.5        # Gs
POST_FALL_MEAN_THRESHOLD = 0.8
POST_FALL_WINDOW = 5         # samples

# Thresholds for state classification
MOTION_THRESHOLD = 3.0
SLEEP_STD_THRESHOLD = 0.2

accel_magnitudes = deque(maxlen=WINDOW_SIZE)
jerk_values = deque(maxlen=WINDOW_SIZE)
last_vector = None

def detect_fall_pattern(mags):
    for i in range(1, len(mags) - POST_FALL_WINDOW):
        if mags[i] < FREE_FALL_THRESHOLD:
            for j in range(i+1, min(i+5, len(mags))):
                if mags[j] > IMPACT_THRESHOLD:
                    post_fall = mags[j+1 : j+1+POST_FALL_WINDOW]
                    if len(post_fall) < POST_FALL_WINDOW:
                        continue
                    if np.mean(post_fall) < POST_FALL_MEAN_THRESHOLD:
                        return True
    return False

def classify_motion(x, y, z):
    global last_vector

    current_vector = np.array([x, y, z])
    magnitude = np.linalg.norm(current_vector)
    accel_magnitudes.append(magnitude)

    if last_vector is not None:
        jerk = np.linalg.norm(current_vector - last_vector) * SAMPLE_RATE
        jerk_values.append(jerk)
    last_vector = current_vector

    if len(accel_magnitudes) < WINDOW_SIZE:
        return "COLLECTING DATA"

    # Pattern-based fall detection
    if detect_fall_pattern(list(accel_magnitudes)):
        return "FELL DOWN"

    # Fallback classification
    avg_jerk = np.mean(jerk_values)
    print(avg_jerk)
    
    std_magnitude = np.std(accel_magnitudes)
    print(std_magnitude)

    if std_magnitude < SLEEP_STD_THRESHOLD and avg_jerk < 0.5:
        return "SLEEPING"
    elif avg_jerk > MOTION_THRESHOLD:
        return "MINOR MOTION"
    else:
        return "STABLE"
