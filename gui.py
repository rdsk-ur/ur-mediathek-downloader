import sys
import logging
from logging import info, error, warning
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication, QProgressBar, QLabel, QLineEdit, QFileDialog, QPlainTextEdit
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread, QObject
import requests
import subprocess
import time

import util
import video

class ConvertThread(QThread):
    total = pyqtSignal(int)
    update = pyqtSignal(int)
    def __init__(self, url, filename, username, password):
        super().__init__()
        self.abort = False

        self.url = url
        self.filename = filename
        self.username = username
        self.password = password

    def run(self):
        self.update.emit(0)
        self.total.emit(1)

        try:
            session = util.get_authenticated_session({
                "username": self.username,
                "password": self.password,
            })
            meta = video.get_meta(self.url, session)
            info(f"Manifest: " + meta["manifest_url"])
            segments = video.get_segments(meta["manifest_url"])

            len_audio = len(segments["audio"])
            len_video = len(segments["video"])
            info(f"{len_audio} audio segments")
            info(f"{len_video} video segments")

            self.total.emit(len_audio + len_video)
            v = 0

            info("Download video")

            videopart_name = f"{self.filename}.videopart"
            audiopart_name = f"{self.filename}.audiopart"

            with open(videopart_name, "wb") as out_file:
                for url in segments["video"]:
                    if self.abort:
                        warning("Aborted")
                        return
                    res = requests.get(url)
                    out_file.write(res.content)
                    v += 1
                    self.update.emit(v)

            info("Download audio")

            with open(audiopart_name, "wb") as out_file:
                for url in segments["audio"]:
                    if self.abort:
                        warning("Aborted")
                        return
                    res = requests.get(url)
                    out_file.write(res.content)
                    v += 1
                    self.update.emit(v)

            info("Merge using ffmpeg")

            subprocess.run([
                "ffmpeg",
                "-i", videopart_name,
                "-i", audiopart_name,
                "-c", "copy",
                self.filename
            ])

            info("Done")
        except Exception as e:
            error(str(e))

class PlainTextLogger(QObject, logging.Handler):
    # the signal is required to rediret the LogRecord to the main thread
    signal = pyqtSignal(str)
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)

        self.signal.connect(self.add_line)
        logging.getLogger().addHandler(self)

        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        if record.levelname == "ERROR":
            msg = f'<span style="color: red">{msg}</span>'
        elif record.levelname == "WARNING":
            msg = f'<span style="color: orange">{msg}</span>'
        self.signal.emit(msg)

    @pyqtSlot(str)
    def add_line(self, msg):
        self.widget.appendHtml(msg)

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.convert_thread = None

        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        # username
        self.txt_username = QLineEdit("", self)
        grid_layout.addWidget(self.txt_username, 0, 1, 1, 2)
        grid_layout.addWidget(QLabel("Username:", self), 0, 0)

        # password
        self.txt_password = QLineEdit("", self)
        self.txt_password.setEchoMode(QLineEdit.Password)
        grid_layout.addWidget(self.txt_password, 1, 1, 1, 2)
        grid_layout.addWidget(QLabel("Password:", self), 1, 0)

        # url input
        self.txt_url = QLineEdit("", self)
        grid_layout.addWidget(self.txt_url, 2, 1, 1, 2)
        grid_layout.addWidget(QLabel("URL:", self), 2, 0)

        # output file
        self.txt_output = QLineEdit("", self)
        self.txt_output.setReadOnly(True)
        self.btn_choose = QPushButton("Choose", self)
        self.btn_choose.clicked.connect(self.btn_choose_click)
        grid_layout.addWidget(self.txt_output, 3, 1)
        grid_layout.addWidget(self.btn_choose, 3, 2)
        grid_layout.addWidget(QLabel("Output:", self), 3, 0)

        # progress bar
        self.progress = QProgressBar(self)
        grid_layout.addWidget(self.progress, 4, 0, 1, 3)

        # log
        self.lbl_log = PlainTextLogger(self)
        logging.getLogger().setLevel(logging.INFO)
        grid_layout.addWidget(self.lbl_log.widget, 5, 0, 1, 3)

        # download button
        self.btn_download = QPushButton("Download", self)
        self.btn_download.clicked.connect(self.btn_download_click)
        grid_layout.addWidget(self.btn_download, 6, 2)

        self.setWindowTitle("UR Mediathek Downloader")

    @pyqtSlot()
    def btn_choose_click(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Output File", "", "MP4-Files (*.mp4)")
        if filename:
            if not filename.endswith(".mp4"):
                filename += ".mp4"
            self.txt_output.insert(filename)

    @pyqtSlot()
    def reset_thread(self):
        self.convert_thread = None
        self.btn_download.setText("Download")

    @pyqtSlot()
    def btn_download_click(self):
        if self.convert_thread is not None:
            self.convert_thread.abort = True
        else:
            filename = self.txt_output.text()
            if filename == "":
                warning("Please provide a file name for the output")
                return

            self.btn_download.setText("Abort")
            self.convert_thread = ConvertThread(
                url=self.txt_url.text(),
                filename=filename,
                username=self.txt_username.text(),
                password=self.txt_password.text())
            self.convert_thread.total.connect(self.progress.setMaximum)
            self.convert_thread.update.connect(self.progress.setValue)
            self.convert_thread.finished.connect(self.reset_thread)
            self.convert_thread.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = MyWindow()
    wnd.resize(700, 400)
    wnd.show()
    sys.exit(app.exec_())
