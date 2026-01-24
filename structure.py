import os

def create_documentation_structure(product_name, documentation_folder, chapters_count=20):
    """
    Создает структуру документации с нуля.
    
    :param product_name: Название продукта (например, WorkPlace)
    :param documentation_folder: Название директории документации (например, rp_vrm)
    :param chapters_count: Количество глав (по умолчанию 20)
    """
    base_path = f"basis/{product_name}/{documentation_folder}"
    
    # Создание основных директорий
    main_dirs = [
        f"{base_path}/chapters",
        f"{base_path}/media"
    ]
    for dir_path in main_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # Создание поддиректорий для медиа контента по номерам глав
    for i in range(1, chapters_count + 1):
        chapter_media_dir = f"{base_path}/media/{i}.chapter"
        os.makedirs(chapter_media_dir, exist_ok=True)
        
        # Создание файла .gitkeep для пустых папок
        gitkeep_path = f"{chapter_media_dir}/.gitkeep"
        with open(gitkeep_path, "w") as gitkeep_file:
            pass  # Файл создается пустым
    
    # Создание файлов глав
    for i in range(1, chapters_count + 1):
        chapter_file_path = f"{base_path}/chapters/{i}.chapter.adoc"
        with open(chapter_file_path, "w", encoding="utf-8") as chapter_file:
            chapter_file.write("")  # Создаем пустые файлы для глав
    
    # Создание основного файла документации main.adoc
    main_adoc_path = f"{base_path}/main.adoc"
    with open(main_adoc_path, "w", encoding="utf-8") as main_adoc:
        main_adoc.write(":sectnums:\n")
        main_adoc.write(":toc:\n\n")
        main_adoc.write("= Руководство пользователя\n\n")
        main_adoc.write("== Перечень включенных в документ глав\n\n")
        
        # Добавление include для каждой главы
        for i in range(1, chapters_count + 1):
            main_adoc.write(f"include::{{chapter-dir}}/{i}.chapter.adoc[]\n")
        
        # Добавление приложений
        main_adoc.write("\n== Приложения\n\n")
        main_adoc.write(".<<Файл конфигурации среды функционирования Бэкенда Базис.vControl>>\n")
        main_adoc.write(".<<Система управления базой данных>>\n")
        main_adoc.write(".<<Конфигурация развёртывания Базис.vControl>>\n\n")
        
        # Включение файлов приложений
        appendix_files = ["1.appendix.adoc", "2.appendix.adoc", "3.appendix.adoc"]
        for appendix_file in appendix_files:
            main_adoc.write(f"include::{appendix_file}[]\n")

# Настройка параметров
product_name = "WorkPlace"  # Замените на нужное название продукта
documentation_folder = "rp_vrm"  # Замените на нужную директорию документации

# Вызов функции для создания структуры
create_documentation_structure(product_name, documentation_folder)

print("Структура документации успешно создана!")