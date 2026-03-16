import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSystemTrayIcon, QStyle
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from pathlib import Path



from pynput import keyboard, mouse
import time


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Roger's Keystroke Logger")
        
        self.trayIcon = QSystemTrayIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMenuButton))
        self.trayIcon.activated.connect(self.show)
        self.trayIcon.show()
        
        self.strokes = []
        self.keyboard_listener = keyboard.Listener(on_press=self.on_keypress)
        self.mouse_listener = mouse.Listener(on_click=self.on_mouseclick)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.mainLayout = QVBoxLayout()
        self.central_widget.setLayout(self.mainLayout)
        self.infoLabel = QLabel("click record to start recording, stop to stop recording, and save to stop and save")
        self.mainLayout.addWidget(self.infoLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.statusLabel = QLabel("NOT RECORDING")
        self.mainLayout.addWidget(self.statusLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.savedLabel = QLabel(" ")
        self.mainLayout.addWidget(self.savedLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        buttonLayout = QHBoxLayout()
        self.mainLayout.addLayout(buttonLayout)
        
        startButton = QPushButton("start")
        startButton.clicked.connect(self.startButtonPressed)
        buttonLayout.addWidget(startButton)
        
        stopButton = QPushButton("stop")
        stopButton.clicked.connect(self.stopButtonPressed)
        buttonLayout.addWidget(stopButton)
        
        clearButton = QPushButton("clear")
        clearButton.clicked.connect(self.strokes.clear)
        buttonLayout.addWidget(clearButton)
        
        saveButton = QPushButton("save")
        saveButton.clicked.connect(self.saveButtonPressed)
        buttonLayout.addWidget(saveButton)
        
        hideButton = QPushButton("hide")
        hideButton.clicked.connect(self.hide)
        buttonLayout.addWidget(hideButton)

        self.show()
    
        
    def on_keypress(self, key):
        try:
            ts = self.ts()
            self.strokes.append(f'{ts} - {key.char}')
        except AttributeError:
            self.strokes.append(f'{ts} - {str(key)}')
    
    def on_mouseclick(self, x, y, button, pressed):
        if pressed is None or pressed=="Released":
            return
        ts = time.strftime(r'%d/%m/%Y %H:%M:%S')
        self.strokes.append(f'{ts} - {button}')
        
    
    def clearButtonPressed(self):
        self.strokes.clear()
        self.statusLabel.setText('cleared history')
    
    def saveHist(self):
        if getattr(sys, 'frozen', False):
            filePath = Path(sys.executable).parent / 'logged_keys.txt'
        else:
            filePath = Path(__file__).parent.resolve() / 'logged_keys.txt'

        try:
            with open(filePath, 'a', encoding="utf-8") as f:
                f.write(f"\n\nnew save at {self.ts()}\n" + "\n".join(self.strokes))
        except:
            return
        self.strokes.clear()
        return filePath
            
    def startButtonPressed(self):
        if not self.keyboard_listener.running:
            self.keyboard_listener.start()
        if not self.mouse_listener.running:
            self.mouse_listener.start()
        self.statusLabel.setText("RECORDING")
            
    def stopButtonPressed(self):
        if self.keyboard_listener.running:
            self.keyboard_listener.stop()
            self.keyboard_listener = keyboard.Listener(on_press=self.on_keypress)
        if self.mouse_listener.running:
            self.mouse_listener.stop()
            self.mouse_listener = mouse.Listener(on_click=self.on_mouseclick)
        self.statusLabel.setText("NOT RECORDING")
        
    def saveButtonPressed(self):
        filePath = self.saveHist()
        if filePath is not None:
            self.savedLabel.setText(f'{self.ts()} - saved to {filePath}')
        else:
            self.savedLabel.setText(f'{self.ts()} - could not save to {filePath}')
    

    def closeEvent(self, event):
        if self.strokes!=[]:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "Unsaved Log",
                "You have unsaved keystrokes. Save before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                self.stopButtonPressed()
                self.saveButtonPressed()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                self.stopButtonPressed()
                event.accept()
            else:
                event.ignore()
        else:
            self.stopButtonPressed()
            event.accept()

    def ts(self):
        return time.strftime(r'%d/%m/%Y %H:%M:%S')
        

def main():
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL)
    app = QApplication([])
    app.setApplicationName("Keystroke Logger")
    app.setFont(QFont("Times", 15))
    win = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()