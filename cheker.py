import os
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit, QLineEdit
)

class AsciiDocChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Основной layout
        layout = QVBoxLayout()

        # Поля для выбора файла и директории
        self.file_label = QLabel("Выберите файл для проверки:")
        self.file_input = QLineEdit()
        self.browse_button = QPushButton("Обзор")
        self.browse_button.clicked.connect(self.browse_file)
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_input)
        layout.addWidget(self.browse_button)

        # Кнопка для запуска проверки
        self.check_button = QPushButton("Проверить файл")
        self.check_button.clicked.connect(self.check_file)
        layout.addWidget(self.check_button)

        # Поле для вывода ошибок
        self.errors_label = QLabel("Результаты проверки:")
        self.errors_output = QTextEdit()
        self.errors_output.setReadOnly(True)
        layout.addWidget(self.errors_label)
        layout.addWidget(self.errors_output)

        # Настройка окна
        self.setLayout(layout)
        self.setWindowTitle("Проверка Asciidoc-файлов")

    def browse_file(self):
        """Открывает диалог выбора файла."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "AsciiDoc Files (*.adoc);;All Files (*)")
        if file_path:
            self.file_input.setText(file_path)

    def check_file(self):
        """Проверяет выбранный файл на соответствие регламенту."""
        file_path = self.file_input.text().strip()
        if not file_path or not os.path.exists(file_path):
            self.errors_output.setText("Ошибка: Файл не выбран или не существует.")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Список проверок
            errors = []

            # 1. Проверка заголовков нужного уровня
            if re.search(r'^=.*$', content, re.MULTILINE):  # Заголовок уровня 1 недопустим
                errors.append("Ошибка: Найден заголовок уровня 1 (=). Используйте == для глав.")

            if re.search(r'^={5,}.*$', content, re.MULTILINE):  # Более 4 знаков '=' недопустимо
                errors.append("Ошибка: Найден заголовок с более чем 4 знаками '='.")

            # 2. Проверка отсутствия лишних переносов строк
            if re.search(r'\n\n\n+', content):  # Более двух подряд идущих пустых строк
                errors.append("Ошибка: Найдено более двух подряд идущих пустых строк.")

            # 3. Проверка пробелов перед новой строкой
            if re.search(r' \n', content):  # Пробел перед переносом строки
                errors.append("Ошибка: Найдены пробелы перед новой строкой.")

            # 4. Проверка использования только Linux-переносов строк
            if re.search(r'\r\n', content):  # Windows-переносы строк (\r\n)
                errors.append("Ошибка: Использованы Windows-переносы строк. Используйте Linux (\n).")

            # 5. Проверка наличия пустых строк после заголовков
            if re.search(r'^={2,}.*$\n[^ ]', content, re.MULTILINE):  # После заголовка нет пустой строки
                errors.append("Ошибка: После заголовков должен быть хотя бы один пустой символ.")

            # 6. Проверка оформления таблиц
            if not re.search(r'\|===.*?\|===', content, re.DOTALL):  # Неправильная структура таблицы
                errors.append("Ошибка: Таблицы должны начинаться и заканчиваться |===")

            # 7. Проверка ссылок на рисунки
            if re.search(r'<<fig_[a-zA-Z0-9_]+>>', content) and not re.search(r'\[\[fig_[a-zA-Z0-9_]+\]\]', content):
                errors.append("Ошибка: Для каждой ссылки на рисунок должна быть определена метка [[fig_...]].")

            # 8. Проверка форматирования inline-элементов
            if re.search(r'btn:\[[^\]]+\]', content):  # Проверка кнопок
                pass  # Если найдены корректные btn:[название], то всё хорошо
            else:
                errors.append("Ошибка: Найдены неправильно оформленные кнопки. Используйте btn:[название].")

            if re.search(r'<[^>]+>', content):  # Проверка клавиш
                pass  # Если найдены корректные <Enter>, то всё хорошо
            else:
                errors.append("Ошибка: Найдены неправильно оформленные клавиши. Используйте <Enter>.")

            # 9. Проверка блоков кода
            if not re.search(r'\[source,[a-z]+\]\n----.*?----', content, re.DOTALL):
                errors.append("Ошибка: Блоки кода должны быть оформлены как [source,language]\n----\nкод\n----")

            # 10. Проверка примечаний, советов и предупреждений
            for block_type in ["NOTE", "TIP", "WARNING", "IMPORTANT", "CAUTION"]:
                if re.search(fr'\[{block_type}\]\n====.*?====', content, re.DOTALL):
                    pass  # Если найдены корректные блоки, то всё хорошо
                else:
                    errors.append(f"Ошибка: Найдены неправильно оформленные блоки [{block_type}].")

            # 11. Проверка правильности имён рисунков
            if re.search(r'image::.*?\.png\[width=\d+\]', content):
                pass  # Если найдены корректные image::..., то всё хорошо
            else:
                errors.append("Ошибка: Рисунки должны быть указаны как image::путь/к/рисунку.png[width=число]")

            # Вывод результатов
            if errors:
                self.errors_output.setText("\n".join(errors))
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
    sys.exit(app.exec())