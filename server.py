import multiprocessing, time, importlib
import ffmpeg, frontend, media_lib, ffmpeg, server_func, config, control, schedule_gen

if __name__ == "__main__":

    print('AVSS running...')
    server_func.clearStream()
    print('Deleted files from static/stream/')
    server_func.clearTMP()
    print('Deleted temp files from data/control/')
    #server_func.resetSystem()
    media_lib.createDB()
    print('Loaded database')
    config.tmp = control.createTMP()
    print('Created temp file at data/tmp/')

    server_func.loadConfig()

    FRONTEND_PROCESS = multiprocessing.Process(target=frontend.server)
    FRONTEND_PROCESS.start()
    print('Flask server started')

    STREAM_SETTINGS = server_func.getAllSettings()
    print(STREAM_SETTINGS)
    LIVESTREAM_PROCESS = ffmpeg.streamTV(setting_list=STREAM_SETTINGS)
    print('Live stream started')

    while(True):
        time.sleep(1)
        control_data = control.loadTMP(config.tmp)
        if control_data['restart_stream']=='True' or control_data['restart_stream']==True:
            LIVESTREAM_PROCESS.kill()
            server_func.clearStream()
            STREAM_SETTINGS = server_func.getAllSettings()
            LIVESTREAM_PROCESS = ffmpeg.streamTV(setting_list=STREAM_SETTINGS)
            control_data['restart_stream']='False'
            control.saveTMP(control_data, config.tmp)
        if control_data['reset_system']=='True' or control_data['reset_system']==True:
            server_func.resetSystem()
            LIVESTREAM_PROCESS.kill()
            server_func.clearStream()
            STREAM_SETTINGS = server_func.getAllSettings()
            LIVESTREAM_PROCESS = ffmpeg.streamTV(setting_list=STREAM_SETTINGS)
            control_data['reset_system']='False'
            control.saveTMP(control_data, config.tmp)

