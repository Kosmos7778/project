import os
import re
import time
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFileDialog, QTextEdit, QLineEdit,
    QHBoxLayout, QCheckBox, QProgressBar, QListWidget,
    QListWidgetItem, QGroupBox, QTabWidget, QPushButton,
    QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class WorkerThread(QThread):
    """Поток для обработки файлов"""
    progress = pyqtSignal(int)
    file_processed = pyqtSignal(str, dict)
    finished = pyqtSignal(dict)
    
    def __init__(self, file_paths, options):
        super().__init__()
        self.file_paths = file_paths
        self.options = options
        
    def run(self):
        total_files = len(self.file_paths)
        results = {
            'processed': 0,
            'fixed': 0,
            'warnings': 0,
            'errors': 0,
            'files': []
        }
        
        for idx, file_path in enumerate(self.file_paths):
            try:
                file_result = self.process_file(file_path)
                results['files'].append(file_result)
                
                if file_result['changes'] > 0:
                    results['fixed'] += 1
                if file_result['warnings'] > 0:
                    results['warnings'] += file_result['warnings']
                
                results['processed'] += 1
                
                # Отправляем прогресс
                progress = int((idx + 1) / total_files * 100)
                self.progress.emit(progress)
                self.file_processed.emit(file_path, file_result)
                
            except Exception as e:
                results['errors'] += 1
                error_result = {
                    'file': file_path,
                    'error': str(e),
                    'changes': 0,
                    'warnings': 0,
                    'report': []
                }
                results['files'].append(error_result)
                self.file_processed.emit(file_path, error_result)
        
        self.finished.emit(results)
    
    def process_file(self, file_path):
        """Обработка одного файла"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        report = []
        warnings = []
        changes_count = 0
        
        # 1. Исправление заголовков
        if self.options['fix_headers']:
            def fix_html_headers(match):
                nonlocal changes_count
                tag = match.group(1)
                text = match.group(2)
                level = {'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5, 'h6': 6}.get(tag.lower(), 1)
                changes_count += 1
                return f"{'#' * level} {text}"
            
            content_before = content
            content = re.sub(r'<(h[1-6])>(.*?)</\1>', fix_html_headers, content, flags=re.IGNORECASE)
            if content != content_before:
                report.append("✓ Исправлены HTML-заголовки на Markdown")
        
        # 2. Исправление путей изображений
        if self.options['fix_images']:
            image_fixes = 0
            def fix_image_paths(match):
                nonlocal image_fixes
                alt_text = match.group(1)
                path = match.group(2)
                
                if path.startswith('../images/') or path.startswith('./images/'):
                    new_path = path.replace('../images/', '_images/').replace('./images/', '_images/')
                    image_fixes += 1
                    return f'![{alt_text}]({new_path})'
                return match.group(0)
            
            content_before = content
            content = re.sub(r'!\[(.*?)\]\((.*?)\)', fix_image_paths, content)
            if image_fixes > 0:
                report.append(f"✓ Исправлено {image_fixes} путей к изображениям")
        
        # 3. Удаление лишних пустых строк
        if self.options['fix_blank_lines']:
            content_before = content
            content, n_removed = re.subn(r'\n{3,}', '\n\n', content)
            if n_removed > 0:
                report.append(f"✓ Удалено {n_removed} блоков лишних пустых строк")
        
        # 4. Исправление переносов строк
        if self.options['fix_line_endings']:
            content_before = content
            content, n_subs = re.subn(r'\r\n', '\n', content)
            if n_subs > 0:
                report.append(f"✓ Исправлено {n_subs} Windows-переносов строк")
        
        # 5. Удаление пробелов в конце строк
        if self.options['fix_trailing_spaces']:
            content_before = content
            content, n_spaces = re.subn(r'[ \t]+\n', '\n', content)
            if n_spaces > 0:
                report.append(f"✓ Удалено {n_spaces} пробелов в конце строк")
        
        # 6. Добавление пустой строки после заголовков
        if self.options['add_line_after_header']:
            lines = content.splitlines()
            fixed_lines = []
            headers_fixed = 0
            
            for i, line in enumerate(lines):
                fixed_lines.append(line)
                
                if re.match(r'^#{1,6}\s+', line):
                    if i + 1 < len(lines) and lines[i + 1].strip() != '':
                        fixed_lines.append('')
                        headers_fixed += 1
            
            if headers_fixed > 0:
                content = "\n".join(fixed_lines)
                report.append(f"✓ Добавлено {headers_fixed} пустых строк после заголовков")
        
        # 7. Проверка ссылок
        broken_links = re.findall(r'\[.*?\]\(.*?\)', content)
        for link in broken_links:
            if ']()' in link or '](#' in link:
                warnings.append(f"Возможная битая ссылка: {link[:50]}...")
        
        # 8. Проверка HTML-тегов
        html_tags = re.findall(r'<(?!br|hr|img|a\b)[a-zA-Z][^>]*>', content)
        if html_tags:
            warnings.append(f"Найдено {len(html_tags)} HTML-тегов (рекомендуется Markdown)")
        
        # 9. Проверка изображений
        image_pattern = r'!\[(.*?)\]\((.*?)\)(?:\{([^}]+)\})?'
        images = re.finditer(image_pattern, content)
        
        for match in images:
            alt_text, path, attributes = match.groups()
            
            if not alt_text.strip():
                warnings.append(f"Пустой alt-текст у изображения: {path}")
            
            if attributes:
                if not re.match(r'^(width=\d+|height=\d+|\s*)*$', attributes):
                    warnings.append(f"Некорректные атрибуты у изображения: {path}")
        
        # 10. Записываем изменения
        if content != original_content:
            backup_path = file_path + '.bak'
            with open(backup_path, 'w', encoding='utf-8') as backup:
                backup.write(original_content)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        
        # Подсчет измененных строк
        original_lines = original_content.splitlines()
        new_lines = content.splitlines()
        changes = sum(1 for i, j in zip(original_lines, new_lines) if i != j)
        
        return {
            'file': file_path,
            'changes': changes,
            'warnings': len(warnings),
            'report': report,
            'warnings_list': warnings,
            'fixed': content != original_content
        }


class YFMChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.file_paths = []
        self.worker = None
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Разделитель для двух панелей
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель: управление
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # 1. Выбор файлов
        files_group = QGroupBox("Файлы для проверки")
        files_layout = QVBoxLayout()
        
        # Кнопки управления файлами
        btn_layout = QHBoxLayout()
        self.add_files_btn = QPushButton("📄 Добавить файлы")
        self.add_files_btn.clicked.connect(self.add_files)
        self.add_folder_btn = QPushButton("📁 Добавить папку")
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.clear_btn = QPushButton("🗑️ Очистить список")
        self.clear_btn.clicked.connect(self.clear_files)
        
        btn_layout.addWidget(self.add_files_btn)
        btn_layout.addWidget(self.add_folder_btn)
        btn_layout.addWidget(self.clear_btn)
        
        files_layout.addLayout(btn_layout)
        
        # Список файлов
        self.files_list = QListWidget()
        self.files_list.setMinimumHeight(150)
        files_layout.addWidget(self.files_list)
        
        # Статистика файлов
        self.files_stats = QLabel("Файлов не выбрано")
        files_layout.addWidget(self.files_stats)
        
        files_group.setLayout(files_layout)
        left_layout.addWidget(files_group)
        
        # 2. Опции проверки
        options_group = QGroupBox("Опции проверки")
        options_layout = QVBoxLayout()
        
        self.fix_headers_cb = QCheckBox("Исправлять заголовки (h1 → #, h2 → ##)")
        self.fix_headers_cb.setChecked(True)
        options_layout.addWidget(self.fix_headers_cb)
        
        self.fix_images_cb = QCheckBox("Исправлять пути изображений")
        self.fix_images_cb.setChecked(True)
        options_layout.addWidget(self.fix_images_cb)
        
        self.fix_blank_lines_cb = QCheckBox("Удалять лишние пустые строки")
        self.fix_blank_lines_cb.setChecked(True)
        options_layout.addWidget(self.fix_blank_lines_cb)
        
        self.fix_line_endings_cb = QCheckBox("Исправлять переносы строк")
        self.fix_line_endings_cb.setChecked(True)
        options_layout.addWidget(self.fix_line_endings_cb)
        
        self.fix_trailing_spaces_cb = QCheckBox("Удалять пробелы в конце строк")
        self.fix_trailing_spaces_cb.setChecked(True)
        options_layout.addWidget(self.fix_trailing_spaces_cb)
        
        self.add_line_after_header_cb = QCheckBox("Добавлять пустую строку после заголовков")
        self.add_line_after_header_cb.setChecked(True)
        options_layout.addWidget(self.add_line_after_header_cb)
        
        options_group.setLayout(options_layout)
        left_layout.addWidget(options_group)
        
        # 3. Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        # 4. Кнопки действий
        action_layout = QHBoxLayout()
        self.check_btn = QPushButton("✅ Начать проверку")
        self.check_btn.clicked.connect(self.start_check)
        self.check_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        
        self.cancel_btn = QPushButton("❌ Отменить")
        self.cancel_btn.clicked.connect(self.cancel_check)
        self.cancel_btn.setEnabled(False)
        
        action_layout.addWidget(self.check_btn)
        action_layout.addWidget(self.cancel_btn)
        left_layout.addLayout(action_layout)
        
        left_panel.setLayout(left_layout)
        
        # Правая панель: результаты
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Вкладки для результатов
        self.tabs = QTabWidget()
        
        # Вкладка 1: Общие результаты
        self.results_tab = QWidget()
        results_layout = QVBoxLayout()
        
        self.summary_label = QLabel("Результаты проверки появятся здесь")
        self.summary_label.setWordWrap(True)
        results_layout.addWidget(self.summary_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        results_layout.addWidget(self.details_text)
        
        self.results_tab.setLayout(results_layout)
        self.tabs.addTab(self.results_tab, "📊 Результаты")
        
        # Вкладка 2: Детали по файлам
        self.files_tab = QWidget()
        files_tab_layout = QVBoxLayout()
        
        self.files_details = QTextEdit()
        self.files_details.setReadOnly(True)
        files_tab_layout.addWidget(self.files_details)
        
        self.files_tab.setLayout(files_tab_layout)
        self.tabs.addTab(self.files_tab, "📄 Детали файлов")
        
        # Вкладка 3: Статистика
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        self.stats_tab.setLayout(stats_layout)
        self.tabs.addTab(self.stats_tab, "📈 Статистика")
        
        right_layout.addWidget(self.tabs)
        right_panel.setLayout(right_layout)
        
        # Добавляем панели в разделитель
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        self.setWindowTitle("YFM Multi-File Checker")
        self.resize(1200, 700)
    
    def add_files(self):
        """Добавить отдельные файлы"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Выберите файлы", "", 
            "Markdown Files (*.md);;All Files (*.*)"
        )
        
        for file_path in files:
            if file_path not in self.file_paths:
                self.file_paths.append(file_path)
                item = QListWidgetItem(os.path.basename(file_path))
                item.setToolTip(file_path)
                self.files_list.addItem(item)
        
        self.update_stats()
    
    def add_folder(self):
        """Добавить все файлы из папки"""
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith('.md'):
                        file_path = os.path.join(root, file)
                        if file_path not in self.file_paths:
                            self.file_paths.append(file_path)
                            rel_path = os.path.relpath(file_path, folder)
                            item = QListWidgetItem(rel_path)
                            item.setToolTip(file_path)
                            self.files_list.addItem(item)
        
        self.update_stats()
    
    def clear_files(self):
        """Очистить список файлов"""
        self.file_paths.clear()
        self.files_list.clear()
        self.update_stats()
    
    def update_stats(self):
        """Обновить статистику файлов"""
        count = len(self.file_paths)
        if count == 0:
            self.files_stats.setText("Файлов не выбрано")
        else:
            total_size = sum(os.path.getsize(f) for f in self.file_paths) / 1024
            self.files_stats.setText(f"Выбрано файлов: {count} ({total_size:.1f} KB)")
    
    def start_check(self):
        """Начать проверку выбранных файлов"""
        if not self.file_paths:
            QMessageBox.warning(self, "Ошибка", "Выберите файлы для проверки")
            return
        
        # Получаем опции
        options = {
            'fix_headers': self.fix_headers_cb.isChecked(),
            'fix_images': self.fix_images_cb.isChecked(),
            'fix_blank_lines': self.fix_blank_lines_cb.isChecked(),
            'fix_line_endings': self.fix_line_endings_cb.isChecked(),
            'fix_trailing_spaces': self.fix_trailing_spaces_cb.isChecked(),
            'add_line_after_header': self.add_line_after_header_cb.isChecked()
        }
        
        # Настраиваем интерфейс
        self.check_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Очищаем результаты
        self.summary_label.setText("⏳ Начинаю проверку файлов...")
        self.details_text.clear()
        self.files_details.clear()
        self.stats_text.clear()
        
        # Создаем и запускаем поток
        self.worker = WorkerThread(self.file_paths, options)
        self.worker.progress.connect(self.update_progress)
        self.worker.file_processed.connect(self.add_file_result)
        self.worker.finished.connect(self.on_check_finished)
        self.worker.start()
    
    def cancel_check(self):
        """Отменить проверку"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.summary_label.setText("❌ Проверка отменена пользователем")
            self.reset_ui()
    
    def update_progress(self, value):
        """Обновить прогресс-бар"""
        self.progress_bar.setValue(value)
    
    def add_file_result(self, file_path, result):
        """Добавить результат обработки файла"""
        filename = os.path.basename(file_path)
        
        if 'error' in result:
            text = f"❌ {filename}: ОШИБКА - {result['error']}\n"
            self.details_text.append(text)
        else:
            if result['changes'] > 0:
                text = f"✅ {filename}: Исправлено {result['changes']} строк"
                if result['warnings'] > 0:
                    text += f" (+{result['warnings']} предупреждений)"
            else:
                text = f"✓ {filename}: Без изменений"
                if result['warnings'] > 0:
                    text += f" ({result['warnings']} предупреждений)"
            
            self.details_text.append(text)
            
            # Добавляем детали для вкладки файлов
            file_details = f"\n{'='*60}\n📄 Файл: {filename}\n"
            file_details += f"📁 Путь: {file_path}\n"
            
            if result['report']:
                file_details += "\n📝 Исправления:\n"
                for item in result['report']:
                    file_details += f"  • {item}\n"
            
            if result['warnings_list']:
                file_details += f"\n⚠ Предупреждения ({result['warnings']}):\n"
                for warning in result['warnings_list'][:10]:  # Показываем первые 10
                    file_details += f"  • {warning}\n"
                if len(result['warnings_list']) > 10:
                    file_details += f"  • ... и ещё {len(result['warnings_list']) - 10} предупреждений\n"
            
            self.files_details.append(file_details)
    
    def on_check_finished(self, results):
        """Обработка завершения проверки"""
        self.reset_ui()
        
        # Общая статистика
        total_time = results.get('time', 0)
        
        summary = f"✅ ПРОВЕРКА ЗАВЕРШЕНА\n\n"
        summary += f"📊 СТАТИСТИКА:\n"
        summary += f"• Обработано файлов: {results['processed']}\n"
        summary += f"• Исправлено файлов: {results['fixed']}\n"
        summary += f"• Найдено предупреждений: {results['warnings']}\n"
        summary += f"• Ошибок обработки: {results['errors']}\n"
        
        if total_time > 0:
            summary += f"• Время выполнения: {total_time:.2f} сек\n"
        
        self.summary_label.setText(summary)
        
        # Детальная статистика
        stats_text = "📈 ДЕТАЛЬНАЯ СТАТИСТИКА\n\n"
        
        # Распределение по типам файлов
        folders = {}
        for file_path in self.file_paths:
            folder = os.path.dirname(file_path)
            folders[folder] = folders.get(folder, 0) + 1
        
        if folders:
            stats_text += "📁 ФАЙЛЫ ПО ПАПКАМ:\n"
            for folder, count in sorted(folders.items(), key=lambda x: x[1], reverse=True)[:10]:
                stats_text += f"  {folder}: {count} файлов\n"
        
        # Топ файлов с изменениями
        changed_files = [f for f in results['files'] if f.get('changes', 0) > 0]
        if changed_files:
            stats_text += "\n🏆 ТОП ФАЙЛОВ ПО ИЗМЕНЕНИЯМ:\n"
            for file_result in sorted(changed_files, key=lambda x: x['changes'], reverse=True)[:5]:
                name = os.path.basename(file_result['file'])
                stats_text += f"  {name}: {file_result['changes']} изменений\n"
        
        # Предупреждения по типам
        warning_types = {}
        for file_result in results['files']:
            for warning in file_result.get('warnings_list', []):
                # Извлекаем тип предупреждения
                if "ссылка" in warning.lower():
                    warning_types['Битые ссылки'] = warning_types.get('Битые ссылки', 0) + 1
                elif "html" in warning.lower():
                    warning_types['HTML теги'] = warning_types.get('HTML теги', 0) + 1
                elif "изображен" in warning.lower():
                    warning_types['Изображения'] = warning_types.get('Изображения', 0) + 1
                else:
                    warning_types['Прочие'] = warning_types.get('Прочие', 0) + 1
        
        if warning_types:
            stats_text += "\n⚠ ПРЕДУПРЕЖДЕНИЯ ПО ТИПАМ:\n"
            for wtype, count in sorted(warning_types.items(), key=lambda x: x[1], reverse=True):
                stats_text += f"  {wtype}: {count}\n"
        
        self.stats_text.setText(stats_text)
    
    def reset_ui(self):
        """Сбросить UI после завершения"""
        self.check_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)


def main():
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = YFMChecker()
    window.show()
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем (Ctrl+C)")
        sys.exit(0)


if __name__ == "__main__":
    main()