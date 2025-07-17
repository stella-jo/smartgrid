import minimalmodbus
import serial
import time
from relay import set_relay
import threading

auto_mode = True
relay_state = True
lock = threading.Lock()

def set_auto_mode(mode):
    global auto_mode
    with lock:
        auto_mode = mode

def get_auto_mode():
    with lock:
        return auto_mode

instrument = minimalmodbus.Instrument('/dev/serial0', 1)
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1
instrument.mode = minimalmodbus.MODE_RTU

print(instrument)

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

def sensor_loop(socketio):
    global relay_state

    while True:
        try: 
            current = read_current()
            power = read_power()
            voltage = read_voltage()

            values = {
                'current': round(current, 3),
                'power': round(power, 1),
                'voltage': round(voltage, 1),
            }

            if get_auto_mode():
                if current > 0.2 and relay_state:
                    print("off")
                    relay_state = False
                    set_relay(False)
                    socketio.emit('relay_status', False)
                elif current < 0.1 and not relay_state:
                    print("on")
                    relay_state = True
                    set_relay(True)
                    socketio.emit('relay_status', True)

            print(values)
            socketio.emit('sensor_data', values)
            time.sleep(1)
        except Exception as e: 
            print(e)
            time.sleep(2)