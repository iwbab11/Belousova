import os, sys, time, sqlite3
import serial, serial.tools.list_ports
from PyQt5 import QtCore, QtWidgets, uic

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "..", "..", "bin")
os.makedirs(BIN, exist_ok=True)

db = sqlite3.connect(os.path.join(BIN, "events.db"))
db.executescript("""
CREATE TABLE IF NOT EXISTS events (
id INTEGER PRIMARY KEY AUTOINCREMENT,
ts TEXT DEFAULT (datetime('now', 'localtime')),
event_type TEXT NOT NULL,
description TEXT,
mode TEXT);
CREATE TABLE IF NOT EXISTS measurements (
id INTEGER PRIMARY KEY AUTOINCREMENT,
ts TEXT DEFAULT (datetime('now', 'localtime')),
mode TEXT, gate TEXT, distance INTEGER,
temperature REAL, humidity REAL, light INTEGER, status TEXT);
""")

TEXT = {
    "OK": "норма",
    "NO_SIGNAL": "НЕИСПРАВНОСТЬ: нет сигнала датчика DHT11",
    "OVERHEAT": "НЕИСПРАВНОСТЬ: перегрев, автоматика отключена",
    "OPEN": "шлагбаум открыт", "CLOSED": "шлагбаум закрыт",
    "DAY": "день, подсветка выключена", "NIGHT": "ночь, подсветка включена"
}

def num(s):
    return None if s == "nan" else float(s)

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(HERE, "gate.ui"), self)
        self.ser = None
        self.mode = "MANUAL"
        self.prev = {}
        self.last_save = 0
        self.comboPort.addItems([p.device for p in serial.tools.list_ports.comports()])
        self.btnConnect.clicked.connect(self.connect_port)
        self.btnManual.clicked.connect(lambda: self.send("M", "MODE", "ручной режим"))
        self.btnAuto.clicked.connect(lambda: self.send("A", "MODE", "автоматический режим"))
        self.btnOpen.clicked.connect(lambda: self.manual("O", "открыть шлагбаум"))
        self.btnClose.clicked.connect(lambda: self.manual("C", "закрыть шлагбаум"))
        self.btnTest.clicked.connect(lambda: self.send("T", "DIAG", "запуск самопроверки"))
        self.btnReset.clicked.connect(lambda: self.send("R", "RESTORE", "сброс: ручной режим"))
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(100)
        self.show_log()

    def add_event(self, event_type, description):
        db.execute("INSERT INTO events(event_type, description, mode) VALUES (?, ?, ?)",
                   (event_type, description, self.mode))
        db.commit()
        self.show_log()

    def show_log(self):
        self.listLog.clear()
        for ts, et, desc in db.execute("SELECT ts, event_type, description FROM events "
                                       "ORDER BY id DESC LIMIT 20"):
            self.listLog.addItem(f"{ts} {et:<8} {desc}")

    def connect_port(self):
        try:
            self.ser = serial.Serial(self.comboPort.currentText(), 9600, timeout=1)
        except serial.SerialException as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка", str(e))
            return
        self.add_event("CONNECT", "подключение к " + self.comboPort.currentText())

    def send(self, cmd, event_type, description):
        if not self.ser:
            QtWidgets.QMessageBox.warning(self, "Нет связи", "Сначала подключитесь к Arduino")
            return
        self.ser.write((cmd + "\n").encode())
        if cmd in ("A", "M", "R"):
            self.mode = "AUTO" if cmd == "A" else "MANUAL"
        self.add_event(event_type, description)

    def manual(self, cmd, description):
        if self.mode == "AUTO":
            QtWidgets.QMessageBox.information(self, "Автоматический режим", "Открывать и закрывать вручную - в ручном режиме")
            return
        self.send(cmd, "CMD", description)

    def poll(self):
        while self.ser and self.ser.in_waiting:
            p = self.ser.readline().decode(errors="ignore").strip().split(";")
            if p[0] == "DATA" and len(p) == 9:
                self.show_data(*p[1:])
            elif p[0] == "TEST" and len(p) == 3:
                self.add_event("DIAG", f"{p[1]}: {p[2]}")

    def show_data(self, mode, gate, dist, t, h, light, day, status):
        self.mode = mode
        self.labelData.setText(f"Режим: {mode} {TEXT[gate].capitalize()}"
                               f"До автомобиля: {dist} см\n"
                               f"Температура: {t} C Влажность: {h}"
                               f"Освещенность: {light} ({TEXT[day]})")
        self.labelState.setText("Состояние: " + TEXT[status])
        self.labelState.setStyleSheet("color: green" if status == "OK" else "color: red")
        for key, value in (("status", status), ("gate", gate), ("day", day)):
            old = self.prev.get(key)
            self.prev[key] = value
            if old == value:
                continue
            if key != "status":
                self.add_event(value, TEXT[value])
            elif value != "OK":
                self.add_event("FAULT", TEXT[value])
            elif old is not None:
                self.add_event("RESTORE", "работоспособность восстановлена")
        if time.time() - self.last_save >= 5:
            db.execute("INSERT INTO measurements(mode, gate, distance, temperature, humidity," \
            "light, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (mode, gate, int(dist), num(t), num(h), int(light), status))
            db.commit()
            self.last_save = time.time()

app = QtWidgets.QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())