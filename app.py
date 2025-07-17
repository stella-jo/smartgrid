from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Thread
from sensor_thread import sensor_loop, set_auto_mode
from relay import set_relay, get_relay_state

relay_state = False 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('toggle_relay')
def handle_toggle_relay():
    global relay_state
    relay_state = not relay_state
    set_relay(relay_state)
    socketio.emit('relay_status', relay_state)

@socketio.on('set_auto_mode')
def handle_auto_mode(mode):
    set_auto_mode(mode)
    print(f"[mode changed] auto mode: {'on' if mode else 'off'}")
    socketio.emit('auto_mode_status', mode)

@socketio.on('connect')
def send_initial_status():
    socketio.emit('relay_status', get_relay_state())
    socketio.emit('auto_mode_status', True)

def start_sensor():
    sensor_loop(socketio)

if __name__ == '__main__':
    thread = Thread(target=start_sensor)
    thread.daemon = True
    thread.start()
    
    socketio.run(app, host='0.0.0.0', port=5000)
