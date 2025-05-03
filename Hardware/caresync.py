import time
from max30102 import MAX30102
import hrcalc
import numpy as np
from collections import deque
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from gpiozero import DigitalInputDevice
from mpu6050_i2c import *

SAMPLE_INTERVAL = 0.01 
SAMPLE_INTERVAL = 0.001 


# Constants for logging
HWID = "9334de0b9ebd424d95e40d338953137e"
HW_PASSWORD = "A1B2C3D4E5F6G7H8"
PIPE_PATH = "tmp/hw_data_pipe"


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

    max102 = MAX30102()
    ir_data = []
    red_data = []
    bpms = []

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

            num_bytes = max102.get_data_present()
            bpm = None
            spo2 = None
            temp = None
            if num_bytes > 0:
                # grab all the data and stash it into arrays
                while num_bytes > 0:
                    red, ir = max102.read_fifo()
                    num_bytes -= 1
                    ir_data.append(ir)
                    red_data.append(red)

                while len(ir_data) > 100:
                    ir_data.pop(0)
                    red_data.pop(0)

                if len(ir_data) == 100:
                    bpm, valid_bpm, spo2, valid_spo2 = hrcalc.calc_hr_and_spo2(ir_data, red_data)
                    if valid_bpm:
                        bpms.append(bpm)
                        while len(bpms) > 4:
                            bpms.pop(0)
                        bpm = np.mean(bpms)
                        if (np.mean(ir_data) < 50000 and np.mean(red_data) < 50000):
                            bpm = 0
                            if flag == False:
                                print("Finger not detected")
                                flag = True
                        else:
                            flag = False
                            temp = max102.read_temperature()

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
        max102.shutdown()
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
