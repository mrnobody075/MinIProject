import sys
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
                             QGroupBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

# Ensure SQLite database and table exist
conn = sqlite3.connect('C:/Users/vishal/PycharmProjects/MiniProject/employee.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    time TEXT NOT NULL
                 )''')
conn.commit()

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def markAttendance(name):
    cursor.execute("SELECT * FROM attendance WHERE name = ? AND date(time) = date('now')", (name,))
    record = cursor.fetchone()
    if record is None:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO attendance (name, time) VALUES (?, ?)", (name, now))
        conn.commit()
        return True  # Indicates new attendance was marked
    return False  # Attendance already marked for today

def loadImages(path):
    images = []
    classNames = []
    myList = os.listdir(path)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    return images, classNames

class AttendanceSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Worker Attendance System")
        self.setGeometry(100, 100, 1200, 800)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.cap = cv2.VideoCapture(0)

        self.knownFaces = {}
        self.totalCount = 0
        self.initUI()
        self.startRecognition()

    def initUI(self):
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        titleLabel = QLabel("Worker Attendance System", self)
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet("font-size: 28px; font-weight: bold; margin: 20px 0; color: #343a40;")
        layout.addWidget(titleLabel)

        mainLayout = QHBoxLayout()
        layout.addLayout(mainLayout)

        leftPanel = QVBoxLayout()
        mainLayout.addLayout(leftPanel, 1)

        self.startButton = QPushButton("Start Recognition", self)
        self.startButton.setStyleSheet("font-size: 18px; padding: 10px; background-color: #007bff; color: white;")
        self.startButton.clicked.connect(self.startRecognition)
        leftPanel.addWidget(self.startButton)

        self.quitButton = QPushButton("Quit", self)
        self.quitButton.setStyleSheet("font-size: 18px; padding: 10px; background-color: #dc3545; color: white;")
        self.quitButton.clicked.connect(self.closeApp)
        leftPanel.addWidget(self.quitButton)

        tableGroupBox = QGroupBox("Attendance Table")
        tableGroupBox.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px; color: #343a40; padding: 10px; padding-bottom: 5px;")
        leftPanel.addWidget(tableGroupBox)

        tableLayout = QVBoxLayout(tableGroupBox)
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Name", "Time"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setVisible(False)
        tableLayout.addWidget(self.tableWidget)

        self.totalCountLabel = QLabel("Total Workers Recognized: 0", self)
        self.totalCountLabel.setAlignment(Qt.AlignCenter)
        self.totalCountLabel.setStyleSheet("font-size: 18px; font-weight: bold; color: #28a745; margin-top: 10px;")
        leftPanel.addWidget(self.totalCountLabel)

        rightPanel = QVBoxLayout()
        mainLayout.addLayout(rightPanel, 3)

        webcamGroupBox = QGroupBox("Webcam Feed")
        rightPanel.addWidget(webcamGroupBox)

        webcamLayout = QVBoxLayout(webcamGroupBox)
        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        webcamLayout.addWidget(self.imageLabel)

    def startRecognition(self):
        path = "images"
        images, classNames = loadImages(path)
        self.encodeListKnown = findEncodings(images)
        self.classNames = classNames
        self.knownFaces.clear()
        self.totalCount = 0
        self.updateAttendanceTableFromDB()  # Ensure table is reset to match the database
        self.totalCountLabel.setText("Total Workers Recognized: 0")
        self.timer.start(30)
    def updateFrame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace, tolerance=0.5)
            faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
            best_match_index = np.argmin(faceDis)

            def updateAttendanceTableFromDB(self):
                """Load all attendance records from the database and update the table."""
                self.tableWidget.setRowCount(0)  # Clear existing rows
                cursor.execute("SELECT Name, Time FROM attendance ORDER BY Name")
                rows = cursor.fetchall()
                for name, time in rows:
                    rowPosition = self.tableWidget.rowCount()
                    self.tableWidget.insertRow(rowPosition)
                    self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(name))
                    self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(time))
                self.totalCount = len(rows)
                self.totalCountLabel.setText(f"Total Workers Recognized: {self.totalCount}")

            # Update logic in updateFrame:
            if matches[best_match_index]:
                name = self.classNames[best_match_index].upper()
                if name not in self.knownFaces:
                    marked = markAttendance(name)
                    if marked:
                        self.totalCount += 1
                        self.totalCountLabel.setText(f"Total Workers Recognized: {self.totalCount}")
                        self.updateAttendanceTable(name)
                    self.knownFaces[name] = True
            else:
                name = "Unrecognized"

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            color = (0, 255, 0) if name != "Unrecognized" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
        self.imageLabel.setPixmap(QPixmap.fromImage(img))

    def updateAttendanceTable(self, name):
        """Update the GUI table with the latest recognized worker."""
        now = datetime.now().strftime('%H:%M:%S')
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)
        self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(name))
        self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(now))

    def updateAttendanceTableFromDB(self):
        """Load all attendance records from the database and update the table."""
        self.tableWidget.setRowCount(0)  # Clear existing rows
        cursor.execute("SELECT Name, Time FROM attendance ORDER BY Name")
        rows = cursor.fetchall()
        for name, time in rows:
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(name))
            self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(time))
        self.totalCount = len(rows)
        self.totalCountLabel.setText(f"Total Workers Recognized: {self.totalCount}")

    def closeApp(self):
        self.timer.stop()
        self.cap.release()
        cv2.destroyAllWindows()
        conn.close()
        self.close()

app = QApplication(sys.argv)
window = AttendanceSystem()
window.show()
sys.exit(app.exec_())
