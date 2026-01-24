import os
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFileDialog, QTextEdit, QLineEdit
)


class AsciiDocChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.file_label = QLabel("Выберите файл для проверки:")
        self.file_input = QLineEdit()
        self.browse_button = QPushButton("Обзор")
        self.browse_button.clicked.connect(self.browse_file)

        layout.addWidget(self.file_label)
        layout.addWidget(self.file_input)
        layout.addWidget(self.browse_button)

        self.check_button = QPushButton("Проверить и исправить файл")
        self.check_button.clicked.connect(self.check_file)
        layout.addWidget(self.check_button)

        self.errors_label = QLabel("Результаты проверки и исправлений:")
        self.errors_output = QTextEdit()
        self.errors_output.setReadOnly(True)

        layout.addWidget(self.errors_label)
        layout.addWidget(self.errors_output)

        self.setLayout(layout)
        self.setWindowTitle("Проверка и исправление AsciiDoc-файлов")

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "AsciiDoc Files (*.adoc);;All Files (*)")
        if file_path:
            self.file_input.setText(file_path)

    def check_file(self):
        file_path = self.file_input.text().strip()
        if not file_path or not os.path.exists(file_path):
            self.errors_output.setText("Ошибка: Файл не выбран или не существует.")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            original_content = content
            report = []

            # 1. Исправляем заголовки уровня 1 (=) на ==
            def fix_headers(line):
                if re.match(r'^=[^=].*', line):
                    fixed_line = '==' + line[1:]
                    report.append("Исправлен заголовок уровня 1 (=) на уровень 2 (==).")
                    return fixed_line
                return line

            lines = content.splitlines()
            new_lines = [fix_headers(line) for line in lines]
            content = "\n".join(new_lines)

            # 2. Удаляем более двух подряд идущих пустых строк (оставляем максимум две)
            def fix_blank_lines(match):
                report.append("Удалены лишние подряд идущие пустые строки.")
                return '\n\n'

            content_before = content
            content = re.sub(r'\n{3,}', fix_blank_lines, content)
            if content != content_before:
                pass  # отчет уже добавлен в fix_blank_lines

            # 3. Удаляем пробелы перед переносом строки
            content, n_subs_space = re.subn(r' +\n', '\n', content)
            if n_subs_space > 0:
                report.append(f"Удалено {n_subs_space} пробелов перед новой строкой.")

            # 4. Приводим переносы строк к Linux (\n)
            content, n_subs_crlf = re.subn(r'\r\n', '\n', content)
            if n_subs_crlf > 0:
                report.append(f"Заменено {n_subs_crlf} Windows-переносов строк на Linux (\\n).")

            # 5. Добавляем пустую строку после заголовков (== и выше), если её нет
            lines = content.splitlines()
            fixed_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                fixed_lines.append(line)
                if re.match(r'^={2,} ', line) or re.match(r'^={2,}$', line):
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if next_line.strip() != '':
                            fixed_lines.append('')
                            report.append(f"Добавлена пустая строка после заголовка: {line.strip()}")
                    else:
                        pass
                i += 1
            content = "\n".join(fixed_lines)

            # 7. Исправляем кнопки: разные варианты button:[...] / button[...] -> btn:[...]
            content_before = content
            content = re.sub(r'\bbutton:\[([^\]]+)\]', r'btn:[\1]', content)
            content = re.sub(r'\bbutton\[(.+?)\]', r'btn:[\1]', content)
            if content != content_before:
                report.append("Исправлены неправильно оформленные кнопки на btn:[название].")

            # 8. Исправляем клавиши на <Enter>
            content_before = content
            content = re.sub(r'<[eE][nN][tT][eE][rR]>', r'<Enter>', content)
            if content != content_before:
                report.append("Исправлены неправильно оформленные клавиши (замена на <Enter>).")

            # 9. Форматируем блоки кода: добавляем [source,plaintext] если отсутствует [source,...] перед ----
            lines = content.splitlines()
            fixed_lines = []
            i = 0
            code_blocks_fixed = False
            while i < len(lines):
                line = lines[i]
                if line.strip() == '----':
                    if i == 0 or not re.match(r'\[source,[a-zA-Z]+\]', lines[i - 1]):
                        fixed_lines.append('[source,plaintext]')
                        fixed_lines.append('----')
                        code_blocks_fixed = True
                        i += 1
                        while i < len(lines) and lines[i].strip() != '----':
                            fixed_lines.append(lines[i])
                            i += 1
                        if i < len(lines):
                            fixed_lines.append('----')
                            i += 1
                        continue
                    else:
                        fixed_lines.append(line)
                        i += 1
                else:
                    fixed_lines.append(line)
                    i += 1
            content_after_code_fix = "\n".join(fixed_lines)
            if code_blocks_fixed:
                report.append("Автоматически оформлены блоки кода как [source,plaintext].")
                content = content_after_code_fix

            # Записываем исправленный файл, если есть изменения
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.errors_output.setText("Ошибки найдены и исправлены:\n" + "\n".join(report))
            else:
                self.errors_output.setText("Файл соответствует регламенту. Ошибок не найдено.")

        except Exception as e:
            self.errors_output.setText(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = AsciiDocChecker()
    window.resize(600, 400)
    window.show()
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем (Ctrl+C).")
        sys.exit(0)
