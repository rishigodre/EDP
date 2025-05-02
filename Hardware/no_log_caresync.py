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

SAMPLE_INTERVAL = 0.001 

# function for peak detection 
def detect_peaks(signal, threshold):
    peaks = []
    for i in range(1, len(signal)-1):
        if signal[i] > threshold and signal[i] > signal[i-1] and signal[i] > signal[i+1]:
            peaks.append(i)
    return peaks

# functions for calculation of Beats per minute 
def calculate_bpm(peaks, times):
    if len(peaks) < 2:
        return None
    intervals = [times[peaks[i]] - times[peaks[i-1]] for i in range(1, len(peaks))]
    avg_interval = np.mean(intervals)
    return 60 / avg_interval if avg_interval > 0 else None

# function for SpO2% 
def basic_spo2_estimation(ir, red):
    if ir and red:
        ratio = red / (ir + 1)
        return max(0, min(100, 110 - 15 * ratio))
    return None

def main():
    # Setup gpiozero for LO+ and LO- pins
    lo_plus = DigitalInputDevice(14)  # GPIO14 (Pin 8)
    lo_minus = DigitalInputDevice(15)  # GPIO15 (Pin 10)

    # Initialize I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # variables using in the calculation of jerk
    oldG = 1
    #fallThreshold = 1500

    x_len = 500         # Number of points to display
    y_range = 32768     # 16-bit ADC range
    xs = list(range(0, x_len))
    ys = [0] * x_len

    # heart rate and SpO2 max30 max30 being enabled 
    max30 = MAX30100(
        mode = 0x03,
        sample_rate = 100,
        pulse_width = 1600,
        led_current_red = 27.1,
        led_current_ir = 27.1
    )
    max30.enable_spo2()

    # Ring buffers for live data
    ir_data = deque(maxlen=500)
    red_data = deque(maxlen=500)
    timestamps = deque(maxlen=500)

    # Initialize ADS1115 ADC
    adc = ADS1115(i2c)
    adc.gain = 1  # Gain of 1x (±4.096V range)
    chan = AnalogIn(adc, 0) # setting the channel for input 

    try:
        print("Monitoring... Press Ctrl+C to stop.")
        while True:
            # trying to read the accelerometer 
            try:
                ax,ay,az,wx,wy,wz = mpu6050_conv() # read and convert mpu6050 data
            except:
                continue
            # calculation of net acceleration in g and Jerk
            netG = ax * ax + ay * ay + az * az
            netG = netG ** 0.5
            jerkMag = (netG - oldG) / (SAMPLE_INTERVAL)
            # direct fall detection using jerk
            if jerkMag > fallThreshold:
                print("fall!!")
                time.sleep(0.1)
            oldG = netG
            
            #reading MAX30100 for heart reat and SpO2 
            max30.read_sensor()
            ir = max30.ir
            red = max30.red
            t = time.time()

            if ir is None or ir < 1000:
                print("[WARN] No finger detected or weak signal.")
                time.sleep(0.1)
                continue

            ir_data.append(ir)
            red_data.append(red)
            timestamps.append(t)

            # Peak detection
            if len(ir_data) > 100:
                peaks = detect_peaks(ir_data, threshold=np.mean(ir_data)*1.05)
                bpm = calculate_bpm(peaks, list(timestamps)) if peaks else None
            else:
                bpm = None

            spo2 = basic_spo2_estimation(ir, red)
            max30.refresh_temperature()
            temp = max30.get_temperature()
            print(f"Temp: {temp:.1f}°C | SpO2: {spo2:.1f}% | HR: {bpm:.1f} bpm" if bpm else "HR: --")
            
            # reading the data of ecg sensor using the ADC
            if lo_plus.value == 1 or lo_minus.value == 1:
                ecg_value = 0
                print("Lead off detected!")
            else:
                ecg_value = chan.value  # RAW ADC counts (-32768 to +32767)
                print("ECG value is :",ecg_value)
            ys.append(ecg_value)
            ys = ys[-x_len:]

            time.sleep(SAMPLE_INTERVAL)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
