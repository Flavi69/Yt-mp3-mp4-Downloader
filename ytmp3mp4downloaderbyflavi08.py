from PySide6.QtCore import QEvent, Qt, QObject, Signal
from PySide6.QtWidgets import (
    QApplication, QMessageBox, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QProgressBar, QComboBox, QFileDialog
)
from pytube import YouTube
from moviepy.editor import AudioFileClip
import os
import threading


class DownloadCompletedEvent(QEvent):
    EVENT_TYPE = QEvent.registerEventType(QEvent.User)


class EventReceiver(QObject):
    download_completed = Signal()


def show_message_box(message):
    msg_box = QMessageBox()
    msg_box.setText(message)
    msg_box.exec_()

app = QApplication([])

window = QWidget()
window.setWindowTitle("YouTube Downloader")


link_input = QLineEdit()
format_selector = QComboBox()
format_selector.addItems(["MP3", "MP4"])
download_button = QPushButton("Download")
progress_bar = QProgressBar()
location_input = QLineEdit()
location_button = QPushButton("Choose Location")

layout = QVBoxLayout()
layout.addWidget(QLabel("YouTube Link"))
layout.addWidget(link_input)
layout.addWidget(QLabel("Select Format"))
layout.addWidget(format_selector)
layout.addWidget(QLabel("Download Location"))
layout.addWidget(location_input)
layout.addWidget(location_button)
layout.addWidget(download_button)
layout.addWidget(progress_bar)

window.setLayout(layout)


download_location = None


def update_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    progress_bar.setValue(percentage)
# made by flavi08


def download_video():
    global download_location  

    link = link_input.text().strip()
    if link:
        try:
            selected_option = format_selector.currentText()
            if selected_option == 'MP3':
                download_audio(link)
            elif selected_option == 'MP4':
                if download_location:
                    download_mp4(link)
                else:
                    show_message_box('Please select a download location!')
            else:
                show_message_box('No option selected!')
        except Exception as e:
            show_message_box(f'An error occurred: {str(e)}')


def choose_location_and_download(link):
    global download_location  

    options = QFileDialog.Options()
    options |= QFileDialog.ShowDirsOnly
    selected_directory = QFileDialog.getExistingDirectory(window, "Choose Download Location", options=options)
    if selected_directory:
        download_location = selected_directory  # Set the download location
        location_input.setText(selected_directory)

# MP3
def download_audio(link):
    global download_location  l

    if download_location:
        yt = YouTube(link, on_progress_callback=update_progress)
        ys = yt.streams.filter(only_audio=True).first()
        threading.Thread(target=download_audio_thread, args=(ys, download_location)).start()

def download_audio_thread(stream, download_location):
    audio_filename = stream.download(output_path=download_location)
    mp3_filename = os.path.join(download_location, os.path.splitext(os.path.basename(audio_filename))[0] + ".mp3")

    audio = AudioFileClip(audio_filename)
    audio.write_audiofile(mp3_filename, bitrate='320k')
    audio.close()

    os.remove(audio_filename)

    event_receiver.download_completed.emit()

# MP4
def download_mp4(link):
    global download_location  

    if download_location:
        yt = YouTube(link, on_progress_callback=update_progress)
        ys = yt.streams.get_highest_resolution()
        threading.Thread(target=download_mp4_thread, args=(ys, download_location)).start()

def download_mp4_thread(stream, download_location):
    stream.download(output_path=download_location)
    event_receiver.download_completed.emit()

event_receiver = EventReceiver()
event_receiver.download_completed.connect(lambda: show_message_box("Download Completed!"))

download_button.clicked.connect(download_video)
location_button.clicked.connect(choose_location_and_download)

window.show()
app.exec_()
