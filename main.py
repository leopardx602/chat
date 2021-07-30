from flask import Flask, render_template, url_for, redirect, jsonify, request,\
    session, request, copy_current_request_context

from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user  

from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

from flask_session import Session

import json
import time
import sql

users = {'chen01': {'password': '123'},
        'chen02': {'password': '456'}}  

user_room = {
    'ting':{
        'rooms':['room01']
    },
    'chen':{
        'rooms':['room01']
    }
}

app = Flask(__name__)
app.secret_key = 'secret!'   # os.urandom(16).hex()
app.config['SESSION_TYPE'] = 'filesystem'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong" # defalt = "basic"
login_manager.login_view = 'login' # return to login() if not log in
login_manager.login_message = 'please log in first'

Session(app)
socketio = SocketIO(app, async_mode=None, manage_session=False)


class User(UserMixin, object):
    def __init__(self, id=None):
        self.id = id

@login_manager.user_loader  
def user_loader(username):  
    if username not in users:  
        return  
    return User(username)

@app.route('/')  
def init():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('login')) 

@app.route('/login', methods=['GET', 'POST'])  
def login():  
    if request.method == 'GET':  
        return render_template('login.html')

    username = request.form['username']  
    if username in users and request.form['password'] == users[username]['password']: 
        user = User()
        user.id = username  
        login_user(user)  
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')  
def logout():  
    username = current_user.get_id()
    logout_user()
    return redirect(url_for('login')) 

@app.route('/index')
@login_required
def index():
    # if current_user.is_authenticated:
    return render_template('index.html', usrID=current_user.id)

@app.route('/loadOldMsg', methods = ['POST'])
def oldData():
    #print(current_user.id)
    data = request.get_data()
    data = json.loads(data)
    print(data)
    room = sql.Rooms()
    data = room.history(data['roomID'], int(data['startID']))
    #print(data)
    return jsonify(data), 200

@app.route('/loadNewMsg', methods= ["POST"])
def newData():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    room= sql.Rooms()
    data = room.newMsg(data['roomID'], int(data['endID']))
    print(data)
    return jsonify(data), 200

@app.route('/inputText', methods = ['POST'])
def inputText():
    print(current_user.id)
    data = request.get_data()
    data = json.loads(data)
    print(data)
    return 'OK', 200

@app.route('/friendList')
def friendList():
    print(current_user.id)
    user = sql.Users()
    #user.select(current_user.id)
    data = user.select(current_user.id, 'friendID')
    return jsonify(data), 200

@app.route('/loadRoom', methods = ['POST'])
def loadRoom():
    data = request.get_data()
    data = json.loads(data)
    friendID = data
    print(friendID)
    user = sql.Users()
    #print(current_user.id)
    roomID = user.roomID(current_user.id, friendID)
    room = sql.Rooms()
    #print(roomID)
    data = room.loadMsg(roomID)

    data = {'msg':room.loadMsg(roomID), 'roomID':roomID, 'userID':current_user.id}

    return jsonify(data), 200


#####################

@socketio.event
def my_event(message):
    print('my_event', current_user.id)
    emit('my_response',
         {'data': message['data'], 'count': 0})

@socketio.event
def join(message):
    join_room(message['room'])
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()), 'count': 0})

@socketio.event
def leave(message):
    leave_room(message['room'])

    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': 0})

@socketio.on('close_room')
def on_close_room(message):
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': 0},
         to=message['room'])
    close_room(message['room'])

@socketio.event
def my_room_event(message):
    emit('my_response',
         {'data': message['data'], 'count': 0},
         to=message['room'])

@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()
    emit('my_response',
         {'data': 'Disconnected!', 'count': 0},
         callback=can_disconnect)

@socketio.event
def connect():
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('connect')
def test_connect():
    print('Connected!', request.sid)
    user_id = session['_user_id']
    if user_id in user_room:
        room_id = user_room[user_id]['rooms'][0]
        join_room(room_id)

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)

@socketio.event
def get_session():
    #print('session', session)
    #print('get-session:', session.get('value', ''), request.sid)
    #print('user:', current_user.id if current_user.is_authenticated else 'anonymous')
    emit('refresh-session', {
        'session': session.get('value', ''),
        'user': current_user.id
            if current_user.is_authenticated else 'anonymous'
    })

@socketio.event
def set_session(data):
    if 'session' in data:
        session['value'] = data['session']
    elif 'user' in data:
        if data['user'] is not None:
            login_user(User(data['user']))
        else:
            logout_user()

if __name__ == '__main__':
    #app.config['TEMPLATED_AUTO_RELOAD'] = True
    #app.run(host='0.0.0.0', port='3000', debug=True)
    socketio.run(app)
