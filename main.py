import pyautogui
import keyboard
from screeninfo import get_monitors
import matplotlib.pyplot as plt
import tkinter as tk
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtGui
import sys
from functools import partial
import re
import threading

monitors = []

monitor_is_selected = False
monitor_selected = ""
monitor_assignments = []


class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.radios = {}
        self.buttons = {}
        self.labels = {}

        # set the title
        self.setWindowTitle("Label")

        # setting  the geometry of window
        self.setGeometry(0, 0, 400, 300)

        self.label_1 = QLabel('Monitor Switch', self)
        self.label_1.resize(300, 30)
        self.label_1.move(15, 15)
        self.label_1.setFont(QFont('Times', 25))

        self.label_2 = QLabel('Quick and easy way to switch monitors', self)
        self.label_2.resize(300, 20)
        self.label_2.move(15, 45)
        self.label_2.setFont(QFont('Times', 10))

        self.reset_button = QPushButton(
            'Reset Configuration', self)
        self.reset_button.resize(120, 30)
        self.reset_button.move(15, 70)
        self.reset_button.clicked.connect(self.reset)

        self.reset_button = QPushButton(
            'Identify Monitor', self)
        self.reset_button.resize(120, 30)
        self.reset_button.move(15, 100)
        self.reset_button.clicked.connect(identify_monitor)

        for iteration, m in enumerate(monitors):
            self.radios[iteration] = QRadioButton(
                "Monitor " + str(iteration + 1), self)
            self.radios[iteration].move(15, 130 + iteration * 20)
            self.radios[iteration].toggled.connect(
                lambda:
                    self.radio_state()
            )

            self.labels[iteration] = QLabel(
                "(unassigned) id:" + str(iteration + 1), self)
            self.pal = self.labels[iteration].palette()
            self.pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor("red"))
            self.labels[iteration].setPalette(self.pal)
            self.labels[iteration].resize(140, 30)
            self.labels[iteration].move(90, 130 + iteration * 20)

            self.buttons[iteration] = QPushButton(
                "CTRL + " + str(iteration + 1), self)
            self.buttons[iteration].setEnabled(monitor_is_selected)
            self.buttons[iteration].move(220, 137 + iteration * 20)
            self.buttons[iteration].resize(75, 17)
            self.buttons[iteration].clicked.connect(self.btn_state)

        self.show()

    def radio_state(self):
        for key, value in self.radios.items():
            if value.isChecked():
                text = value.text()
                global monitor_is_selected
                global monitor_selected

                if monitor_is_selected == False:

                    monitor_is_selected = True

                    for btn_key, btn_value in self.buttons.items():
                        btn_value.setEnabled(monitor_is_selected)

                monitor_selected = text

    def btn_state(self):
        for key, value in self.buttons.items():
            if value == self.sender():
                global monitor_is_selected

                if monitor_is_selected == True:

                    for label_key, label_value in self.labels.items():
                        global monitor_selected

                        formatted_label_text = label_value.text()
                        if "(assigned)" in label_value.text():
                            formatted_label_text = formatted_label_text[formatted_label_text.find(
                                '(assigned)'):]

                        label_text = re.sub('\D', '', formatted_label_text)
                        btn_text = re.sub('\D', '', value.text())
                        monitor_text = re.sub('\D', '', monitor_selected)

                        if (label_text == monitor_text):
                            global monitor_assignments

                            if "(assigned)" in label_value.text():
                                for idx, x in enumerate(monitor_assignments):
                                    for button_key, button_value in self.buttons.items():
                                        if x['key'] in button_value.text():
                                            button_value.setEnabled(True)
                                            del monitor_assignments[idx]
                                            break
                                    break

                            self.pal = label_value.palette()
                            self.pal.setColor(
                                QtGui.QPalette.WindowText, QtGui.QColor("green"))
                            label_value.setPalette(self.pal)

                            label_value.setText(
                                "CTRL + " + btn_text + " (assigned) id:" + label_text)

                            monitor_assignments.append({
                                "id": label_text,
                                "key": btn_text
                            })

                            value.setEnabled(False)

    def reset(self):
        global monitor_is_selected
        global monitor_selected

        monitor_is_selected = False
        monitor_selected = ""

        for label_key, label_value in self.labels.items():
            label_value.setText("(unassigned) id:" + str(label_key + 1))

            self.pal = label_value.palette()
            self.pal.setColor(
                QtGui.QPalette.WindowText, QtGui.QColor("red"))
            label_value.setPalette(self.pal)

        for key, value in self.buttons.items():
            value.setEnabled(True)

        global monitor_assignments
        monitor_assignments = []


def append_monitors():
    for m in get_monitors():
        monitors.append({"width": m.width / 2 + m.x, "height": m.height / 2})


def identify_monitor():
    global monitor_selected

    monitor_x = 99999999
    for mid, m in enumerate(get_monitors()):
        if str(mid + 1) in monitor_selected:
            monitor_x = m.x

    root = tk.Tk()
    root.wm_overrideredirect(True)
    root.attributes('-alpha', 0.5)
    root.geometry(("{0}x{1}+" + str(monitor_x) + "+0").format(root.winfo_screenwidth(),
                                                              root.winfo_screenheight()))
    root.bind("<Button-1>", lambda evt: root.destroy())

    l = tk.Label(text=monitor_selected, font=("Helvetica", 60))
    l.pack(expand=True)

    root.mainloop()


def hotkey_listen():
    while True:
        for m in monitor_assignments:
            if keyboard.is_pressed('ctrl+' + str(m['key'])):
                pyautogui.moveTo(
                    monitors[int(m['id']) - 1]['width'], monitors[int(m['id']) - 1]['height'])


def config_monitors():

    App = QApplication(sys.argv)

    # create the instance of our Window
    window = Window()

    # start the app
    App.exec()


def main():
    append_monitors()
    th = threading.Thread(target=hotkey_listen)
    th.start()
    config_monitors()


if __name__ == '__main__':
    main()
