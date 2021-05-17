import cv2
import threading
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QImage

running = False

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def play(self):
        global running
        running = True
        th = threading.Thread(target=self.run)
        th.start()
        print("Play!")

    def stop(self):
        global running
        running = False
        print("Stop!")

    def run(self):
        cap = cv2.VideoCapture(0)

        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.label.resize(int(width), int(height))

        while running:
            ret, img = cap.read()

            if ret:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, c = img.shape
                qImg = QImage(img.data, w, h, w*c, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)
                self.label.setPixmap(pixmap)

            else:
                QMessageBox.about(self, "Error", "Cannot read frame.") # 오류발생 수정 필요!
                
                print("cannot read frame.")
                break
        cap.release()
        print("Thread end.")

    def initUI(self):
        play_Button = QPushButton('play')
        stop_Button = QPushButton('stop')


        self.label = QLabel()

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.label)
        hbox.addWidget(play_Button)
        hbox.addWidget(stop_Button)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(3)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)

        self.setWindowTitle('졸음운전 방지 시스템')
        self.setGeometry(300, 300, 300, 200)
        self.show()

        play_Button.clicked.connect(self.play)
        stop_Button.clicked.connect(self.stop)




if __name__ == '__main__':

    app = QApplication(sys.argv)
    frame = App()
    sys.exit(app.exec_())
