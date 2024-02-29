import sqlite3
from datetime import datetime, timedelta

def getSeconds(video_length):
    # Przekształć czas w formacie mm:ss na liczbę sekund
    time = datetime.strptime(video_length, "%H:%M:%S")
    return time.hour*60*60 + time.minute * 60 + int(time.second)

def secondsToTime(seconds):
    hours, minutes = divmod(int(seconds/60), 60)
    if minutes < 10: minutes = '0'+str(minutes)
    else: minutes = str(minutes)
    sec = int(seconds%60)
    if sec < 10: sec = '0'+str(int(seconds%60))
    else: sec = str(int(seconds%60))
    time_string = str(hours)+':'+str(minutes)+':'+sec
    return time_string

def createDB():
    connection = sqlite3.connect('data/media_library.db')
    cursor = connection.cursor()

    # creates table "videos"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            videoname TEXT,
            uploadDate TEXT,
            groupID INTEGER,
            season INTEGER,
            episode INTEGER,
            video_length TEXT,
            age_cat INTEGER
        )
    ''')

    # creates table "groups"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            groupName TEXT,
            createDate TEXT,
            description TEXT,
            groupType INTEGER,
            sortOrder INTEGER
        )
    ''')

    # creates table "schedule"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day INTEGER,
            itemType INTEGER,
            itemID INTEGER,
            itemMode INTEGER,
            itemTime TEXT
        )
    ''')

    connection.commit()
    connection.close()


# executes SQL query on db
def sqlQuery(query, ret=0, param=0):
    connection = sqlite3.connect('data/media_library.db')
    cursor = connection.cursor()
    if param==1: cursor.execute(query[0], query[1])
    else: cursor.execute(query)
    values = 0
    if ret==1: values = cursor.fetchall()
    connection.commit()
    connection.close()
    return values

def addVideo(filename, videoName, date, groupID, video_length):
    sqlQuery(['''
        INSERT INTO videos (filename, videoname, uploadDate, groupID, season, episode, video_length)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (filename, videoName, date, groupID, 0, 0, video_length)], param=1)

def addGroup(groupname, date, description, groupType, sort_order):
    sqlQuery(['''
        INSERT INTO groups (groupName, createDate, description, groupType, sortOrder)
        VALUES (?, ?, ?, ?, ?)
    ''', (groupname, date, description, groupType, sort_order)], param=1)


def getVideos(group='all'):
    if group=='all': videos = sqlQuery('SELECT * FROM videos', 1)
    else: videos = sqlQuery('SELECT * FROM videos where groupID='+str(group), 1)

    return videos

def getVideosSorted(group, groupType, sort_order):
    sql = ''
    sort_order=int(sort_order)
    groupType=int(groupType)
    if sort_order==0: 
        if groupType!=1: 
            sql = 'SELECT * FROM videos where groupID='+str(group)+' order by videoname ASC;'
        else: 
            sql = 'SELECT * FROM videos where groupID='+str(group)+' order by season ASC, episode ASC, videoname ASC;'

    elif sort_order==1: 
        if groupType!=1:
            sql = 'SELECT * FROM videos where groupID='+str(group)+' order by videoname DESC;'
        else: 
            sql = 'SELECT * FROM videos where groupID='+str(group)+' order by season DESC, episode DESC, videoname DESC;'

    videos = sqlQuery(sql, 1)
    return videos

def filterEmptyGroups(groups):
    for group in groups[:]:
        videos = getVideos(group[0])
        if videos == '' or videos == 0 or videos==[]:
            groups.remove(group)
    return groups

def getGroups(type=-1, filter_empty=0):
    addition = ''
    if type!=-1: addition = ' where groupType='+str(type)
    groups = sqlQuery('SELECT * FROM groups'+addition, 1)
    if filter_empty==1: groups = filterEmptyGroups(groups)
    return groups

def getSeries():
    return getGroups(1)
def getNotSeries():
    return getGroups(0)
def getAds():
    return getGroups(2)

def getMaxTime(groupID):
    videos = getVideos(groupID)
    seconds = [getSeconds(time[7]) for time in videos]
    MaxSeconds = max(seconds)
    MaxTime = secondsToTime(MaxSeconds)
    return MaxTime

def getMaxTimes():
    series = getGroups(type=1, filter_empty=1)
    movies = getGroups(type=0, filter_empty=1)
    groups = series+movies
    group_times = []
    for group in groups:
        group_times.append(getMaxTime(group[0]))
    return group_times

def getSchedule():
    result = sqlQuery('SELECT * FROM schedule', 1)
    newArray = []
    for item in result:
        group = getGroup(item[3])[0]
        newArray.append({'itemDay':item[1],'itemType':item[2],'itemID':item[3],'itemMode':item[4],'itemTime':item[5], 'itemName':group[1], 'itemLength':getMaxTime(item[3])})
    return newArray

def getVideo(id):
    return sqlQuery('SELECT * FROM videos where id='+str(id), 1)

def getGroup(id):
    return sqlQuery('SELECT * FROM groups where id='+str(id), 1)

def updateVideo(video_id, videoname, group_id, season, episode):
    sqlQuery(['''
        UPDATE videos
        SET videoname=?, groupID=?, season=?, episode=?
        WHERE id=?
    ''', (videoname, group_id, season, episode, video_id)], param=1)

def updateGroup(group_id, groupname, description, groupType, sort_order):
    sqlQuery(['''
        UPDATE groups
        SET groupname=?, description=?, groupType=?, sortOrder=?
        WHERE id=?
    ''', (groupname, description, groupType, sort_order, group_id)], param=1)

def deleteVideo(video_id):
    sqlQuery('DELETE FROM videos WHERE id='+str(video_id))


def deleteAllVideos():
    sqlQuery('DELETE FROM videos')


def deleteGroup(group_id):
    sqlQuery('DELETE FROM groups WHERE id='+str(group_id))

def deleteAllGroups():
    sqlQuery('DELETE FROM groups')

'''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day INTEGER,
            itemType INTEGER,
            itemID INTEGER,
            itemMode INTEGER,
            itemTime TEXT
        )
'''

def saveScheduleTemplate(fullSchedule):
    for item in fullSchedule:
        print(item)
        sqlQuery(['''
        INSERT INTO schedule (day, itemType, itemID, itemMode, itemTime)
        VALUES (?, ?, ?, ?, ?)
        ''', (int(item['itemDay']), int(item['itemType']), int(item['itemID']), int(item['itemMode']), item['itemTime'])], param=1)

def clearScheduleTemplate():
    sqlQuery('DELETE FROM schedule')

