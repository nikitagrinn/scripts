import os
import sys

def convert_file_to_utf8_bom(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    if not content:
        return False # Игнорируем пустые файлы

    # Проверка на наличие BOM
    has_bom = content.startswith(b'\xef\xbb\xbf')
    if has_bom:
        content = content[3:]
        
    # Попытка декодирования
    try:
        text = content.decode('utf-8')
        encoding_used = 'utf-8'
        # Если файл уже был utf-8 и у него уже был BOM, не перезаписываем зря
        if has_bom:
            return False 
    except UnicodeDecodeError:
        try:
            text = content.decode('cp1251')
            encoding_used = 'cp1251'
        except UnicodeDecodeError:
            try:
                text = content.decode('cp1252')
                encoding_used = 'cp1252'
            except UnicodeDecodeError:
                print(f"Skipping {file_path}: unknown encoding")
                return False
                
    # Нормализация переносов строк (Опционально. Если не хотите менять - закомментируйте)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
                
    tmp_file_path = file_path + ".tmp"
    try:
        # БЕЗОПАСНАЯ ЗАПИСЬ: пишем во временный файл
        with open(tmp_file_path, 'w', encoding='utf-8-sig', newline='') as f:
            # Записываем с нужным line ending (os.linesep)
            f.write(text.replace('\n', os.linesep))
            
        # Атомарно заменяем старый файл новым
        os.replace(tmp_file_path, file_path)
        
        print(f"Converted: {os.path.basename(file_path)} ({encoding_used} -> UTF-8 BOM)")
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        # Удаляем временный файл, если что-то пошло не так
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
        return False

def main():
    # Получаем абсолютный путь к папке, где лежит этот скрипт
    target_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Scanning directory and all subdirectories: {target_dir}")

    converted = 0
    
    # os.walk рекурсивно обходит текущую папку и все её подпапки
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            # Ищем только нужные расширения
            if file.endswith('.cpp') or file.endswith('.h'):
                # Формируем полный путь к файлу
                full_file_path = os.path.join(root, file)
                
                # Запускаем конвертацию
                if convert_file_to_utf8_bom(full_file_path):
                    converted += 1
                    
    print(f"\nDone! Successfully converted {converted} files.")

if __name__ == '__main__':
    main()