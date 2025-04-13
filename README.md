# 🔐 CryptoApp

Приложение для шифрования, дешифрования и криптоанализа текстов на русском языке с использованием шифров Цезаря и Виженера. Также реализован частотный анализ текста, включая биграммы, с визуализацией результатов.

## 📦 Возможности

- Шифр Цезаря:
  - Шифрование/дешифрование с выбором ключа
  - Криптоанализ методом частот
- Шифр Виженера:
  - Шифрование/дешифрование с произвольным ключом
  - Криптоанализ с автоматическим определением длины ключа
- Частотный анализ:
  - Подсчет частот букв и биграмм
  - Отображение статистики и графиков
- Управление файлами:
  - Автоматическое создание и удаление зашифрованных/расшифрованных файлов
  - Сохранение ключей для дальнейшего использования

## 🛠️ Установка

```bash
pip install -r requirements.txt
```

### Зависимости:

- Python 3.8+
- PySide6
- matplotlib

## 🚀 Запуск

```bash
python main.py
```

## 📁 Структура проекта

```plaintext
CryptoApp/
├── main.py                # Главный файл с логикой приложения и GUI
├── frequency_analyzer.py  # Модуль анализа частот
├── utils.py               # Вспомогательные функции (если есть)
├── assets/                # Иконки, стили, шаблоны
└── README.md              # Документация
```

## 🧠 Основные компоненты

- `caesar_transform()` — логика сдвига по алфавиту
- `vigenere_transform()` — логика шифра Виженера
- `analyze_caesar()` — криптоанализ Цезаря
- `analyze_vigenere()` — криптоанализ Виженера
- `analyze_frequency()` — частотный и биграммный анализ текста
- `clear_created_files()` — удаление временных файлов
- GUI: интерфейс PySide6 с вкладками, формами и кнопками

## 📈 Визуализация

Частотный анализ визуализирует:

- 📊 10 самых частых букв
- 🔁 10 самых частых биграмм
- 📉 Графики для удобного восприятия распределения

## 📎 Пример вывода частотного анализа:

```
Частотные характеристики текста:

10 самых частых букв:
'о': 523 (11.50%)
'е': 489 (10.76%)
...

10 самых частых биграмм:
'н'о': 45 (2.30%)
'ст': 42 (2.15%)
...
```

## 🧩 Диаграмма классов UML

```plantuml
@startuml

class CryptoApp {
    - current_file: str
    - original_text: str
    - created_files: list
    - caesar_keys: dict
    - vigenere_keys: dict
    - file_counters: dict

    + read_file(filename)
    + write_file(filename, content)
    + clear_created_files()

    + caesar_transform(text, key)
    + caesar_encrypt()
    + caesar_decrypt()
    + analyze_caesar()

    + vigenere_transform(text, key, encrypt)
    + vigenere_encrypt()
    + vigenere_decrypt()
    + analyze_vigenere()

    + analyze_frequency()

    + find_key_length(text, max_len)
    + find_vigenere_key(text, key_length)

    + show_error(message)
    + show_info(message)
}

class FrequencyAnalyzer {
    + analyze_text(text)
    + create_frequency_plots(letters, bigrams)
}

CryptoApp --> FrequencyAnalyzer

@enduml
```

(Диаграмму можно визуализировать в [PlantUML](https://plantuml.com/))

## 📌 Замечания

- Поддержка только русских букв
- Программа работает с `.txt` файлами в UTF-8
- Автоматическая генерация имен файлов (`encC_1.txt`, `decV_2.txt` и т.д.)

## 📧 Обратная связь

Если вы нашли баг или хотите предложить улучшение — создайте issue или отправьте pull request.

---

**Лицензия:** MIT



![VLF1hjiW4BpxApWwglq3ELGlYjHxJpqYWjSEAbxSPPtKZVhlXO2La3elXnZlZ7TcOFdmh8ZdqLRQAk_5aPQ9tM6QnAqIuTSAHsOmgAna-CrxuPaoe6SYG9QziL3K2HH3Tw_xlR36SqPYHMet8mC5f3DwHRG2hqZ-XAMiNym020J_8UtzyKKGgAHKnpzK8-oIbmHVoJ2KU2EqGmRaG3mvPp](https://github.com/user-attachments/assets/57fea131-5764-424c-a022-9469faf5ee21)
