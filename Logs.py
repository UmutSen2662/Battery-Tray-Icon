import sys
import json
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
)


class LogWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table Demo")
        self.setGeometry(100, 100, 400, 750)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel("Battery Charge Logs")
        self.title_label.setAlignment(Qt.AlignCenter)  # Use Qt.AlignCenter from PySide6.QtCore
        self.layout.addWidget(self.title_label)
        # Set the title font
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete Selected")
        self.save_exit_button = QPushButton("Save and Exit")
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.save_exit_button)
        self.layout.addLayout(self.button_layout)

        self.load_logs()

        self.delete_button.clicked.connect(self.delete_selected)
        self.save_exit_button.clicked.connect(self.save_and_exit)
        self.delete_button.setStyleSheet("padding: 8px 16px;")
        self.save_exit_button.setStyleSheet("padding: 8px 16px;")

    def load_logs(self):
        try:
            with open("Log.json") as file:
                data = json.load(file)
                percents = data["percent"]
                times = data["time"]
                times = [str(datetime.fromtimestamp(x)) for x in times]
                times = [(x[:10] + "  " + x[-9:-3]) for x in times]

                self.table.setRowCount(len(times))
                self.table.setColumnCount(2)
                self.table.setHorizontalHeaderLabels(["Time", "Percent"])
                self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

                for row, (time, percent) in enumerate(zip(times, percents)):
                    item_time = QTableWidgetItem(time)
                    item_percent = QTableWidgetItem(str(percent))

                    # Disable editing for both items
                    item_time.setFlags(item_time.flags() & ~Qt.ItemIsEditable)
                    item_percent.setFlags(item_percent.flags() & ~Qt.ItemIsEditable)

                    self.table.setItem(row, 0, item_time)
                    self.table.setItem(row, 1, item_percent)

                self.data = data
        except FileNotFoundError:
            self.data = {"time": [], "percent": []}
            self.table.setRowCount(0)
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["Time", "Percent"])
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def delete_selected(self):
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)
        for row in selected_rows:
            self.table.removeRow(row)
            self.data["time"].pop(row)
            self.data["percent"].pop(row)

    def save_and_exit(self):
        print("Saved")
        with open("Log.json", "w") as file:
            json.dump(self.data, file)
        self.close()


def show_logs():
    app = QApplication(sys.argv)

    # Set the global font
    global_font = QFont()
    global_font.setPointSize(12)
    app.setFont(global_font)

    window = LogWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    show_logs()
