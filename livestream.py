import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
import time
import threading
import queue
import datetime

Gst.init(None)

video_queue = queue.Queue()

def play_live_video(video_path, resolution, framerate):
    pipeline_str = f'filesrc location={video_path} ! decodebin ! videoconvert ! videoscale ! video/x-raw,width={resolution[0]},height={resolution[1]} ! videorate ! video/x-raw,framerate={framerate}/1 ! autovideosink'
    pipeline = Gst.parse_launch(pipeline_str)
    pipeline.set_state(Gst.State.PLAYING)

    bus = pipeline.get_bus()
    msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.EOS | Gst.MessageType.ERROR)
    pipeline.set_state(Gst.State.NULL)

# Funkcja wątku do transmisji na żywo
def live_streaming_thread(resolution, framerate):
    while True:
        try:
            video_info = video_queue.get()
            video_path = video_info["video"]
            timestamp = video_info["timestamp"]

            current_time = time.time()
            start_time = timestamp.timestamp()

            # Oczekiwanie na odpowiednią godzinę do rozpoczęcia transmisji
            while current_time < start_time:
                time.sleep(1)
                current_time = time.time()

            play_live_video(video_path, resolution, framerate)

        except queue.Empty:
            pass

# Funkcja do ustawiania parametrów dla wszystkich filmów
def set_video_parameters():
    for video_info in video_list:
        video_queue.put(video_info)

# Przykładowe dane
video_list = [
    {"video": "/ścieżka/do/wideo1.mp4", "timestamp": datetime.datetime(2024, 2, 11, 12, 0, 0)},
    {"video": "/ścieżka/do/wideo2.mp4", "timestamp": datetime.datetime(2024, 2, 11, 13, 0, 0)}
]

# Parametry wideo ustawione przez użytkownika
user_resolution = (1280, 720)  # Przykładowa rozdzielczość
user_framerate = 30  # Przykładowa ilość klatek na sekundę

# Rozpoczęcie wątku do transmisji na żywo
streaming_thread = threading.Thread(target=live_streaming_thread, args=(user_resolution, user_framerate))
streaming_thread.start()

# Ustawianie parametrów dla wszystkich filmów
set_video_parameters()

# Oczekiwanie na zakończenie wątku
streaming_thread.join()
