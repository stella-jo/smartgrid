from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Thread
from sensor_thread import sensor_loop
import RPi.GPIO as GPIO

RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW) 


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

# 백그라운드에서 센서 루프 실행
def start_sensor():
    sensor_loop(socketio)

if __name__ == '__main__':
    thread = Thread(target=start_sensor)
    thread.daemon = True
    thread.start()
    
    socketio.run(app, host='0.0.0.0', port=5000)

relay_state = False 

@socketio.on('toggle_relay')
def handle_toggle_relay():
    global relay_state
    relay_state = not relay_state

    GPIO.output(RELAY_PIN, GPIO.HIGH if relay_state else GPIO.LOW)

    print(f"릴레이 상태 변경됨: {'ON' if relay_state else 'OFF'}")
    
    socketio.emit('relay_status', relay_state)

@socketio.on('connect')
def send_initial_status():
    socketio.emit('relay_status', relay_state)
