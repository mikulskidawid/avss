import subprocess, config, os, schedule_gen, media_lib, time
from datetime import datetime, timedelta, date

def videoProcessing(filepath):
    input = filepath+'_proc.mp4'
    output = filepath+'.mp4'
    ffmpeg_cmd = (
        f"ffmpeg -i {input} -vf 'fps=30,scale=1920:1080' -b:v 2M "
        "-c:v h264 -preset ultrafast -c:a aac -b:a 192k -ar 44100 -ac 2 "
        f"{output}"
    )
    process = subprocess.Popen(ffmpeg_cmd, shell=True)
    process.wait()
    if os.path.exists(input):
        os.remove(input)

def generatePlaylist(file=1):
    if os.path.exists('schedule/playlist1.txt'):
        os.remove('schedule/playlist1.txt')
    if os.path.exists('schedule/playlist2.txt'):
        os.remove('schedule/playlist2.txt')


    schedule = schedule_gen.scheduleInfo()
    with open('schedule/playlist'+str(file)+'.txt', 'w') as file:
        for s in schedule:
            '''timeNow = datetime.now().second + datetime.now().minute*60+datetime.now().hour*60
            itemDate = datetime.strptime(s[3], '%d-%m-%Y')
            itemTime = media_lib.getSeconds(s[2])

            hours, minutes = divmod(int(itemTime/60), 60)
            seconds = int(itemTime%60)
            itemDate = itemDate +timedelta(hours=hours, minutes=minutes, seconds=seconds)

            if itemDate >= datetime.now()+timedelta(days=3):
                break'''

            line = "file '../static/uploads/videos/"+s[0]+".mp4'"
            file.write(line + '\n')
        file.write("file 'playlist2.txt'")

# Streaming functions

def streamTV(
    input='video1.mp4',
    output='static/stream/live.m3u8',
    setting_list='',
    ):
    
    '''
    ffmpeg = [
        'ffmpeg',
        '-re',
        '-stream_loop','-1',
        '-i',input,
        '-i', 'logo2.png', '-filter_complex', '[0:v]scale=1280:720[v];[1:v]scale=100:100,format=rgba,colorchannelmixer=aa=0.5[ov];[v][ov]overlay=W-w-10:10',
        '-r',str(framerate),
        '-c:a', 'copy',
        '-s', '1280x720', '-preset', 'veryfast',
        '-listen', '1',
        '-f', 'flv', output
    ]
    '''

    test = "'-f', 'hls', '-strftime', '1','-hls_time', '4','-hls_flags', 'delete_segments', 'static/stream/live.m3u8'"

    offset=schedule_gen.getOffset()
    print('Synchronizing the schedule...')
    time.sleep(offset)
    print('Schedule synchronized')

    generatePlaylist()

    horizontal_position = ''
    vertical_position = ''

    if setting_list[16] == '1':
        horizontal_position = str(setting_list[17])
    elif setting_list[16] == '2':
        horizontal_position = "(W-w)/2"
    elif setting_list[16] == '3':
        horizontal_position = "W-w-"+str(setting_list[17])

    if setting_list[18] == '1':
        vertical_position = str(setting_list[19])
    elif setting_list[18] == '2':
        vertical_position = "(H-h)/2"
    elif setting_list[18] == '3':
        vertical_position = "H-h-"+str(setting_list[19])

    logo_transparency = float(float(setting_list[15])/100.0)

    ffmpeg = [
        'ffmpeg',
        '-re',
        '-f','concat',
        '-safe', '0',
        '-i','schedule/playlist1.txt',
        '-i', 'logo2.png', 
        '-filter_complex', 
        '[0:v]scale='+str(setting_list[0])+':'+str(setting_list[1])+'[v];[1:v]scale='+str(setting_list[13])+':'+str(setting_list[14])+',format=rgba,colorchannelmixer=aa='+str(logo_transparency)+'[ov];[v][ov]overlay='+horizontal_position+':'+vertical_position,
        '-r',str(setting_list[2]),
        '-c:v', 'h264', '-crf', str(setting_list[2]),
        '-s', str(setting_list[0])+'x'+str(setting_list[1]),
        '-preset', setting_list[3],
        '-f', 'flv', 'rtmp://localhost/live/stream'
        
        
    ]

    '''if int(setting_list[4]) == 1:
        ffmpeg +=[
        '-filter_complex', 
        '[0:v]scale='+str(setting_list[0])+':'+str(setting_list[1])+'[v];[1:v]scale='+str(setting_list[13])+':'+str(setting_list[14])+',format=rgba,colorchannelmixer=aa='+str(logo_transparency)+'[ov];[v][ov]overlay='+horizontal_position+':'+vertical_position,
        '-r',str(setting_list[2]),
        '-c:v', 'h264', '-crf', str(setting_list[2]),
        '-b:v', '2M', '-b:a', '192k',
        '-s', str(setting_list[0])+'x'+str(setting_list[1]),
        '-preset', setting_list[3],
        '-f', 'flv', '-listen', '1', setting_list[5]
        ]'''

    return subprocess.Popen(ffmpeg)

def streamNoSignal(
    output='static/stream/live.m3u8',
    setting_list=''
    ):
    # ffmpeg -f lavfi -i testsrc=size=640x480:rate=30 -vf format=rgb24 -c:v libx264 -preset ultrafast -tune zerolatency -g 30 -b:v 500k -hls_time 2 -hls_list_size 5 -hls_wrap 10 live.m3u8

    ffmpeg = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'smptebars=size='+str(setting_list[0])+'x'+str(setting_list[1])+':rate='+str(setting_list[2]),
        '-vf', 'format=rgb24',
        '-c:v', 'h264',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-g', str(setting_list[2]),
        '-b:v', '500k',
        '-s', str(setting_list[0])+'x'+str(setting_list[1]),
        '-strftime', '1',
        '-hls_time', '4',
        '-hls_flags', 'delete_segments',
        output
    ]
    
    print(ffmpeg)

    return subprocess.Popen(ffmpeg)

def streamTest(output='http://localhost:8080'):
    ffmpeg = [
        'ffmpeg', '-re', '-f', 'lavfi', '-i',
        "aevalsrc=if(eq(floor(t)\,ld(2))\,st(0\,random(4)*3000+1000))\;st(2\,floor(t)+1)\;st(1\,mod(t\,1))\;(0.6*sin(1*ld(0)*ld(1))+0.4*sin(2*ld(0)*ld(1)))*exp(-4*ld(1)) [out1]; testsrc=s=1920x1080,drawtext=borderw=3:fontcolor=white:fontsize=60:text='%{localtime}':x=\(w-text_w\)/2:y=\(h-text_h-line_h\)/2 [out0]",
         '-r', '30',
        '-acodec', 'aac',
        '-ac', '2', '-ab', '128k', '-ar', '44100', '-c:v', 'libx264', '-profile:v', 'main',
        '-force_key_frames', '"expr:gte(t,n_forced*2)"', '-sc_threshold', '0', '-pix_fmt', 'yuv420p', 
        '-b:v', '500K', '-maxrate', '500K', '-s', '1280x720', '-preset', 'veryfast', 
        '-listen', '1', '-f', 'flv', 'http://localhost:8080'
    ]

    try:
        print('Starting test streaming...')
        subprocess.run(ffmpeg, check=True)
        print('Test stream run successfully')
    except subprocess.CalledProcessError as e:
        print("Could not start broadcasting")
