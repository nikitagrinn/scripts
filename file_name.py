from pathlib import Path

# Текущая папка, где лежит скрипт
base_dir = Path(__file__).parent
output_file = base_dir / 'file_list.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    # Ищем все файлы рекурсивно
    for path in base_dir.rglob('*'):
        if path.is_file() and path.name != 'file_list.txt' and path.name != Path(__file__).name:
            # path.relative_to(base_dir) оставляет только "хвост" пути
            # as_posix() заставляет использовать слэш '/' даже на Windows
            rel_path = path.relative_to(base_dir).as_posix()
            
            f.write(rel_path + '\n')

print("Готово.")