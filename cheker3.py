import os
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFileDialog, QTextEdit, QLineEdit,
    QTabWidget, QMessageBox
)

class AsciiDocChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout_main = QVBoxLayout()
        self.tabs = QTabWidget()
        self.layout_main.addWidget(self.tabs)

        # Вкладка 1: Проверка файла (можно вставить ваш функционал)
        self.tab_file_check = QWidget()
        layout_file_check = QVBoxLayout()

        self.file_input = QLineEdit()
        self.browse_button = QPushButton("Обзор")
        self.browse_button.clicked.connect(self.browse_file)
        layout_file_check.addWidget(QLabel("Выберите файл для проверки:"))
        layout_file_check.addWidget(self.file_input)
        layout_file_check.addWidget(self.browse_button)

        self.check_button = QPushButton("Проверить и исправить файл")
        self.check_button.clicked.connect(self.check_file)
        layout_file_check.addWidget(self.check_button)

        self.errors_output = QTextEdit()
        self.errors_output.setReadOnly(True)
        layout_file_check.addWidget(QLabel("Результаты проверки и исправлений:"))
        layout_file_check.addWidget(self.errors_output)

        self.tab_file_check.setLayout(layout_file_check)
        self.tabs.addTab(self.tab_file_check, "Проверка файла")

        # Вкладка 2: Пользователи — отдельно
        self.tab_users = QWidget()
        layout_users = QVBoxLayout()

        layout_users.addWidget(QLabel("Введите текст для замены *Пользователи* → `+Пользователи+`:"))

        self.users_text_edit = QTextEdit()
        layout_users.addWidget(self.users_text_edit)

        self.replace_button = QPushButton("Выполнить замену для *Пользователи*")
        self.replace_button.clicked.connect(self.replace_users)
        layout_users.addWidget(self.replace_button)

        self.result_text_edit = QTextEdit()
        self.result_text_edit.setReadOnly(True)
        layout_users.addWidget(QLabel("Результат после замены:"))
        layout_users.addWidget(self.result_text_edit)

        self.tab_users.setLayout(layout_users)
        self.tabs.addTab(self.tab_users, "*Пользователи*")  # Название вкладки с точной звездочкой

        self.setLayout(self.layout_main)
        self.setWindowTitle("Проверка и исправление AsciiDoc-файлов")

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "AsciiDoc Files (*.adoc);;All Files (*)")
        if file_path:
            self.file_input.setText(file_path)

    def check_file(self):
        # Ваш существующий код проверки файла, здесь заглушка
        self.errors_output.setText("Функция проверки файла не реализована в этом примере.")

    def replace_users(self):
        # Заменяем ТОЛЬКО в тексте вкладки *Пользователи*
        text = self.users_text_edit.toPlainText()
        if not text:
            QMessageBox.warning(self, "Внимание", "Текст для замены пуст.")
            return

        # Замена строго '*Пользователи*' на '`+Пользователи+`'
        new_text, count = re.subn(r'\*Пользователи\*', r'`+Пользователи+`', text)

        if count == 0:
            QMessageBox.information(self, "Результат", "Совпадений для замены не найдено.")
            self.result_text_edit.setPlainText(text)
        else:
            self.result_text_edit.setPlainText(new_text)
            QMessageBox.information(self, "Результат", f"Выполнено {count} замена(замен).")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = AsciiDocChecker()
    window.resize(600, 600)
    window.show()
    sys.exit(app.exec())

