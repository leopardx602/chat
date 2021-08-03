import time
import pymysql
import threading
import traceback

from config import db_config

lock_room = threading.Lock()

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

class Chat(SQL):
    def __init__(self):
        self.database = 'chat_info'

    def get_invitation(self, userID):
        self.connect()
        sql = f"select applicantID, applicantNickName from invitation where invitedID='{userID}'"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        self.db.close()
        print('get_invitation', results)
        return results  # [{'applicantID':'chen01', 'applicantNickName':'Chen'}, {...}]
        
    def add_invitation(self, applicantID, invitedID, applicantNickName):
        sql = f"""INSERT INTO invitation(applicantID, invitedID, applicantNickName)
            VALUES ('{applicantID}', '{invitedID}', '{applicantNickName}')"""
        self.command(sql)

    def check_repeat_invitation(self, applicantID, invitedID):
        self.connect()
        sql = f"select invitedID from invitation where applicantID='{applicantID}'"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        self.db.close()
        #print('check_repeat_invitation', results)
        invited_list = []
        for item in results:
            invited_list.append(item['invitedID'])

        if invitedID in invited_list: return True
        return False

    def confirm_invitation(self, userID, friendID, userNickName, friendNickName): 
        # build roomID from history
        lock_room.acquire()
        self.connect()
        sql = f"select * from room_info"
        self.cursor.execute(sql)
        results = self.cursor.fetchone()  # {'roomID':0, 'delete_room':0}
        self.db.close()
        roomID = 'room{}'.format(results['roomID']+1)
        sql = f"UPDATE room_info SET roomID='{results['roomID']+1}' WHERE roomID='{results['roomID']}'"
        self.command(sql)
        lock_room.release()

        # build room
        room = Rooms()
        room.create(roomID)
        
        # add friend and roomID
        user = Users()
        user.add_friend(userID, friendID, roomID, friendNickName)
        user.add_friend(friendID, userID, roomID, userNickName)

        # delete invitation 
        self.delete_invitation(friendID, userID)
        

    def delete_invitation(self, applicantID, invitedID):
        sql = f"DELETE FROM invitation WHERE applicantID='{applicantID}' AND invitedID='{invitedID}';"
        self.command(sql)

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

    def create_user_info(self):
        sql = f"""CREATE TABLE user_info (
          userID char(20) NOT NULL,
          password char(20) NOT NULL,
          nickName char(20) DEFAULT NULL,
          PRIMARY KEY (userID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        self.command(sql)

    def add_user(self, userID, password, nickName):
        self.create(userID)
        sql = f"""INSERT INTO user_info(userID, password, nickName)
            VALUES ('{userID}', '{password}', '{nickName}')"""
        self.command(sql)

    def get_userInfo(self):  # {'chen01':{'password':'123', 'nickName':''}}
        self.connect()
        sql = f"SELECT * from user_info"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        self.db.close()
        users = {}
        for item in results:
            users[item['userID']] = {'password':item['password'], 'nickName':item['nickName']}
        return users

    def add_friend(self, userID, friendID, roomID, nickName):
        sql = f"""INSERT INTO {userID}(friendID, roomID, nickName)
            VALUES ('{friendID}', '{roomID}', '{nickName}')"""
        self.command(sql)

    def get_friends(self, userID):
        self.connect()
        sql = f"""SELECT friendID, nickName from {userID}"""
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        self.db.close()
        print('get_friend', results)
        return results  # [{'friendID':'chen01', 'nickName':'Chen'}, {...}]

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

    def userList(self):
        self.connect()
        sql = f"show tables"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        self.db.close()
        data = []
        for key in results:
            data.append(key['Tables_in_users'])
        return data

class Rooms(SQL):
    def __init__(self):
        self.database = 'rooms'

    def create(self, roomID):
        sql = f"""CREATE TABLE {roomID} (
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

    def all_room(self):
        self.connect()
        sql = 'show tables;'
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        self.db.close()
        rooms = []
        for key in results:
            rooms.append(key['Tables_in_rooms'])
        print('all room', rooms)


class Invitation(SQL):
    def __init__(self):
        self.database = 'invitation'
        
    def create(self, userID):
        sql = """CREATE TABLE {} (
          friendID char(20) NOT NULL,
          PRIMARY KEY (friendID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;""".format(userID)
        self.command(sql)

if __name__ == '__main__':

    user = Users()
    user.get_userInfo()
    #user.add_user('chen01', '123')
    #user.add_user('chen02', '123')
    #user.add_user('anny', '123')
    #user.add_user('dating', '123')

    #user.create2()
    #user.userList()
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

    #user = Users()
    #user.command('ALTER TABLE chen01 ADD nickName VARCHAR(20);')

    room = Rooms()
    #room.all_room()
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

    chat = Chat()
    chat.confirm_invitation('chen01', 'anny0124', 'chen01', 'chen01')
    #chat.delete_invitation('chen01', 'anny0124')


    #db.close()
