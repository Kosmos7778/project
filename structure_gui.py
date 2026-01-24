import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QCheckBox, QSpinBox
)

class DocumentationCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Создание структуры документации")
        
        # Главный layout
        layout = QVBoxLayout()

        # Ввод названия главной директории
        self.root_dir_label = QLabel("Название главной директории:")
        self.root_dir_input = QLineEdit("root")  # По умолчанию "root"
        layout.addWidget(self.root_dir_label)
        layout.addWidget(self.root_dir_input)

        # Ввод названия продукта
        self.product_name_label = QLabel("Название продукта:")
        self.product_name_input = QLineEdit()
        layout.addWidget(self.product_name_label)
        layout.addWidget(self.product_name_input)

        # Ввод директории документации
        self.doc_dir_label = QLabel("Директория документации:")
        self.doc_dir_input = QLineEdit()
        self.browse_button = QPushButton("Обзор")
        self.browse_button.clicked.connect(self.browse_directory)
        layout.addWidget(self.doc_dir_label)
        layout.addWidget(self.doc_dir_input)
        layout.addWidget(self.browse_button)

        # Ввод количества глав
        self.chapters_count_label = QLabel("Количество глав:")
        self.chapters_count_input = QSpinBox()
        self.chapters_count_input.setMinimum(1)
        self.chapters_count_input.setMaximum(100)
        self.chapters_count_input.setValue(20)  # Значение по умолчанию
        layout.addWidget(self.chapters_count_label)
        layout.addWidget(self.chapters_count_input)

        # Ввод количества приложений
        self.appendix_count_label = QLabel("Количество приложений:")
        self.appendix_count_input = QSpinBox()
        self.appendix_count_input.setMinimum(0)
        self.appendix_count_input.setMaximum(20)
        self.appendix_count_input.setValue(3)  # Значение по умолчанию
        layout.addWidget(self.appendix_count_label)
        layout.addWidget(self.appendix_count_input)

        # Чекбокс для создания приложений
        self.create_appendix_checkbox = QCheckBox("Создать приложения (appendix)")
        layout.addWidget(self.create_appendix_checkbox)

        # Кнопка создания документации
        self.create_button = QPushButton("Создать документацию")
        self.create_button.clicked.connect(self.create_documentation)
        layout.addWidget(self.create_button)

        # Установка layout
        self.setLayout(layout)

    def browse_directory(self):
        """Открывает диалог выбора директории."""
        directory = QFileDialog.getExistingDirectory(self, "Выберите директорию")
        if directory:
            self.doc_dir_input.setText(directory)

    def create_documentation(self):
        """Создает структуру документации с учетом параметров."""
        root_dir = self.root_dir_input.text().strip()  # Название главной директории
        product_name = self.product_name_input.text().strip()
        doc_dir = self.doc_dir_input.text().strip()
        chapters_count = self.chapters_count_input.value()
        appendix_count = self.appendix_count_input.value()
        create_appendix = self.create_appendix_checkbox.isChecked()

        # Проверка введенных данных
        if not root_dir:
            self.show_message("Ошибка", "Введите название главной директории.")
            return
        if not product_name:
            self.show_message("Ошибка", "Введите название продукта.")
            return
        if not doc_dir:
            self.show_message("Ошибка", "Выберите директорию документации.")
            return

        # Создание структуры документации
        try:
            self.generate_structure(root_dir, product_name, doc_dir, chapters_count, appendix_count, create_appendix)
            self.show_message("Успех", "Структура документации успешно создана!")
        except Exception as e:
            self.show_message("Ошибка", f"Произошла ошибка: {str(e)}")

    def generate_structure(self, root_dir, product_name, doc_dir, chapters_count, appendix_count=0, create_appendix=False):
        """
        Генерирует структуру документации.

        :param root_dir: Название главной директории.
        :param product_name: Название продукта.
        :param doc_dir: Директория для документации.
        :param chapters_count: Количество глав.
        :param appendix_count: Количество приложений.
        :param create_appendix: Флаг для создания приложений.
        """
        base_path = os.path.join(doc_dir, root_dir, product_name, "documentation")
        os.makedirs(base_path, exist_ok=True)

        # Создание основных директорий
        main_dirs = [
            os.path.join(base_path, "chapters"),
            os.path.join(base_path, "media")
        ]
        for dir_path in main_dirs:
            os.makedirs(dir_path, exist_ok=True)

        # Создание поддиректорий для медиа контента по номерам глав
        for i in range(1, chapters_count + 1):
            chapter_media_dir = os.path.join(base_path, "media", f"{i}.chapter")
            os.makedirs(chapter_media_dir, exist_ok=True)
            
            # Создание файла .gitkeep для пустых папок
            gitkeep_path = os.path.join(chapter_media_dir, ".gitkeep")
            with open(gitkeep_path, "w") as gitkeep_file:
                pass  # Файл создается пустым

        # Создание файлов глав
        for i in range(1, chapters_count + 1):
            chapter_file_path = os.path.join(base_path, "chapters", f"{i}.chapter.adoc")
            with open(chapter_file_path, "w", encoding="utf-8") as chapter_file:
                chapter_file.write("")  # Создаем пустые файлы для глав

        # Создание приложений, если выбрано
        if create_appendix and appendix_count > 0:
            appendix_dir = os.path.join(base_path, "appendix")
            os.makedirs(appendix_dir, exist_ok=True)

            # Создание файлов приложений
            for i in range(1, appendix_count + 1):
                appendix_file_path = os.path.join(appendix_dir, f"{i}.appendix.adoc")
                with open(appendix_file_path, "w", encoding="utf-8") as appendix_file:
                    appendix_file.write(f"== Приложение {i}\n\n")

            # Создание карты приложений appendix.adoc
            appendix_map_path = os.path.join(base_path, "appendix.adoc")
            with open(appendix_map_path, "w", encoding="utf-8") as appendix_map:
                appendix_map.write(":appendix-number: 0\n:sectnums:\n:toc:\n\n")
                appendix_map.write("== Приложения\n\n")
                for i in range(1, appendix_count + 1):
                    appendix_map.write(f".<<Приложение_{i}>>\n")
                    appendix_map.write(f"include::{i}.appendix.adoc[]\n")

        # Создание основного файла документации main.adoc
        main_adoc_path = os.path.join(base_path, "main.adoc")
        with open(main_adoc_path, "w", encoding="utf-8") as main_adoc:
            main_adoc.write(":sectnums:\n")
            main_adoc.write(":toc:\n\n")
            main_adoc.write("= Руководство пользователя\n\n")
            main_adoc.write("== Перечень включенных в документ глав\n\n")
            
            # Добавление include для каждой главы
            for i in range(1, chapters_count + 1):
                main_adoc.write(f"include::{{chapter-dir}}/{i}.chapter.adoc[]\n")
            
            # Если выбрано создание приложений
            if create_appendix and appendix_count > 0:
                main_adoc.write("\n== Приложения\n\n")
                main_adoc.write("include::appendix.adoc[]\n")

    def show_message(self, title, message):
        """Показывает сообщение пользователю."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = DocumentationCreator()
    window.resize(400, 350)
    window.show()
    sys.exit(app.exec())