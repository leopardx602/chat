import pymysql
import threading
import traceback

from config import db_config

lock_room = threading.Lock()

class SQL():
    def __init__(self):
        self.database = ''

    def connect(self):
        self.db = pymysql.connect(
            host = '127.0.0.1',
            port = 3306,
            user = db_config['user'],
            password = db_config['password'],
            database = self.database,
            charset = 'utf8',
            cursorclass = pymysql.cursors.DictCursor)
        self.cursor = self.db.cursor()  

    def command(self, cmd):
        try:
            print(cmd)
            self.cursor.execute(cmd) 
            self.db.commit()
            return self.cursor.fetchall()
        except:
            traceback.print_exc()
            self.db.rollback()
            return ''

    def with_command(self, cmd):
        try:
            self.connect()
            print(cmd)
            self.cursor.execute(cmd) 
            self.db.commit()
            result = self.cursor.fetchall()
            self.db.close()
            return result
        except:
            traceback.print_exc()
            self.db.rollback()
            return ''

    def drop(self, userID):
        self.with_command(f'drop table {userID}')

    def showTable(self):
        tables = []
        for data in self.with_command("show tables"):
            tables.append(data['Tables_in_users'])
        return tables

class Chat(SQL):
    def __init__(self):
        self.database = 'chat_info'

    def get_invitation(self, userID):
        sql = f"select applicantID, applicantNickName from invitation where invitedID='{userID}'"
        return self.with_command(sql)  # [{'applicantID':'chen01', 'applicantNickName':'Chen'}, {...}]
        
    def add_invitation(self, applicantID, invitedID, applicantNickName):
        sql = f"""INSERT INTO invitation(applicantID, invitedID, applicantNickName)
            VALUES ('{applicantID}', '{invitedID}', '{applicantNickName}')"""
        self.with_command(sql)

    def check_repeat_invitation(self, applicantID, invitedID):
        sql = f"select invitedID from invitation where applicantID='{applicantID}'"
        result = self.with_command(sql)
        invited_list = []
        for item in result:
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
        self.with_command(sql)
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
        self.with_command(sql)

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
        self.with_command(sql)

    def create_user_info(self):
        sql = f"""CREATE TABLE user_info (
          userID char(20) NOT NULL,
          password char(20) NOT NULL,
          nickName char(20) DEFAULT NULL,
          PRIMARY KEY (userID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        self.with_command(sql)

    def add_user(self, userID, password, nickName):
        self.create(userID)
        sql = f"""INSERT INTO user_info(userID, password, nickName)
            VALUES ('{userID}', '{password}', '{nickName}')"""
        self.with_command(sql)

    def get_userInfo(self):  # {'chen01':{'password':'123', 'nickName':''}}
        sql = f"SELECT * from user_info"
        result = self.with_command(sql)
        users = {}
        for item in result:
            users[item['userID']] = {'password':item['password'], 'nickName':item['nickName']}
        return users

    def add_friend(self, userID, friendID, roomID, nickName):
        sql = f"""INSERT INTO {userID}(friendID, roomID, nickName)
            VALUES ('{friendID}', '{roomID}', '{nickName}')"""
        self.with_command(sql)

    def get_friends(self, userID):
        sql = f"""SELECT friendID, nickName from {userID}"""
        return self.with_command(sql)  # [{'friendID':'chen01', 'nickName':'Chen'}, {...}]

    def insert(self, userID, friendID, roomID):
        sql = f"""INSERT INTO {userID}(friendID, roomID)
            VALUES ('{friendID}', '{roomID}')"""
        self.with_command(sql)

    def select(self, userID, value=''):
        if not value:
            sql = f"SELECT * from {userID}"
        else:
            sql = f"SELECT {value} from {userID}"
        result = self.with_command(sql)
        if value:
            list1 = []
            for row in result:
                list1.append(row[value])
            print(list1)
            return list1
        else:
            for row in result:
                print(row)
        return result

    def roomID(self, userID, friendID):
        sql = f"SELECT roomID from {userID} where friendID='{friendID}'"
        data = self.with_command(sql)
        return data[0]['roomID']

    def userList(self):
        sql = f"show tables"
        result = self.with_command(sql)
        data = []
        for key in result:
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
        self.with_command(sql)

    def insert(self, roomID, userID, message):
        sql = f"""INSERT INTO {roomID}(userID, message)
            VALUES ('{userID}', '{message}')"""
        self.with_command(sql)
        
    def loadMsg(self, roomID, loadMsgNumber = 10):
        sql = f"SELECT * from {roomID} ORDER BY id DESC Limit 0, {loadMsgNumber}"
        result = self.with_command(sql)
        return result[::-1]

    def history(self, roomID, ID):
        if ID <= 1:
            return
        msgNumber = 3
        msgNumber = ID - 1 if ID <= msgNumber else msgNumber
        start = ID-1-msgNumber if ID-1-msgNumber>0 else 0
        sql = f"SELECT * from {roomID} ORDER BY id Limit {start}, {msgNumber}"
        return self.with_command(sql)

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
        sql = 'show tables;'
        result = self.with_command(sql)
        rooms = []
        for key in result:
            rooms.append(key['Tables_in_rooms'])
        print('all room', rooms)

if __name__ == '__main__':
    user = Users()
    user.get_userInfo()
    room = Rooms()
    chat = Chat()
    chat.confirm_invitation('chen01', 'anny0124', 'chen01', 'chen01')
