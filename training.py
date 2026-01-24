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

    # Раздел 1: Именование веток в GIT
    git_branch_naming_content = (
        "В данном разделе описываются правила именования веток в GIT.\n"
        "Пример: feature/новая-функция, bugfix/исправление-ошибки."
    )
    git_branch_naming_animation = [
        "Шаг 1: Создайте новую ветку с префиксом 'feature/'.",
        "Шаг 2: Используйте дефисы вместо пробелов.",
        "Шаг 3: Добавьте описание функционала после префикса.",
    ]
    document += generate_section("Именование веток в GIT", git_branch_naming_content, git_branch_naming_animation)

    # Раздел 2: Выстраивание структуры документа в GIT
    git_structure_content = (
        "Структура проекта должна быть четко определена.\n"
        "Пример:\nsource/\ndocs/\nimages/\nREADME.adoc\n"
        "basis/WorkPlace/rp_vrm/chapters/\nbasis/WorkPlace/rp_vrm/media/"
    )
    git_structure_animation = [
        "Шаг 1: Создайте корневой каталог 'source'.",
        "Шаг 2: Добавьте подкаталог 'docs' для документации.",
        "Шаг 3: Включите папку 'images' для хранения изображений.",
        "Шаг 4: Создайте директорию для глав (chapters).",
    ]
    document += generate_section("Выстраивание структуры документа в GIT", git_structure_content, git_structure_animation)

    # Раздел 3: Текст в asciidoc
    asciidoc_text_content = (
        "AsciiDoc позволяет форматировать текст с использованием простых маркеров.\n"
        "Пример:\n*Жирный текст*\n_Курсив_\n`Код`\n\n"
        "Рекомендуется придерживаться правила 1 предложение = 1 строка."
    )
    asciidoc_text_animation = [
        "Шаг 1: Используйте звездочки для жирного текста.",
        "Шаг 2: Используйте нижние подчеркивания для курсива.",
        "Шаг 3: Используйте обратные кавычки для оформления кода.",
    ]
    document += generate_section("Текст в asciidoc", asciidoc_text_content, asciidoc_text_animation)

    # Раздел 4: Таблицы
    tables_content = (
        "Пример таблицы:\n\n"
        "[width=\"100%\",cols=\"35%,65%\",options=\"header\"]\n"
        "|===\n"
        "| Параметр | Пример\n"
        "| *Хост* | 10.0.30.9:389\n"
        "| *Base DN* | DC=sk,DC=local\n"
        "|===\n"
    )
    tables_animation = [
        "Шаг 1: Укажите ширину таблицы и колонки с помощью параметров width и cols.",
        "Шаг 2: Добавьте заголовок таблицы с помощью options=\"header\".",
        "Шаг 3: Заполните содержимое таблицы с помощью символа '|'.",
    ]
    document += generate_section("Таблицы", tables_content, tables_animation)

    # Раздел 5: Рисунки
    images_content = (
        "Пример рисунка:\n\n"
        ".Автоматическая разметка диска. Шаг 2\n"
        "image::path/to/image.png[width=500]\n\n"
        "Для inline-рисунков используйте:\n\n"
        "image:../media/pic/кнопка_удалить.png[width=25]"
    )
    images_animation = [
        "Шаг 1: Сохраните изображение в папке media с расширением .png.",
        "Шаг 2: Используйте точку перед названием рисунка для добавления подписи.",
        "Шаг 3: Укажите путь к изображению и размер с помощью параметра width.",
    ]
    document += generate_section("Рисунки", images_content, images_animation)

    # Раздел 6: Ссылки в документе
    links_content = (
        "Пример внешней ссылки:\n\n"
        "https://example.com[Название ссылки]\n\n"
        "Пример внутренней ссылки:\n\n"
        "<<sec_example,Перейти к разделу>>"
    )
    links_animation = [
        "Шаг 1: Для внешних ссылок используйте URL и необязательное название.",
        "Шаг 2: Для внутренних ссылок используйте двойные угловые скобки <<...>>.",
    ]
    document += generate_section("Ссылки в документе", links_content, links_animation)

    # Раздел 7: Оформление блока кода
    code_block_content = (
        "Пример блока кода JSON:\n\n"
        "[source,json]\n"
        "----\n"
        "{\n"
        '  "key": "value"\n'
        "}\n"
        "----\n\n"
        "Пример блока кода YAML:\n\n"
        "[source,yaml]\n"
        "----\n"
        "key: value\n"
        "----"
    )
    code_block_animation = [
        "Шаг 1: Укажите тип кода с помощью параметра source.",
        "Шаг 2: Оберните код в теги ---- для создания блока.",
    ]
    document += generate_section("Оформление блока кода", code_block_content, code_block_animation)

    # Сохранение документа
    with open("document.adoc", "w", encoding="utf-8") as file:
        file.write(document)
    print("AsciiDoc-документ успешно создан!")


if __name__ == "__main__":
    main()