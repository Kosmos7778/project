import os
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFileDialog, QTextEdit, QLineEdit,
    QHBoxLayout, QCheckBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class YFMChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()

        # 1. Выбор файла
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Файл для проверки:")
        self.file_input = QLineEdit()
        self.browse_button = QPushButton("📂 Обзор")
        self.browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_input, stretch=1)
        file_layout.addWidget(self.browse_button)
        layout.addLayout(file_layout)

        # 2. Опции проверки
        self.options_label = QLabel("Опции проверки:")
        layout.addWidget(self.options_label)
        
        self.fix_headers_cb = QCheckBox("Исправлять заголовки (h1 → #, h2 → ##)")
        self.fix_headers_cb.setChecked(True)
        layout.addWidget(self.fix_headers_cb)
        
        self.fix_images_cb = QCheckBox("Исправлять пути изображений")
        self.fix_images_cb.setChecked(True)
        layout.addWidget(self.fix_images_cb)
        
        self.fix_blank_lines_cb = QCheckBox("Удалять лишние пустые строки")
        self.fix_blank_lines_cb.setChecked(True)
        layout.addWidget(self.fix_blank_lines_cb)
        
        self.fix_line_endings_cb = QCheckBox("Исправлять переносы строк")
        self.fix_line_endings_cb.setChecked(True)
        layout.addWidget(self.fix_line_endings_cb)
        
        self.fix_trailing_spaces_cb = QCheckBox("Удалять пробелы в конце строк")
        self.fix_trailing_spaces_cb.setChecked(True)
        layout.addWidget(self.fix_trailing_spaces_cb)
        
        self.add_line_after_header_cb = QCheckBox("Добавлять пустую строку после заголовков")
        self.add_line_after_header_cb.setChecked(True)
        layout.addWidget(self.add_line_after_header_cb)

        # 3. Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 4. Кнопка проверки
        self.check_button = QPushButton("✅ Проверить и исправить файл")
        self.check_button.clicked.connect(self.check_file)
        layout.addWidget(self.check_button)

        # 5. Результаты
        self.results_label = QLabel("Результаты проверки:")
        layout.addWidget(self.results_label)
        
        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)
        layout.addWidget(self.results_output)

        # 6. Статистика
        self.stats_label = QLabel("")
        layout.addWidget(self.stats_label)

        self.setLayout(layout)
        self.setWindowTitle("YFM Markdown Checker")
        self.resize(800, 600)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл", "", 
            "Markdown Files (*.md);;All Files (*.*)"
        )
        if file_path:
            self.file_input.setText(file_path)

    def check_file(self):
        file_path = self.file_input.text().strip()
        if not file_path or not os.path.exists(file_path):
            self.results_output.setText("❌ Ошибка: Файл не выбран или не существует.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            original_content = content
            report = []
            fixes_count = 0

            # Прогресс: чтение файла
            self.progress_bar.setValue(10)

            # 1. Исправление заголовков (если включено)
            if self.fix_headers_cb.isChecked():
                self.progress_bar.setValue(20)
                
                # Исправляем h1 → #, h2 → ## и т.д. (HTML теги на Markdown)
                def fix_html_headers(match):
                    nonlocal fixes_count
                    tag = match.group(1)
                    text = match.group(2)
                    level = {'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5, 'h6': 6}.get(tag.lower(), 1)
                    fixes_count += 1
                    return f"{'#' * level} {text}"
                
                content_before = content
                content = re.sub(r'<(h[1-6])>(.*?)</\1>', fix_html_headers, content, flags=re.IGNORECASE)
                if content != content_before:
                    report.append(f"✓ Исправлено {fixes_count} HTML-заголовков на Markdown")

            # 2. Исправление путей изображений (если включено)
            if self.fix_images_cb.isChecked():
                self.progress_bar.setValue(30)
                
                # Находим и исправляем неправильные пути к изображениям
                image_fixes = 0
                
                # Вариант 1: ![текст](путь)
                def fix_image_paths(match):
                    nonlocal image_fixes
                    alt_text = match.group(1)
                    path = match.group(2)
                    
                    # Если путь начинается с неправильного префикса
                    if path.startswith('../images/') or path.startswith('./images/'):
                        # Меняем на стандартный путь для YFM
                        new_path = path.replace('../images/', '_images/').replace('./images/', '_images/')
                        image_fixes += 1
                        return f'![{alt_text}]({new_path})'
                    return match.group(0)
                
                content_before = content
                content = re.sub(r'!\[(.*?)\]\((.*?)\)', fix_image_paths, content)
                
                if image_fixes > 0:
                    report.append(f"✓ Исправлено {image_fixes} путей к изображениям")

            # 3. Удаление лишних пустых строк (если включено)
            if self.fix_blank_lines_cb.isChecked():
                self.progress_bar.setValue(40)
                
                # Удаляем более двух подряд идущих пустых строк
                content_before = content
                content, n_removed = re.subn(r'\n{3,}', '\n\n', content)
                if n_removed > 0:
                    report.append(f"✓ Удалено {n_removed} блоков лишних пустых строк")

            # 4. Исправление переносов строк (если включено)
            if self.fix_line_endings_cb.isChecked():
                self.progress_bar.setValue(50)
                
                # Приводим переносы строк к Unix формату (\n)
                content_before = content
                content, n_subs = re.subn(r'\r\n', '\n', content)
                if n_subs > 0:
                    report.append(f"✓ Исправлено {n_subs} Windows-переносов строк на Unix")

            # 5. Удаление пробелов в конце строк (если включено)
            if self.fix_trailing_spaces_cb.isChecked():
                self.progress_bar.setValue(60)
                
                # Удаляем пробелы перед переносом строки
                content_before = content
                content, n_spaces = re.subn(r'[ \t]+\n', '\n', content)
                if n_spaces > 0:
                    report.append(f"✓ Удалено {n_spaces} пробелов в конце строк")

            # 6. Добавление пустой строки после заголовков (если включено)
            if self.add_line_after_header_cb.isChecked():
                self.progress_bar.setValue(70)
                
                lines = content.splitlines()
                fixed_lines = []
                headers_fixed = 0
                
                for i, line in enumerate(lines):
                    fixed_lines.append(line)
                    
                    # Проверяем, является ли строка заголовком Markdown (# ## ### и т.д.)
                    if re.match(r'^#{1,6}\s+', line):
                        # Если следующая строка не пустая и существует
                        if i + 1 < len(lines) and lines[i + 1].strip() != '':
                            fixed_lines.append('')
                            headers_fixed += 1
                
                if headers_fixed > 0:
                    content = "\n".join(fixed_lines)
                    report.append(f"✓ Добавлено {headers_fixed} пустых строк после заголовков")

            # 7. Дополнительные проверки для YFM
            self.progress_bar.setValue(80)
            
            # Проверяем наличие некорректных ссылок
            broken_links = re.findall(r'\[.*?\]\(.*?\)', content)
            link_warnings = []
            for link in broken_links:
                # Проверяем на пустые или подозрительные ссылки
                if ']()' in link or '](#' in link:
                    link_warnings.append(f"Возможная битая ссылка: {link[:50]}...")
            
            # Проверяем на использование HTML-тегов (кроме разрешённых)
            html_tags = re.findall(r'<(?!br|hr|img|a\b)[a-zA-Z][^>]*>', content)
            if html_tags:
                report.append(f"⚠ Найдено {len(html_tags)} HTML-тегов (рекомендуется использовать Markdown)")

            # 8. Проверка разметки изображений с атрибутами
            self.progress_bar.setValue(90)
            
            # Проверяем правильность разметки изображений с размерами {width=... height=...}
            image_errors = []
            image_pattern = r'!\[(.*?)\]\((.*?)\)(?:\{([^}]+)\})?'
            images = re.finditer(image_pattern, content)
            
            for match in images:
                alt_text, path, attributes = match.groups()
                
                # Проверка 1: Пустой alt-текст
                if not alt_text.strip():
                    image_errors.append(f"Пустой alt-текст у изображения: {path}")
                
                # Проверка 2: Некорректные атрибуты
                if attributes:
                    if not re.match(r'^(width=\d+|height=\d+|\s*)*$', attributes):
                        image_errors.append(f"Некорректные атрибуты у изображения {path}: {attributes}")
            
            if image_errors:
                report.append(f"⚠ Найдено {len(image_errors)} проблем с разметкой изображений")

            # Прогресс: завершение
            self.progress_bar.setValue(100)

            # 9. Записываем исправленный файл, если есть изменения
            if content != original_content:
                backup_path = file_path + '.bak'
                with open(backup_path, 'w', encoding='utf-8') as backup:
                    backup.write(original_content)
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                changes_count = sum(1 for i, j in zip(original_content.splitlines(), content.splitlines()) if i != j)
                
                report_text = "✅ Файл проверен и исправлен:\n\n"
                report_text += "Исправления:\n" + "\n".join(f"• {item}" for item in report if item.startswith('✓'))
                
                if link_warnings:
                    report_text += "\n\n⚠ Предупреждения:\n" + "\n".join(f"• {warn}" for warn in link_warnings[:5])
                    if len(link_warnings) > 5:
                        report_text += f"\n• ... и ещё {len(link_warnings) - 5} предупреждений"
                
                if image_errors:
                    report_text += "\n\n⚠ Проблемы с изображениями:\n" + "\n".join(f"• {err}" for err in image_errors[:3])
                    if len(image_errors) > 3:
                        report_text += f"\n• ... и ещё {len(image_errors) - 3} проблем"
                
                report_text += f"\n\n📊 Статистика:\n"
                report_text += f"• Изменено строк: {changes_count}\n"
                report_text += f"• Резервная копия: {os.path.basename(backup_path)}\n"
                report_text += f"• Размер файла: {os.path.getsize(file_path) / 1024:.1f} KB"
                
                self.results_output.setText(report_text)
                self.stats_label.setText(f"🔄 Изменено: {changes_count} строк | 💾 Резервная копия создана")
                
            else:
                self.results_output.setText("✅ Файл соответствует стандартам YFM Markdown. Ошибок не найдено.")
                self.stats_label.setText("✓ Файл проверен, изменений не требуется")

        except Exception as e:
            self.results_output.setText(f"❌ Критическая ошибка:\n{str(e)}")
            self.stats_label.setText("✗ Ошибка при обработке файла")
        finally:
            self.progress_bar.setVisible(False)


def main():
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Современный стиль
    
    window = YFMChecker()
    window.show()
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем (Ctrl+C)")
        sys.exit(0)


if __name__ == "__main__":
    main()