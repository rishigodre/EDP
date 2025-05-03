import time
from max30100 import MAX30100
import numpy as np
from collections import deque
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from gpiozero import DigitalInputDevice
from mpu6050_i2c import *
import os
SAMPLE_INTERVAL = 0.001 

# Constants for logging
HWID = "9334de0b9ebd424d95e40d338953137e"
HW_PASSWORD = "A1B2C3D4E5F6G7H8"
PIPE_PATH = "tmp/hw_data_pipe"

# Function for peak detection 
def detect_peaks(signal, threshold):
    peaks = []
    for i in range(1, len(signal)-1):
        if signal[i] > threshold and signal[i] > signal[i-1] and signal[i] > signal[i+1]:
            peaks.append(i)
    return peaks

# Function for calculation of Beats per minute 
def calculate_bpm(peaks, times):
    if len(peaks) < 2:
        return None
    intervals = [times[peaks[i]] - times[peaks[i-1]] for i in range(1, len(peaks))]
    avg_interval = np.mean(intervals)
    return 60 / avg_interval if avg_interval > 0 else None

# Function for SpO2% estimation
def basic_spo2_estimation(ir, red):
    if ir and red:
        ratio = red / (ir + 1)
        return max(0, min(100, 110 - 15 * ratio))
    return None

def ensure_pipe():
    if not os.path.exists(PIPE_PATH):
        os.mkfifo(PIPE_PATH)
        print(f"[HW Emulator] Created FIFO at {PIPE_PATH}")
        
def pipe(log_entry):
    with open(PIPE_PATH, "w") as f:
        f.write(log_entry)
        try:
            with open(PIPE_PATH, 'w') as pipe:
                pipe.write(log_entry)
        except BrokenPipeError:
            print("[HW Emulator] Reader disconnected. Waiting to retry...")
            time.sleep(1)
        except Exception as e:
            print(f"[HW Emulator] Error: {e}")
            time.sleep(1)

def main():
    ensure_pipe()
    lo_plus = DigitalInputDevice(14)  # GPIO14 (Pin 8)
    lo_minus = DigitalInputDevice(15)  # GPIO15 (Pin 10)

    i2c = busio.I2C(board.SCL, board.SDA)

    oldG = 1

    x_len = 500
    ys = [0] * x_len

    max30 = MAX30100(
        mode = 0x03,
        sample_rate = 100,
        pulse_width = 1600,
        led_current_red = 27.1,
        led_current_ir = 27.1
    )
    max30.enable_spo2()

    ir_data = deque(maxlen=500)
    red_data = deque(maxlen=500)
    timestamps = deque(maxlen=500)

    adc = ADS1115(i2c)
    adc.gain = 1
    chan = AnalogIn(adc, 0)

    try:
        print("Monitoring... Press Ctrl+C to stop.")
        while True:
            try:
                ax, ay, az, wx, wy, wz = mpu6050_conv()
            except:
                continue

            netG = (ax ** 2 + ay ** 2 + az ** 2) ** 0.5
            jerkMag = (netG - oldG) / SAMPLE_INTERVAL
            oldG = netG

            max30.read_sensor()
            ir = max30.ir
            red = max30.red
            t = time.time()

            if ir is None or ir < 1000:
                time.sleep(0.1)
                continue

            ir_data.append(ir)
            red_data.append(red)
            timestamps.append(t)

            if len(ir_data) > 100:
                peaks = detect_peaks(ir_data, threshold=np.mean(ir_data) * 1.05)
                bpm = calculate_bpm(peaks, list(timestamps)) if peaks else None
            else:
                bpm = None

            spo2 = basic_spo2_estimation(ir, red)
            max30.refresh_temperature()
            temp = max30.get_temperature()

            if lo_plus.value == 1 or lo_minus.value == 1:
                ecg_value = 0
            else:
                ecg_value = chan.value
            ys.append(ecg_value)
            ys = ys[-x_len:]

            # Logging
            current_time = time.time()
            
            # multiply time stamp by 1000 to and truncate the decimal part to get resolution of ms
            timestamp = str(int(current_time * 1000))  # 13-digit timestamp in ms
            sensor_lines = []

            if bpm is not None and spo2 is not None and temp is not None:
                sensor_lines.append(f"1{timestamp}{int(bpm)}")
                sensor_lines.append(f"2{timestamp}{int(spo2)}")
                sensor_lines.append(f"3{timestamp}{int(temp)}")
            if lo_plus.value == 0 and lo_minus.value == 0:
                sensor_lines.append(f"4{timestamp}{ecg_value}")
            sensor_lines.append(f"5{timestamp}{jerkMag}")

            log_entry = f"".join(sensor_lines) + "\n"
            pipe(log_entry)
            time.sleep(SAMPLE_INTERVAL)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
