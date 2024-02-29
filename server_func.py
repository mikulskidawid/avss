import os, media_lib, datetime, subprocess, psutil, platform, shutil, json, configparser, control
from os import listdir

def getVideoTime(file):
    data = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    print(data.stdout)
    seconds = float(data.stdout)
    video_time = datetime.timedelta(seconds=seconds)
    minutes, seconds = divmod(video_time.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    video_time = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)
    return video_time


def clearStream():
    folderPath = 'static/stream/'
    if os.path.isfile('static/stream/live.m3u8'): 
        os.remove('static/stream/live.m3u8')

    for fileName in listdir(folderPath):
        # Check file extension
        if fileName.endswith('.m4s') or fileName.endswith('.tmp') or fileName.endswith('.ts'):
            # Remove File
            os.remove(folderPath + fileName)

def clearTMP():
    folderPath = 'data/tmp/'
    for fileName in listdir(folderPath):
        # Check file extension
        if fileName.endswith('.tmp'):
            # Remove File
            os.remove(folderPath + fileName)

def removeVideos():
    folderPath = 'static/uploads/videos/'
    media_lib.deleteAllVideos()
    for fileName in listdir(folderPath):
        # Check file extension
        if fileName.endswith('.mp4'):
            # Remove File
            os.remove(folderPath + fileName)

def resetSystem():
    if os.path.exists('data/media_library.db'):
        os.remove('data/media_library.db')
    if os.path.exists('data/schedule.db'):
        os.remove('data/schedule.db')
    media_lib.createDB()

def getSize(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def getSysInfo():
    uname = platform.uname()
    lscpu = subprocess.check_output(['lscpu']).decode('utf-8')
    cpu_usage = psutil.cpu_percent()
    last_reboot = psutil.boot_time()
    boot_time = datetime.datetime.fromtimestamp(last_reboot)
    boot_time = "{:02d}.{:02d}.{:04d} {:02d}:{:02d}:{:02d}".format(
                    boot_time.day, 
                    boot_time.month, 
                    boot_time.year, 
                    boot_time.hour, 
                    boot_time.minute, 
                    boot_time.second
                )

    sysinfo = {
        'system':uname.system, 
        'cpu':lscpu.split('\n')[0].split(':')[1].strip(), 
        'cpu_percent':float(cpu_usage),
        'cpu_temp': 0,
        'boot_time':boot_time
    }
    return json.dumps(sysinfo)

def getMemInfo():
    mem = psutil.virtual_memory()
    mem_info = {
        'total':getSize(mem.total), 
        'available':getSize(mem.available),
        'used':getSize(mem.used),
        'percent':float(mem.percent)
    }
    return json.dumps(mem_info)

def getDiscInfo():
    curLoc = os.path.dirname(os.path.abspath(__file__))
    try:
        result = subprocess.check_output(['df', '-h', curLoc]).decode('utf-8').split('\n')[1]
        result = result.split()
        disc_info = {
            'filesystem': result[0],
            'total': result[1][:len(result[1])-1],
            'used': result[2][:len(result[2])-1],
            'free': result[3][:len(result[3])-1],
            'mount': result[5]
        }

        return json.dumps(disc_info)

    except subprocess.CalledProcessError as e:
        print("Błąd podczas wykonania polecenia 'df':", e)
        return None

def saveScheduleConfig(adGroup, defaultInterrupt):
    config_ini = configparser.ConfigParser()
    config_ini.read('data/schedule.ini')
    config_ini['schedule']['adGroup'] = adGroup
    config_ini['schedule']['defaultInterrupt'] = defaultInterrupt

    config = configparser.ConfigParser()
    config.read_dict(config_ini)
    with open('data/schedule.ini', 'w') as configfile:
        config.write(configfile)

def getScheduleConfig():
    config_ini = configparser.ConfigParser()
    config_ini.read('data/schedule.ini')
    print(config_ini['schedule'])
    return [config_ini['schedule']['adGroup'], config_ini['schedule']['defaultInterrupt']]

def loadConfig():
    import config
    config_ini = configparser.ConfigParser()
    config_ini.read('data/config.ini')
    
    config.stream_w = config_ini['stream']['stream_w']
    config.stream_h = config_ini['stream']['stream_h']
    config.framerate = config_ini['stream']['framerate']
    config.preset = config_ini['stream']['preset']
    config.enable_restream = config_ini['stream']['enable_restream']
    config.stream_out = config_ini['stream']['stream_out']
    config.name = config_ini['channel']['name']
    config.description = config_ini['channel']['description']
    config.mode = config_ini['channel']['mode']

def getAllSettings():
    config_ini = configparser.ConfigParser()
    config_ini.read('data/config.ini')

    settings = [
        config_ini['stream']['stream_w'],
        config_ini['stream']['stream_h'],
        config_ini['stream']['framerate'],
        config_ini['stream']['preset'],
        config_ini['stream']['enable_restream'],
        config_ini['stream']['stream_out'],
        config_ini['channel']['name'],
        config_ini['channel']['description'],
        config_ini['channel']['mode'],   
        config_ini['system']['stream_port'],
        config_ini['system']['frontend_port'],   
        config_ini['admin']['user'],
        config_ini['admin']['password'], #12
        config_ini['overlay']['logo_w'],
        config_ini['overlay']['logo_h'],
        config_ini['overlay']['logo_transparency'],
        config_ini['overlay']['horizontal_position'],
        config_ini['overlay']['horizontal_margin'],
        config_ini['overlay']['vertical_position'],
        config_ini['overlay']['vertical_margin'],   
    ] # 0-12
    return settings

def saveChannelSettings(name, description, mode):
    config_ini = configparser.ConfigParser()
    config_ini.read('data/config.ini')
    config_ini['channel']['name'] = name
    config_ini['channel']['description'] = description
    config_ini['channel']['mode'] = mode

    config = configparser.ConfigParser()
    config.read_dict(config_ini)
    with open('data/config.ini', 'w') as configfile:
        config.write(configfile)
    
    # reloading settings
    loadConfig()

def saveStreamSettings(stream_w, stream_h, framerate, preset, enable_restream, stream_out):
    import config
    config_ini = configparser.ConfigParser()
    config_ini.read('data/config.ini')
    config_ini['stream']['stream_w'] = stream_w
    config_ini['stream']['stream_h'] = stream_h
    config_ini['stream']['framerate'] = framerate
    config_ini['stream']['preset'] = preset
    config_ini['stream']['enable_restream'] = enable_restream
    config_ini['stream']['stream_out'] = stream_out

    conf = configparser.ConfigParser()
    conf.read_dict(config_ini)
    with open('data/config.ini', 'w') as configfile:
        conf.write(configfile)

    # reloading settings
    loadConfig()
    control_data = control.loadTMP(config.tmp)
    control_data['restart_stream']=True
    control.saveTMP(control_data, config.tmp)

def saveSystemSettings(user, password, stream_port, frontend_port):
    config_ini = configparser.ConfigParser()
    config_ini.read('data/config.ini')
    config_ini['system']['stream_port'] = stream_port
    config_ini['system']['frontend_port'] = frontend_port
    config_ini['admin']['user'] = user
    config_ini['admin']['password'] = password

    config = configparser.ConfigParser()
    config.read_dict(config_ini)
    with open('data/config.ini', 'w') as configfile:
        config.write(configfile)

    # reloading settings
    loadConfig()

def saveOverlaySettings(logo_w, logo_h, logo_transparency, horizontal_position, horizontal_margin, vertical_position, vertical_margin):
    import config
    config_ini = configparser.ConfigParser()
    config_ini.read('data/config.ini')
    config_ini['overlay']['logo_w'] = logo_w
    config_ini['overlay']['logo_h'] = logo_h
    config_ini['overlay']['logo_transparency'] = logo_transparency
    config_ini['overlay']['horizontal_position'] = horizontal_position
    config_ini['overlay']['horizontal_margin'] = horizontal_margin
    config_ini['overlay']['vertical_position'] = vertical_position
    config_ini['overlay']['vertical_margin'] = vertical_margin

    conf = configparser.ConfigParser()
    conf.read_dict(config_ini)
    with open('data/config.ini', 'w') as configfile:
        conf.write(configfile)

    # reloading settings
    loadConfig()
    control_data = control.loadTMP(config.tmp)
    control_data['restart_stream']=True
    control.saveTMP(control_data, config.tmp)

