from flask import Flask, render_template, url_for, redirect, jsonify, request,\
    session, request, copy_current_request_context
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user  
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask_session import Session

import json
import time
import threading

import sql

users = sql.Users().get_userInfo()  # {'chen01':{'password':'123', 'nickName':''}}

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

lock_signUp = threading.Lock()

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
    logout_user()
    return redirect(url_for('login'))

@app.route('/signup', methods = ["POST"])  # {'userID':'chen01', 'password':'123'}
def singup():
    global users
    data = json.loads(request.get_data())
    print('signup', data)

    # lock start
    lock_signUp.acquire()
    if data['userID'] in users:
        return 'repeat', 200
    user = sql.Users()
    user.add_user(data['userID'], data['password'], data['nickName'])
    users = user.get_userInfo()  # update users
    lock_signUp.release()
    return 'ok', 200

@app.route('/index')
@login_required
def index():
    # if current_user.is_authenticated:
    return render_template('index.html', usrID=current_user.id, nickName=users[current_user.id]['nickName'])

'''
@socketio.event
def connect():
    print('connected1!')
    #emit('my_response', {'data': 'Connected', 'count': 0})
'''
@socketio.on('connect')
def user_connect():
    print('Connected!', current_user.id, request.sid)
    # join room
    user = sql.Users()
    rooms = user.select(current_user.id, 'roomID')  # ['room01', 'room02']
    for roomID in rooms:
        join_room(roomID)

    # update client user infomation
    emit('userInfo', {'userID':current_user.id, 'nickName':users[current_user.id]['nickName']})

    # show invitation
    chat = sql.Chat()
    invitations = chat.get_invitation(current_user.id)  # ['chen01', 'chen02']
    emit('show_invitation', invitations)

    # show friends
    user = sql.Users()
    data = user.get_friends(current_user.id)  # [{'friendID':'chen01', 'nickName':'Chen'}, {...}]
    print('get_friendID_list', data)
    emit('show_friendID_list', data)

@socketio.on('disconnect')
def user_disconnect():
    print('Client disconnected', request.sid)
    #leave_room(message['room'])
    #close_room(message['room'])

@socketio.event
def get_room_message(data):  # 'chen01'
    friendID = data
    user = sql.Users()
    roomID = user.roomID(current_user.id, friendID)
    room = sql.Rooms()
    data = room.loadMsg(roomID)
    for num, item in enumerate(data):
        data[num]['time'] = str(item['time'])
    print('show_room_message', data)
    emit('show_room_message', data)

@socketio.event
def get_old_message(data):
    user = sql.Users()
    roomID = user.roomID(current_user.id, data['friendID'])
    room = sql.Rooms()
    data = room.history(roomID, int(data['startID']))
    for num, item in enumerate(data):
        data[num]['time'] = str(item['time'])

    print('get_old_message', data) 
    emit('show_old_message', data)

@socketio.event
def send_new_message(data):  # {'friendID:'chen02', 'message':'hello'}
    print(data)
    # store in database
    user = sql.Users()
    roomID = user.roomID(current_user.id, data['friendID'])
    room = sql.Rooms()
    room.insert(roomID, current_user.id, data['message'])

    # send to the room
    data = {'sendID':current_user.id, 'recvID':data['friendID'], 'message':data['message'], 'time':time.strftime('%X')}
    emit('show_new_message', data, to = roomID)

@socketio.event
def add_invitation(invitedID):  # 'chen02'
    if invitedID not in users:
        emit('client_event', {'event':'invite_message', 'data':'No this ID'})
        return

    user = sql.Users()
    friend_list = user.select(current_user.id, 'friendID')
    if invitedID in friend_list:
        emit('client_event', {'event':'invite_message', 'data':'Already friend'})
        return

    chat = sql.Chat()
    repeat = chat.check_repeat_invitation(current_user.id, invitedID)
    if repeat:
        emit('client_event', {'event':'invite_message', 'data':'Already invited, waiting for reply!'})
        print('Already invited')
        return

    chat.add_invitation(current_user.id, invitedID, users[current_user.id]['nickName'])
    emit('client_event', {'event':'invite_message', 'data':'OK!'})

@socketio.event
def reply_invitation(data):  # {'applicantID':'chen01', 'reply':True}
    print('reply_invitation', data)

    chat = sql.Chat()
    if data['reply']:
        chat.confirm_invitation(current_user.id, data['applicantID'], users[current_user.id]['nickName'], users[data['applicantID']]['nickName'])
        emit('client_event', {'event':'invite_message', 'data':'accept {}'.format(data['applicantID'])})
    else:
        chat.delete_invitation(data['applicantID'], current_user.id)
        emit('client_event', {'event':'invite_message', 'data':'reject {}'.format(data['applicantID'])})
    
    # update user invitation list
    invitations = chat.get_invitation(current_user.id)  # ['chen01', 'chen02']
    emit('show_invitation', invitations)


@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()
    emit('my_response',
         {'data': 'Disconnected!', 'count': 0},
         callback=can_disconnect)

if __name__ == '__main__':
    #app.config['TEMPLATED_AUTO_RELOAD'] = True
    #app.run(host='0.0.0.0', port='3000', debug=True)
    socketio.run(app, host='0.0.0.0', port=3000)
