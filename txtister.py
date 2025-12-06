import os
import re

def is_binary(file_path):
    """
    Проверяет, является ли файл бинарным.
    Читает первые 1024 байта. Если встречается нулевой байт, считает файл бинарным.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return True
    except Exception:
        return True # Если не удалось прочитать, считаем подозрительным
    return False

def clean_hex_arrays(content):
    """
    Ищет в тексте большие массивы hex-данных (как в C/C++)
    и заменяет их тело на комментарий.
    Например: { 0x00, 0x01 ... } -> { /* ... HEX DATA HIDDEN ... */ }
    """
    # Паттерн ищет конструкцию вида = { ... }; где внутри много hex-чисел
    # (?s) включает режим "точка совпадает с переносом строки"
    # Мы ищем фигурные скобки, внутри которых много цифр, 'x', запятых и пробелов (более 50 символов)
    pattern = r'(=\s*\{[\s\da-fA-FxX,]{50,}?\};)'
    
    # Функция замены
    def replacer(match):
        # Оставляем начало и конец, но скрываем внутренности
        return '= { /* ... LARGE HEX ARRAY HIDDEN ... */ };'

    return re.sub(pattern, replacer, content, flags=re.DOTALL)

def find_and_write_files(root_folder, output_file):
    try:
        script_path = os.path.realpath(__file__)
        output_file_path = os.path.realpath(output_file)
        
        # Добавил .lib, .obj, .dll, .exe, .pdb, .bin и другие бинарники
        excluded_extensions = (
            '.sln', '.vcxproj', '.filters', '.user', 
            '.lib', '.obj', '.dll', '.exe', '.pdb', '.suo', 
            '.ncb', '.bin', '.iso', '.png', '.jpg'
        )
        
        size_limit = 100 * 1024  # 100 КБ

        with open(output_file, 'w', encoding='utf-8') as outfile:
            for dirpath, _, filenames in os.walk(root_folder):
                for filename in filenames:
                    # 1. Фильтр по расширению
                    if filename.lower().endswith(excluded_extensions):
                        continue

                    file_path = os.path.join(dirpath, filename)
                    real_file_path = os.path.realpath(file_path)

                    if real_file_path == script_path or real_file_path == output_file_path:
                        continue

                    try:
                        file_size = os.path.getsize(file_path)

                        # 2. Фильтр по размеру
                        if file_size > size_limit:
                            # Можно раскомментировать строку ниже, если хотите видеть пропущенные файлы в отчете
                            # outfile.write(f"{file_path}: [SKIP > 100KB]\n\n")
                            continue 

                        # 3. Проверка на бинарный файл (отсеивает .lib, если они прошли фильтр расширений, и прочий мусор)
                        if is_binary(file_path):
                            # outfile.write(f"{file_path}: [SKIP BINARY]\n\n")
                            continue

                        # Запись заголовка
                        outfile.write(f"{file_path}:\n")
                        outfile.write("-" * len(file_path) + "\n")

                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                            content = infile.read()
                            
                            # 4. Очистка длинных hex-массивов
                            content = clean_hex_arrays(content)
                            
                            outfile.write(f"{content}\n\n")
                            
                    except (IOError, OSError) as e:
                        outfile.write(f"Ошибка чтения: {e}\n\n")

        print(f"Готово. Файлы записаны в {output_file}")

    except Exception as e:
        print(f"Критическая ошибка: {e}")

# --- НАСТРОЙКИ ---
folder_to_scan = '.'
output_filename = 'all.txt'

# --- ЗАПУСК ---
if __name__ == "__main__":
    find_and_write_files(folder_to_scan, output_filename)