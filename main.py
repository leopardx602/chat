from flask import Flask, render_template, url_for, redirect, jsonify, request
import json
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hello')
def hello():
    return 'Hello'

@app.route('/re_index')
def re_index():
    return redirect(url_for('index'))

@app.route('/oldMsg', methods = ['GET'])
def oldData():
    list1 = [1,2,3,4,time.strftime('%H:%M:%S')]
    print(list1)
    return jsonify(list1), 200

@app.route('/inputText', methods = ['POST'])
def inputText():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    return 'OK', 200

if __name__ == '__main__':
    app.config['TEMPLATED_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port='3000', debug=True)
