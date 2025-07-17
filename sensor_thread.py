import minimalmodbus
import serial
import RPi.GPIO as GPIO
import time
import numpy as np
from sklearn.linear_model import LinearRegression

RELAY_PIN = 17

instrument = minimalmodbus.Instrument('/dev/serial0', 1)
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1
instrument.mode = minimalmodbus.MODE_RTU

power_buffer = []
buffer_size = 30

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

print(instrument)
GPIO.output(RELAY_PIN, GPIO.LOW)

def read_voltage():
    v_raw = instrument.read_register(0, 0, 4)
    return v_raw * 0.1
    
def read_current():
    regs = instrument.read_registers(1, 2, 4)
    raw = (regs[1] << 16) + regs[0]
    return raw * 0.001

def read_power():
    regs = instrument.read_registers(3, 2, 4)
    raw = (regs[1] << 16) + regs[0]
    return raw * 0.1

def read_energy():
    regs = instrument.read_registers(5, 2, 4)
    raw = (regs[1] << 16) + regs[0]
    return raw * 1.0

def predict_power(buffer):
    if len(buffer) < 30:
        return buffer[-1] if buffer else 0.0
    
    X = np.arange(len(buffer)).reshape(-1, 1)
    y = np.array(buffer).reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y)
    future_x = np.array([[len(buffer) + 30]])
    prediction = model.predict(future_x)[0][0]
    return float(prediction)

def sensor_loop(socketio):
    while True:
        try: 
            current = read_current()
            power = read_power()
            voltage = read_voltage()

            power_buffer.append(power)
            if len(power_buffer) > buffer_size:
                power_buffer.pop(0)

            pred_power = predict_power(power_buffer)

            values = {
                'current': round(current, 3),
                'power': round(power, 1),
                'predicted_power': round(pred_power, 1),
                'voltage': round(voltage, 1),
            }

            print(values)
            socketio.emit('sensor_data', values)
            time.sleep(1)
        except Exception as e: 
            print(e)
            time.sleep(2)