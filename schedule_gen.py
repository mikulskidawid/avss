import media_lib, server_func, json, random, sqlite3
from datetime import datetime, timedelta, date

def createScheduleDB():
    connection = sqlite3.connect('data/schedule.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            video_time TEXT,
            video_date TEXT
        )
    ''')

    connection.commit()
    connection.close()
    print('db created')

def appendSchedule(video_id, video_time, video_date):
    connection = sqlite3.connect('data/schedule.db')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO schedule(video_id, video_time, video_date)
        VALUES(?, ?, ?)
    ''', (video_id, media_lib.secondsToTime(video_time), video_date.strftime('%d-%m-%Y')))

    connection.commit()
    connection.close()

def getSchedule():
    connection = sqlite3.connect('data/schedule.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM schedule')
    ret = cursor.fetchall()
    connection.commit()
    connection.close()
    return ret

def getTodaySchedule():
    connection = sqlite3.connect('data/schedule.db')
    cursor = connection.cursor()
    query = 'SELECT * FROM schedule where video_date="'+datetime.now().strftime('%d-%m-%Y')+'"'
    cursor.execute(query)
    ret = cursor.fetchall()
    connection.commit()
    connection.close()
    return ret

def scheduleInfo():
    schedule = filterSchedule()
    info = []
    for s in schedule:
        video = media_lib.getVideo(s[1])
        info.append([video[0][1], s[2], s[3]])
    return info

def todayScheduleInfo():
    schedule = getTodaySchedule()
    info = []
    for s in schedule:
        video = media_lib.getVideo(s[1])
        group = media_lib.getGroup(video[0][4])

        date = datetime.strptime(s[3], '%d-%m-%Y').strftime('%d-%m-%Y')
        time = s[2]

        data = {
            'group_name': group[0][1],
            'group_type': group[0][4],
            'video_name': video[0][2],
            'video_season': video[0][5],
            'video_episode': video[0][6],
            'video_time': time,
            'video_date': date
        }
        info.append(data)
    return info

def filterSchedule():
    schedule = getSchedule()
    newSchedule = []
    i=0
    canAdd = 0
    schLen = len(schedule)
    for item in schedule:
        timeNow = datetime.now().second + datetime.now().minute*60+datetime.now().hour*60

        if i!=schLen-1:
            itemDate = datetime.strptime(schedule[i+1][3], '%d-%m-%Y')
            itemTime = media_lib.getSeconds(schedule[i+1][2])

            hours, minutes = divmod(int(itemTime/60), 60)
            seconds = int(itemTime%60)
            itemDate = itemDate +timedelta(hours=hours, minutes=minutes, seconds=seconds)
            if itemDate >= datetime.now():
                newSchedule.append(item)
        i+=1

    return newSchedule

def getOffset():
    item = filterSchedule()[1]
    video = media_lib.getVideo(item[1])[0]
    videoTime = media_lib.getSeconds(video[7])
    currentTime = datetime.now().time()
    currentTime = (currentTime.hour * 3600) + (currentTime.minute * 60) + currentTime.second
    itemTime = media_lib.getSeconds(item[2])
    calcOffset = abs(itemTime-currentTime)
    return calcOffset
    

def currentItemID():
    schedule = getTodaySchedule()
    newSchedule = []
    i=0
    canAdd = 0
    schLen = len(schedule)
    for item in schedule:
        timeNow = datetime.now().second + datetime.now().minute*60+datetime.now().hour*60

        if i!=schLen-1:
            itemDate = datetime.strptime(schedule[i+1][3], '%d-%m-%Y')
            itemTime = media_lib.getSeconds(schedule[i+1][2])

            hours, minutes = divmod(int(itemTime/60), 60)
            seconds = int(itemTime%60)
            itemDate = itemDate +timedelta(hours=hours, minutes=minutes, seconds=seconds)
            if itemDate >= datetime.now():
                return i
        i+=1

    return -1

def resetIdCounter():
    connection = sqlite3.connect('data/schedule.db')
    cursor = connection.cursor()
    query = "DELETE FROM sqlite_sequence WHERE name='schedule';"
    cursor.execute(query)

    connection.commit()
    connection.close()

def clearSchedule():
    connection = sqlite3.connect('data/schedule.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM schedule')

    connection.commit()
    connection.close()
    resetIdCounter()
    print('schedule cleared')

def createSchedule(days=30):
    clearSchedule()
    scheduleTemplate = media_lib.getSchedule()
    scheduleConfig = server_func.getScheduleConfig()
    interruptVideo = media_lib.getVideo(id=scheduleConfig[1])
    adVideos = media_lib.getVideos(group=scheduleConfig[0])

    for ad in adVideos[:]:
        if int(ad[0])==int(interruptVideo[0][0]):
            adVideos.remove(ad)
    random.shuffle(adVideos)
    interruptVideo = interruptVideo[0]

    print('lets go 1')

    startTime = 0
    startDate = datetime.now() - timedelta(days=datetime.weekday(datetime.now()))
    endDate = startDate+timedelta(days=days)
    day = 0
    scheduleLength = len(scheduleTemplate)
    adNumber = len(adVideos)

    # group counters
    groupData = []
    serie_list = media_lib.getSeries()
    group_list = media_lib.getNotSeries()
    allGroups = serie_list+group_list
    for group in allGroups:
        groupVideos = media_lib.getVideos(group[0])
        data = {'ID':group[0],'counter':0, 'groupLength':len(groupVideos)}
        groupData.append(data)

    print('lets go 2')

    def GetNextVideo(item, grData):
        video = 0
        videos = media_lib.getVideos(group=item['itemID'])
        itemData = 0
        index=0

        for i in range(len(grData)):
            if int(grData[i]['ID'])==int(item['itemID']):
                itemData = grData[i]
                index = i

                if int(item['itemMode'])==2: 
                    random.shuffle(videos)
                video = videos[itemData['counter']]

                grData[i]['counter']+=1
                if grData[i]['counter']>=grData[i]['groupLength']: 
                    grData[i]['counter']=0

        print(item['itemMode'], index, grData)

        return [video, grData]

    while startDate < endDate:
        print('lets go 3', scheduleLength)
        for i in range(scheduleLength):
            group = scheduleTemplate[i]
            nextVideo = GetNextVideo(group, groupData)
            video = nextVideo[0]
            groupData = nextVideo[1]
            print('elo')
            itemStart = media_lib.getSeconds(group['itemTime'])
            itemTime = media_lib.getSeconds(video[7])

            if startTime < itemStart-70:
                end = itemStart-70
                random.shuffle(adVideos)
                y=0

                appendSchedule(interruptVideo[0], startTime, startDate)
                startTime = startTime+media_lib.getSeconds(interruptVideo[7])
                if startTime>24*60*60: 
                    startTime-=24*60*60
                    startDate += timedelta(days=1)
                    if startDate >= endDate: 
                        break

                if end-startTime > media_lib.getSeconds(interruptVideo[7]):
                    while(startTime<end):

                        ad = adVideos[y]
                        appendSchedule(ad[0], startTime, startDate)
                        startTime = startTime+media_lib.getSeconds(ad[7])
                        if startTime>24*60*60: 
                            startTime-=24*60*60
                            startDate += timedelta(days=1)
                            if startDate >= endDate: 
                                break
                        if y>=adNumber-1: 
                            y=0
                            random.shuffle(adVideos)
                        y+=1

                    appendSchedule(interruptVideo[0], startTime, startDate)
                    startTime = startTime+media_lib.getSeconds(interruptVideo[7])
                    if startTime>24*60*60: 
                        startTime-=24*60*60
                        startDate += timedelta(days=1)
                        if startDate >= endDate: 
                            break

                else:
                    while(startTime<end):

                        ad = adVideos[y]
                        appendSchedule(ad[0], startTime, startDate)
                        startTime = startTime+media_lib.getSeconds(ad[7])
                        if startTime>24*60*60: 
                            startTime-=24*60*60
                            startDate += timedelta(days=1)
                            if startDate >= endDate: 
                                break
                        if y>=adNumber-1: 
                            y=0
                            random.shuffle(adVideos)
                        y+=1


            appendSchedule(video[0], startTime, startDate)
            startTime+=itemTime
            if startTime>24*60*60: 
                startTime-=24*60*60
                startDate += timedelta(days=1)
                if startDate >= endDate: 
                    break
