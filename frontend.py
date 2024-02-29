from flask import Flask, render_template, request, redirect
from fileinput import filename 
import datetime, os, media_lib, server_func, config, json, schedule_gen, ffmpeg

def server():
    webServer = Flask(__name__, template_folder='frontend', static_folder='static')
    webServer.config["UPLOAD_FOLDER"] = "static/uploads"
        
    # main pages

    @webServer.route("/") 
    def dashboard():
        groups = len(media_lib.getGroups())
        videos = len(media_lib.getVideos())
        return render_template('index.html', add_data = [groups, videos])

    @webServer.route("/studio") 
    def studio():
        groups = media_lib.getGroups()
        videos = media_lib.getVideos()
        return render_template(
            'studio.html', 
            streamInfo=config.streamOut,
            groups=groups,
            videos=videos
        )

    @webServer.route("/scheduler") 
    def schedule(): 
        schedule_list = media_lib.getSchedule()
        serie_list = media_lib.getSeries()
        group_list = media_lib.getNotSeries()
        ad_list = media_lib.getAds()
        times = media_lib.getMaxTimes()
        print(server_func.getScheduleConfig())
        scheduleConfig = server_func.getScheduleConfig()

        ads = []

        for ad in ad_list:
            ad_videos =  media_lib.getVideos(ad[0])
            for video in ad_videos:
                ads.append(video)

        return render_template(
            'scheduler.html', 
            schedule_list=schedule_list,
            groups=serie_list+group_list,
            times=times,
            ads=ad_list,
            ad_videos=ads,
            scheduleConfig=scheduleConfig
            )

    @webServer.route("/genschedule")
    def gen_schedule(): 
        get_schedule = schedule_gen.getSchedule()
        return render_template('gen_schedule.html', schedule=get_schedule)

    @webServer.route("/library")
    def library_route(): return redirect('/library/all') 

    @webServer.route("/library/<group>") 
    def library(group='all'): 
        video_list = media_lib.getVideos(group)
        group_list = media_lib.getGroups()
        print(group_list)
        show_videos=1; show_groups=1
        if video_list==[]: 
            show_videos=0
        if group_list==[]: 
            show_groups=0

        if group != 'all': group = int(group)
        
        return render_template(
            'library.html', 
            show_videos=show_videos, 
            videos=video_list,
            show_groups=show_groups,
            groups=group_list,
            group=group
            )

    @webServer.route("/overlay") 
    def channel(): 
        settings =server_func.getAllSettings()
        return render_template('overlay.html', 
        settings=settings)

    @webServer.route("/settings") 
    def settings(): 
        settings =server_func.getAllSettings()
        return render_template('settings.html', settings=settings)

    # file upload

    @webServer.route("/upload/video", methods=['POST'])
    def videoUpload():
        videos = request.files.getlist("videos") 
        for video in videos: 
            if video.filename !='':
                curDate = datetime.datetime.now()
                filename = "video_{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}_{:03d}".format(
                    curDate.year, 
                    curDate.month, 
                    curDate.day, 
                    curDate.hour, 
                    curDate.minute, 
                    curDate.second, 
                    int(curDate.microsecond / 1000)
                )
                filepath = 'static/uploads/videos/'+filename
                video.save(filepath+'_proc.mp4')
                ffmpeg.videoProcessing(filepath)
                video_time = server_func.getVideoTime(filepath+'.mp4')
                media_lib.addVideo(filename, filename, curDate, -1, video_time)


        return redirect('/library')

    # edit pages

    @webServer.route("/edit/video/<id>")
    def videoEditPage(id):
        video = media_lib.getVideo(id)
        groups = media_lib.getGroups()
        if len(video)==0: return redirect('/')
        else:
            return render_template('edit/video_edit.html', video=video[0], groups=groups)

    @webServer.route("/create/group")
    def groupCreator():
        return render_template('edit/group_creator.html')

    @webServer.route("/edit/group/<id>")
    def groupEditPage(id):
        group = media_lib.getGroup(id)
        group = group[0]
        videos = media_lib.getVideosSorted(group[0], group[4], group[5])
        if len(group)==0: return redirect('/')
        else:
            return render_template('edit/group_edit.html', group=group, videos=videos)

    # media management

    @webServer.route("/forms/savevideo", methods=['POST'])
    def editVideo():
        if request.method == 'POST':
            video_id = request.form.get('id')
            videoname = request.form.get('videoname')
            group_id = request.form.get('group_id')
            season = request.form.get('season')
            episode = request.form.get('episode')
            video = media_lib.getVideo(video_id)
            if len(video)!=0 and videoname!="": 
                media_lib.updateVideo(video_id, videoname, group_id, season, episode)
                return redirect('/library')
            else: return redirect('/')

    @webServer.route("/forms/deletevideo", methods=['POST'])
    def deleteVideo():
        if request.method == 'POST':
            video_id = request.form.get('video_id')
            filename = request.form.get('filename')
            video = media_lib.getVideo(video_id)
            if len(video)!=0: 
                media_lib.deleteVideo(video_id)
                os.remove('static/uploads/videos/'+filename+'.mp4')
                return redirect('/library')
            else: return redirect('/')

    # group management

    @webServer.route("/forms/creategroup", methods=['POST'])
    def createGroup():
        if request.method == 'POST':
            groupname = request.form.get('groupname')
            description = request.form.get('description')
            groupType = request.form.get('groupType')
            sort_order = request.form.get('sort_order')
            curDate = datetime.datetime.now()
            if groupname!="" and description!="":
                media_lib.addGroup(groupname, curDate, description, groupType, sort_order)
                return redirect('/library')

    @webServer.route("/forms/savegroup", methods=['POST'])
    def editGroup():
        if request.method == 'POST':
            group_id = request.form.get('id')
            groupname = request.form.get('groupname')
            description = request.form.get('description')
            groupType = request.form.get('groupType')
            sort_order = request.form.get('sort_order')
            group = media_lib.getGroup(group_id)
            if len(group)!=0 and groupname!="": 
                media_lib.updateGroup(group_id, groupname, description, groupType, sort_order)
                return redirect('/library')
            else: return redirect('/')

    @webServer.route("/forms/deletegroup", methods=['POST'])
    def deleteGroup():
        if request.method == 'POST':
            group_id = request.form.get('group_id')
            group = media_lib.getGroup(group_id)
            if len(group)!=0:
                media_lib.deleteGroup(group_id)
                return redirect('/library')
            else: return redirect('/')

    @webServer.route("/forms/genschedule", methods=['POST'])
    def gen_schedule_form():
        if request.method == 'POST':
            schedule_gen.createScheduleDB()
            schedule_gen.clearSchedule()
            days = request.form.get('scheduleDays')
            schedule_gen.createSchedule(int(days))
            return redirect('/genschedule')
    
    # settings

    @webServer.route("/forms/save/channel", methods=['POST'])
    def savechannel():
        if request.method == 'POST':
            channel_name = request.form.get('channel_name')
            channel_desc = request.form.get('channel_desc')
            channel_mode = request.form.get('channel_mode')
            server_func.saveChannelSettings(channel_name, channel_desc, channel_mode)
            return redirect('/settings')

    @webServer.route("/forms/save/system", methods=['POST'])
    def savesystem():
        if request.method == 'POST':
            admin_user = request.form.get('admin_user')
            admin_passwd = request.form.get('admin_passwd')
            stream_port = request.form.get('stream_port')
            frontend_port = request.form.get('frontend_port')
            server_func.saveSystemSettings(admin_user, admin_passwd, stream_port, frontend_port)
            return redirect('/settings')

    @webServer.route("/forms/save/stream", methods=['POST'])
    def savestream():
        if request.method == 'POST':
            stream_w = request.form.get('stream_w')
            stream_h = request.form.get('stream_h')
            framerate = request.form.get('framerate')
            preset = request.form.get('preset')
            enable_restream = request.form.get('enable_restream')
            stream_out = request.form.get('stream_out')
            server_func.saveStreamSettings(
                stream_w,
                stream_h,
                framerate,
                preset,
                enable_restream,
                stream_out
            )
            return redirect('/settings')

    @webServer.route("/forms/save/overlay", methods=['POST'])
    def saveoverlay():
        if request.method == 'POST':
            logo_w = request.form.get('logo_w')
            logo_h = request.form.get('logo_h')
            logo_transparency = request.form.get('logo_transparency')
            horizontal_position = request.form.get('horizontal_position')
            horizontal_margin = request.form.get('horizontal_margin')
            vertical_position = request.form.get('vertical_position')
            vertical_margin = request.form.get('vertical_margin')
            server_func.saveOverlaySettings(
                logo_w,
                logo_h,
                logo_transparency,
                horizontal_position,
                horizontal_margin,
                vertical_position,
                vertical_margin
            )
            return redirect('/overlay')

    # save schedule template

    @webServer.route("/forms/save/scheduletemplate", methods=['POST'])
    def savescheduletemplate():
        if request.method == 'POST':
            adGroup = request.form.get('adGroup')
            defaultInterrupt = request.form.get('defaultInterrupt')
            scheduleList = request.form.get('schedule')
            fullSchedule = json.loads(scheduleList)
            media_lib.clearScheduleTemplate()
            media_lib.saveScheduleTemplate(fullSchedule)
            server_func.saveScheduleConfig(adGroup, defaultInterrupt)
            return redirect('/scheduler')
    
    # other requests

    @webServer.route("/requests/servertime")
    def servertime():
        curDate = datetime.datetime.now()
        time = "{:02d}:{:02d}:{:02d}".format(
            curDate.hour, 
            curDate.minute, 
            curDate.second, 
        )
        return time

    @webServer.route("/requests/sysinfo")
    def sysinfo(): return server_func.getSysInfo()

    @webServer.route("/requests/meminfo")
    def meminfo(): return server_func.getMemInfo()

    @webServer.route("/requests/discinfo")
    def discinfo(): return server_func.getDiscInfo()

    @webServer.route("/requests/playinfo")
    def playinfo(): 
        schedule = schedule_gen.filterSchedule()
        video = media_lib.getVideo(schedule[0][1])
        group = media_lib.getGroup(video[0][4])
        if schedule_gen.currentItemID()!=-1:
            return json.dumps({
                'group_name': group[0][1],
                'group_type': group[0][4],
                'video_name': video[0][2],
                'video_season': video[0][5],
                'video_episode': video[0][6]
            })
        else: 
            return json.dumps({
                'group_name': "",
                'group_type': 0,
                'video_name': "No signal",
                'video_season': 0,
                'video_episode': 0
            })

    @webServer.route("/requests/playlist_id")
    def playlistId(): 
        return str(schedule_gen.currentItemID())

    @webServer.route("/requests/daily_playlist")
    def dailyPlaylist(): 
        schedule = schedule_gen.todayScheduleInfo()
        return json.dumps(schedule)
            
    # error handler

    @webServer.errorhandler(403) 
    def err403(): return redirect('/')

    @webServer.errorhandler(404) 
    def err404(): return redirect('/')

    # run www server
    
    webServer.run(debug=False, port=8080) 


