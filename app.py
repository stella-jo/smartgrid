from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Thread
from sensor_thread import sensor_loop

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
