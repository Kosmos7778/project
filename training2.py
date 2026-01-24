import os  # Для работы с файловой системой
import json  # Для сохранения данных в формате JSON

def generate_asciidoc_toc(toc_entries):
    """Генерирует Table of Contents для AsciiDoc."""
    toc = "= Содержание\n:toc:\n:toc-title: Содержание\n\n"
    for i, entry in enumerate(toc_entries, start=1):
        toc += f"{i}. {entry['title']} ......................................................................................... {entry['page']}\n"
    return toc + "\n"

def generate_section(section_title, content, animation_steps=None):
    """Генерирует раздел с возможностью добавления анимации."""
    section = f"== {section_title}\n\n"
    if animation_steps:
        for step in animation_steps:
            section += f"[NOTE]\n====\n{step}\n====\n"
    section += content + "\n"
    return section

def main():
    # Table of Contents
    toc_entries = [
        {"title": "Структура ведения проекта", "page": 4},
        {"title": "Краткая структура продуктовых директорий", "page": 5},
        {"title": "Пояснения к схеме проекта", "page": 6},
        {"title": "Общие правила именования и создания файлов и каталогов", "page": 7},
        {"title": "Общие правила создания структуры Приложений", "page": 9},
        {"title": "Пустые папки в Git", "page": 10},
        {"title": "Полезные советы и сценарии", "page": 11},
        {"title": "Именование веток в GIT", "page": 4},
        {"title": "Выстраивание структуры документа в GIT", "page": 5},
        {"title": "Текст в asciidoc", "page": 7},
        {"title": "Главы", "page": 8},
        {"title": "Разделы", "page": 9},
        {"title": "Таблицы", "page": 10},
        {"title": "Рисунки", "page": 16},
        {"title": "Ссылки в документе", "page": 21},
        {"title": "Оформление блока кода", "page": 23},
        {"title": "Оформление кнопок в интерфейсе", "page": 25},
        {"title": "Оформление клавиш", "page": 26},
        {"title": "Оформление примечаний", "page": 27},
        {"title": "Оформление наименования разделов, вкладок и секций", "page": 28},
        {"title": "Оформление имен файлов и путей к файлам", "page": 29},
        {"title": "Приложения (appendix)", "page": 30},
        {"title": "Обозначения рисунков, таблиц, разделов", "page": 32},
    ]

    # Генерация TOC
    document = generate_asciidoc_toc(toc_entries)

    # Раздел 1: Структура ведения проекта
    project_structure_content = (
        "Структура ведения проекта — продукто-ориентированная, в соотношении 'один проект:много продуктов'.\n"
        "Путь к исходным текстам продуктовых документов начинается с брендового слова (basis)."
    )
    project_structure_animation = [
        "Шаг 1: Создайте корневую директорию 'basis'.",
        "Шаг 2: Для каждого продукта создайте поддиректорию (например, 'vControl', 'WorkPlace').",
        "Шаг 3: Внутри каждой поддиректории организуйте структуру: chapters, media, appendix."
    ]
    document += generate_section("Структура ведения проекта", project_structure_content, project_structure_animation)

    # Раздел 2: Краткая структура продуктовых директорий
    product_directories_content = (
        "Пример структуры:\n\n"
        "basis/\n"
        "├── vControl/\n"
        "│   ├── ra_upr/\n"
        "│   │   ├── chapters/\n"
        "│   │   ├── main.adoc\n"
        "│   │   └── media/\n"
        "├── WorkPlace/\n"
        "│   ├── rp_vrm/\n"
        "│   │   ├── chapters/\n"
        "│   │   ├── main.adoc\n"
        "│   │   └── media/\n"
    )
    product_directories_animation = [
        "Шаг 1: Создайте основную директорию 'basis'.",
        "Шаг 2: Для каждого продукта создайте поддиректорию (например, 'vControl', 'WorkPlace').",
        "Шаг 3: В каждой поддиректории создайте 'chapters' для глав, 'media' для медиафайлов и 'appendix' для приложений."
    ]
    document += generate_section("Краткая структура продуктовых директорий", product_directories_content, product_directories_animation)

    # Раздел 3: Пояснения к схеме проекта
    project_explanation_content = (
        "Основные правила:\n\n"
        "- Директория 'main.adoc' должна содержать карту документации.\n"
        "- Поддиректория 'chapters' используется для хранения файлов глав.\n"
        "- Поддиректория 'media' используется для хранения изображений.\n"
        "- Поддиректория 'appendix' используется для приложений.\n"
    )
    project_explanation_animation = [
        "Шаг 1: Создайте файл 'main.adoc' для структурирования документа.",
        "Шаг 2: Создайте поддиректорию 'chapters' и добавьте файлы глав (.chapter.adoc).",
        "Шаг 3: Создайте поддиректорию 'media' для хранения изображений.",
        "Шаг 4: Создайте поддиректорию 'appendix' для приложений."
    ]
    document += generate_section("Пояснения к схеме проекта", project_explanation_content, project_explanation_animation)

    # Раздел 4: Общие правила именования и создания файлов и каталогов
    naming_rules_content = (
        "Правила именования:\n\n"
        "- Директории продуктов должны соответствовать имени продукта.\n"
        "- Файлы глав должны называться согласно шаблону: номер_главы.chapter.adoc.\n"
        "- Изображения должны иметь формат .png и храниться в поддиректории 'media'."
    )
    naming_rules_animation = [
        "Шаг 1: Используйте осмысленные названия для директорий продуктов.",
        "Шаг 2: Называйте файлы глав в соответствии с шаблоном 'номер_главы.chapter.adoc'.",
        "Шаг 3: Храните изображения в поддиректории 'media' с расширением .png."
    ]
    document += generate_section("Общие правила именования и создания файлов и каталогов", naming_rules_content, naming_rules_animation)

    # Раздел 5: Общие правила создания структуры Приложений
    appendix_structure_content = (
        "Правила создания структуры приложений:\n\n"
        "- Создайте поддиректорию 'appendix' в директории разработки документации.\n"
        "- В начало каждого раздела приложений добавьте служебный атрибут [appendix]."
    )
    appendix_structure_animation = [
        "Шаг 1: Создайте поддиректорию 'appendix' для приложений.",
        "Шаг 2: В каждом файле приложений добавьте атрибут [appendix] для корректной нумерации."
    ]
    document += generate_section("Общие правила создания структуры Приложений", appendix_structure_content, appendix_structure_animation)

    # Раздел 6: Пустые папки в Git
    empty_folders_content = (
        "Если необходимо сохранить пустую директорию, создайте в ней файл .gitkeep.\n\n"
        "Пример: basis/WorkPlace/rp_vrm/media/1.chapter/.gitkeep"
    )
    empty_folders_animation = [
        "Шаг 1: Создайте пустую директорию, если она требуется для структуры проекта.",
        "Шаг 2: Внутри пустой директории создайте файл .gitkeep для отслеживания Git."
    ]
    document += generate_section("Пустые папки в Git", empty_folders_content, empty_folders_animation)

    # Сохранение документа
    output_file = "extended_document.adoc"
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(document)
    
    # Дополнительно: Сохранение TOC в JSON для дальнейшего использования
    toc_json_file = "toc.json"
    with open(toc_json_file, "w", encoding="utf-8") as json_file:
        json.dump(toc_entries, json_file, ensure_ascii=False, indent=4)

    print(f"AsciiDoc-документ успешно создан! ({output_file})")
    print(f"TOC сохранен в формате JSON! ({toc_json_file})")

if __name__ == "__main__":
    main()