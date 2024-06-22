import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QCheckBox
from PyQt5.QtCore import QFile, QTextStream, Qt
import json
import os
import platform

class TaskListApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task List App")
        self.setGeometry(100, 100, 400, 300)
        self.load_css("style.css")

        # Create a layout for the widgets
        layout = QVBoxLayout()

        # Create a line edit for entering task descriptions
        self.task_input = TaskLineEdit(self)
        layout.addWidget(self.task_input)

        # Create a button to add tasks
        add_button = QPushButton("Add Task")
        add_button.clicked.connect(self.add_task)
        layout.addWidget(add_button)

        # Create a list widget to display tasks
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)

        self.setLayout(layout)

        self.load_tasks() # Load tasks

    def load_css(self, filename):
        is_dark_theme = self.is_dark_theme()
        stylesheet_file = "style-dark.css" if is_dark_theme else "style-light.css"
        stylesheet = QFile(stylesheet_file)
        if stylesheet.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(stylesheet)
            QApplication.instance().setStyleSheet(stream.readAll())
    
    def is_dark_theme(self):
        # Detect dark theme for Windows
        if platform.system() == "Windows":
            import winreg
            try:
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return value == 0
            except:
                return False
    
    def closeEvent(self, event):
        self.save_tasks()
        event.accept()

    def add_task(self):
        # Get the task description from the input field
        task_description = self.task_input.text()

        if task_description:
            # Create a QListWidgetItem with a checkbox
            task_item = QListWidgetItem()
            task_item.setFlags(task_item.flags() | 2)  # Add ItemIsUserCheckable flag

            # Create a checkbox and set it as an item widget
            task_checkbox = QCheckBox(task_description)
            task_checkbox.setCheckState(0)  # Set the initial state of the checkbox (Unchecked)
            task_item.setSizeHint(task_checkbox.sizeHint())
            self.task_list.addItem(task_item)
            self.task_list.setItemWidget(task_item, task_checkbox)

            # Connect the checkbox to a slot for handling its state change
            task_checkbox.stateChanged.connect(self.mark_task_completed)

            # Clear the input field
            self.task_input.clear()
            
            # Save tasks to the file
            self.save_tasks()


    def mark_task_completed(self, state):
        # Handle task completion when the checkbox state changes
        sender_checkbox = self.sender()
        item = self.task_list.itemAt(sender_checkbox.pos())  # Get the item at the checkbox's position
        if item:
            # if state == 2:  # CheckState: Checked
            #     item.setHidden(True)  # Hide the completed task
            # else:
            #     item.setHidden(False)  # Show the task again
            # Save tasks to the file
            self.save_tasks()


    def save_tasks(self):
        tasks = []

        for index in range(self.task_list.count()):
            item = self.task_list.item(index)
            checkbox = self.task_list.itemWidget(item)
            tasks.append(
                {
                    'description': checkbox.text(),
                    'completed': checkbox.checkState() == 2
                })

        with open('tasks.json', 'w') as file:
            json.dump(tasks, file)


    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as file:
                tasks = json.load(file)
                for task in tasks:
                    task_item = QListWidgetItem()
                    task_item.setFlags(task_item.flags() | 2)  # Add ItemIsUserCheckable flag
                    task_checkbox = QCheckBox(task['description'])
                    task_checkbox.setCheckState(2 if task['completed'] else 0)
                    task_item.setSizeHint(task_checkbox.sizeHint())
                    self.task_list.addItem(task_item)
                    self.task_list.setItemWidget(task_item, task_checkbox)
                    task_checkbox.stateChanged.connect(self.mark_task_completed)
        except FileNotFoundError:
            pass





class TaskLineEdit(QLineEdit):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and self.text():
            self.parent.add_task()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskListApp()
    window.show()
    sys.exit(app.exec_())
