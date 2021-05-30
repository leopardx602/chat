from flask import Flask, render_template, url_for, redirect, jsonify, request
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user  
import json
import time
import sql

users = {'chen01': {'password': '123'},
        'chen02': {'password': '456'}}  


app = Flask(__name__)
app.secret_key = 'Your Key'   # os.urandom(16).hex()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong" # defalt = "basic"
login_manager.login_view = 'login' # return to login() if not log in
login_manager.login_message = 'please log in first'

class User(UserMixin):  
    pass 

@login_manager.user_loader  
def user_loader(username):  
    if username not in users:  
        return  
    user = User()
    user.id = username  
    return user

@app.route('/')  
def login_():  
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
    return render_template('login.html')

@app.route('/index')
@login_required
def index():
    # if current_user.is_authenticated:
    return render_template('index.html')

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


if __name__ == '__main__':
    app.config['TEMPLATED_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port='3000', debug=True)
