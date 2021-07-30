import time
import pymysql
import threading
import traceback

from config import db_config

lock = threading.Lock()

class SQL():
    def __init__(self):
        #self.db = ''
        #self.cursor = ''
        self.database = ''

    def connect(self):
        self.db = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user=db_config['user'],
            password=db_config['password'],
            database=self.database,
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.db.cursor()  

    def command(self, cmd):
        try:
            self.connect()
            print(cmd)
            self.cursor.execute(cmd) 
            self.db.commit()
            self.db.close()
            return self.cursor.fetchall()
        except:
            traceback.print_exc()
            self.db.rollback()
            return ''

    def drop(self, userID):
        self.command(f'drop table {userID}')

    def showTable(self):
        tables = []
        for data in self.command("show tables"):
            tables.append(data['Tables_in_users'])
        return tables

class Users(SQL):
    def __init__(self):
        self.database = 'users'

    def create(self, userID):
        sql = f"""CREATE TABLE {userID} (
          friendID char(20) NOT NULL,
          roomID char(20) NOT NULL,
          nickName char(20) DEFAULT NULL,
          PRIMARY KEY (friendID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        self.command(sql)

    def insert(self, userID, friendID, roomID):
        sql = f"""INSERT INTO {userID}(friendID, roomID)
            VALUES ('{friendID}', '{roomID}')"""
        self.command(sql)

    def select(self, userID, value=''):
        self.connect()
        if not value:
            sql = f"SELECT * from {userID}"
        else:
            sql = f"SELECT {value} from {userID}"

        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        self.db.close()
        #print(results)
        if value:
            list1 = []
            for row in results:
                list1.append(row[value])
            print(list1)
            return list1
        else:
            for row in results:
                print(row)
        return results

    def roomID(self, userID, friendID):
        self.connect()
        sql = f"SELECT roomID from {userID} where friendID='{friendID}'"
        data = self.command(sql)
        #print(data)
        return data[0]['roomID']

class Rooms(SQL):
    def __init__(self):
        self.database = 'rooms'

    def create(self, userID):
        sql = f"""CREATE TABLE {userID} (
          id int(10) NOT NULL AUTO_INCREMENT,
          userID char(20) NOT NULL,
          message text DEFAULT NULL,
          time TIMESTAMP NOT NULL,
          PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        self.command(sql)

    def insert(self, roomID, userID, message):
        sql = f"""INSERT INTO {roomID}(userID, message)
            VALUES ('{userID}', '{message}')"""
        self.command(sql)
        
    def loadMsg(self, roomID, loadMsgNumber = 5):
        self.connect()
        #sql = "SELECT * from {}".format(roomID)
        sql = f"SELECT * from {roomID} ORDER BY id DESC Limit 0, {loadMsgNumber}"
        print(sql)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        #print(results[::-1])
        self.db.close()
        return results[::-1]

    def history(self, roomID, ID):
        if ID <= 1:
            return

        self.connect()
        msgNumber = 3
        msgNumber = ID - 1 if ID <= msgNumber else msgNumber

        start = ID-1-msgNumber if ID-1-msgNumber>0 else 0
        sql = f"SELECT * from {roomID} ORDER BY id Limit {start}, {msgNumber}"
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            #print(results)
            for row in results:
                print(row)
        except:
            traceback.print_exc()
        self.db.close()
        return results

    def newMsg(self, roomID, ID):
        #ID = ID-3
        self.connect()
        sql = f"SELECT * from {roomID} ORDER BY id DESC Limit 0, 1"
        self.cursor.execute(sql)
        results = self.cursor.fetchone()
        endID = results['id']
        if endID == ID: 
            self.db.close()
            return ''
        
        loadMsgNumber = endID - ID
        sql = f"SELECT * from {roomID} ORDER BY id Limit {ID}, {loadMsgNumber}"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        print(results)
        self.db.close()
        return results

class Invitation(SQL):
    def __init__(self):
        self.database = 'invitation'
        
    def create(self, userID):
        sql = """CREATE TABLE {} (
          friendID char(20) NOT NULL,
          PRIMARY KEY (friendID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;""".format(userID)
        self.command(sql)

def signUp(userID):
    lock.acquire()
    user = Users()
    invi = Invitation()
    users = []
    for data in user.command('show tables'):
        users.append(data['Tables_in_users'])
    if userID not in users:
        user.create(userID)
        invi.create(userID)
    else:
        print(f'{userID} repeated')
    lock.release()

def addFriend(userID, otherID):
    user = Users()
    users = user.showTable()
    if otherID in users:
        pass
    print(data)

if __name__ == '__main__':

    user = Users()
    #user.create('chen01')
    #user.create('chen02')
    #user.create('anny')
    
    #user.insert('chen01', 'chen02', 'room01')
    #user.insert('chen02', 'chen01', 'room01')
    #user.insert('chen01', 'anny', 'room02')
    #user.insert('anny', 'chen01', 'room02')

    #user.select('chen01')


    #room = Rooms()
    #data = room.showTable()
    #print(data)

    #invi = Invitation()
    #invi.drop('chen01')
    #invi.drop('chen02')
    #invi.create('chen01')
    #invi.create('chen02')

    #addFriend(1, 2)

    #user = Users()
    #user.command('ALTER TABLE chen01 ADD nickName VARCHAR(20);')

    room = Rooms()
    #room.create('room01')
    #room.create('room02')
    #room.insert('room01', 'chen01', 'Hello, I am chen01.')
    #room.insert('room01', 'chen02', 'Hello, I am chen02.')
    #room.insert('room02', 'chen01', 'Hello, I am chen01.')
    #room.insert('room02', 'anny', 'Hello, I am anny.')

    #room.insert('room01', 'chen02', 'How do you do?')
    #room.insert('room01', 'chen01', 'Not bad, how about you?')
    #room.insert('room01', 'chen02', 'Me too')
    #room.insert('room01', 'chen02', 'I am software engineer.')
    #room.insert('room01', 'chen02', 'And goot at python')
    #room.insert('room01', 'chen02', 'what do you do')
    #room.insert('room01', 'chen01', 'I am student now in Chiao Tung Unervisity.')

    
    #room.drop('room01')
    #room.select('room01')


    #db.close()
