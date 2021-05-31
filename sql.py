import time
import pymysql
import threading
import traceback

lock = threading.Lock()


class SQL():
    def __init__(self):
        self.db = ''
        self.cursor = ''

    def connect(self):
        self.db = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='lisa1219',
            database='users',
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
        self.command('drop table {}'.format(userID))

    def showTable(self):
        tables = []
        for data in self.command("show tables"):
            tables.append(data['Tables_in_users'])
        return tables

class Users():
    def __init__(self):
        self.db = ''
        self.cursor = ''

    def connect(self):
        self.db = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='lisa1219',
            database='users',
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
        self.command('drop table {}'.format(userID))

    def showTable(self):
        tables = []
        for data in self.command("show tables"):
            tables.append(data['Tables_in_users'])
        return tables

    def create(self, userID):
        sql = """CREATE TABLE {} (
          friendID char(20) NOT NULL,
          roomID char(20) NOT NULL,
          nickName char(20) DEFAULT NULL,
          PRIMARY KEY (friendID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;""".format(userID)
        self.command(sql)

    def insert(self, userID, friendID, roomID):
        sql = """INSERT INTO {}(friendID, roomID)
            VALUES ('{}', '{}')""".format(userID, friendID, roomID)
        print(sql)
        try:
            self.connect()
            self.cursor.execute(sql)
            self.db.commit()
            self.db.close()
        except:
            traceback.print_exc()
            self.db.rollback()


    def select(self, userID, value=''):
        self.connect()
        if not value:
            sql = "SELECT * from {}".format(userID)
        else:
            sql = "SELECT {} from {}".format(value, userID)

        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        #print(results)
        if value:
            list1 = []
            for row in results:
                list1.append(row[value])
            print(list1)
            return list1
        else:
            for row in results:
                print (row)
        self.db.close()

    def roomID(self, userID, friendID):
        self.connect()
        sql = "SELECT roomID from {} where friendID='{}'".format(userID, friendID)
        print(sql)
        self.cursor.execute(sql)
        results = self.cursor.fetchone()
        return results['roomID']



class Rooms():
    def __init__(self):
        self.db = ''
        self.cursor = ''

    def connect(self):
        self.db = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='lisa1219',
            database='rooms',
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
        self.command('drop table {}'.format(userID))

    def showTable(self):
        return self.command("show tables")

    def create(self, userID):
        sql = """CREATE TABLE {} (
          id int(10) NOT NULL AUTO_INCREMENT,
          userID char(20) NOT NULL,
          time char(20) NOT NULL,
          message text DEFAULT NULL,
          PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;""".format(userID)
        self.command(sql)

    def insert(self, roomID, userID, time, message):
        sql = """INSERT INTO {}(userID, time, message)
            VALUES ('{}', '{}', '{}')""".format(roomID, userID, time, message)
        self.command(sql)
        
    def loadMsg(self, roomID, loadMsgNumber = 5):
        self.connect()
        #sql = "SELECT * from {}".format(roomID)
        sql = "SELECT * from {} ORDER BY id DESC Limit 0, {}".format(roomID, loadMsgNumber)
        print(sql)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        results = results[::-1]
        #print(results)
        for row in results:
            print(row)
        self.db.close()
        return results

    def history(self, roomID, ID):
        if ID <= 1:
            return

        self.connect()
        msgNumber = 3
        msgNumber = ID - 1 if ID <= msgNumber else msgNumber

        start = ID-1-msgNumber if ID-1-msgNumber>0 else 0
        sql = "SELECT * from {} ORDER BY id Limit {}, {}".format(roomID, start, msgNumber)
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
        sql = "SELECT * from {} ORDER BY id DESC Limit 0, 1".format(roomID)
        self.cursor.execute(sql)
        results = self.cursor.fetchone()
        endID = results['id']
        if endID == ID: 
            self.db.close()
            return ''
        
        loadMsgNumber = endID - ID
        sql = "SELECT * from {} ORDER BY id Limit {}, {}".format(roomID, ID, loadMsgNumber)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        print(results)
        self.db.close()
        return results

class Invitation():
    def __init__(self):
        self.db = ''
        self.cursor = ''

    def connect(self):
        self.db = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='lisa1219',
            database='invitation',
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

    def create(self, userID):
        sql = """CREATE TABLE {} (
          friendID char(20) NOT NULL,
          PRIMARY KEY (friendID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;""".format(userID)
        self.command(sql)

    def drop(self, userID):
        self.command('drop table {}'.format(userID))


room = Rooms()
#data = room.showTable()
#print(data)

invi = Invitation()
#invi.drop('chen01')
#invi.drop('chen02')
#invi.create('chen01')
#invi.create('chen02')


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
        print('{} repeated'.format(userID))
    lock.release()


def addFriend(userID, otherID):
    user = Users()
    users = user.showTable()
    if otherID in users:
        pass
    print(data)

#addFriend(1, 2)



tmp = time.time()
tmp2 = time.localtime(tmp)
tmp3 = time.strftime("%y%m%d%H%M%S", tmp2)
        
#user = Users()
#user.command('ALTER TABLE chen01 ADD nickName VARCHAR(20);')

room = Rooms()
#room.create('room02')
#room.drop('room02')
#room.select('room01')



def update():
    # Prepare SQL query to UPDATE required records
    sql = "UPDATE employee SET AGE = AGE + 1 \
                            WHERE SEX = '%c'" % ('M')
    try:
        cursor.execute(sql)
        db.commit()
    except:
        traceback.print_exc()
        db.rollback()

def delete():
    sql = "DELETE FROM EMPLOYEE WHERE AGE > '%d'" % (40)
    try:
       cursor.execute(sql)
       db.commit()
    except:
       db.rollback()

#db.close()