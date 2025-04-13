# 🛡️ CryptoApp – Шифрование и криптоанализ на русском языке

**CryptoApp** — это удобное настольное приложение на Python с использованием PySide6, предоставляющее функции шифрования и дешифрования текстов с помощью алгоритмов **Цезаря** и **Виженера**, а также инструменты для криптоанализа и частотного анализа текста.

---

## 📦 Возможности

- 🔐 Шифрование и расшифровка методом Цезаря
- 🔐 Шифрование и расшифровка методом Виженера
- 🔎 Автоматический криптоанализ для Цезаря и Виженера
- 📊 Частотный анализ текста (буквы и биграммы)
- 📁 Управление файлами: чтение, сохранение, очистка созданных файлов
- 📉 Графическая визуализация частот
- 🪄 Удобный графический интерфейс на PySide6

---

## 🖼️ Интерфейс

Программа представляет собой многооконное приложение с вкладками:
- **Цезарь**: ввод ключа, шифрование/дешифрование, анализ
- **Виженер**: текстовый ключ, шифрование/дешифрование, анализ
- **Анализ частот**: текстовый отчет + графики

---

## 📁 Структура проекта

```text
CryptoApp/
├── main.py              # Главный файл приложения
├── resources/           # Ресурсы (иконки, шрифты и т.д.)
├── README.md            # Документация
└── requirements.txt     # Зависимости проекта

## 🧩 UML: Диаграмма классов
@startuml
class CryptoApp {
    - current_file: str
    - original_text: str
    - created_files: list
    - file_counters: dict
    - caesar_keys: dict
    - vigenere_keys: dict
    + read_file(filename): str
    + write_file(filename, content): bool
    + clear_created_files(): void
    + caesar_transform(text, key): str
    + caesar_encrypt(): void
    + caesar_decrypt(): void
    + vigenere_transform(text, key, encrypt): str
    + vigenere_encrypt(): void
    + vigenere_decrypt(): void
    + analyze_caesar(): void
    + analyze_vigenere(): void
    + analyze_frequency(): void
    + find_key_length(text): int
    + find_vigenere_key(text, key_length): str
    + show_error(message): void
    + show_info(message): void
}

class FrequencyAnalyzer {
    + analyze_text(text): tuple
    + create_frequency_plots(letters, bigrams): tuple
}

CryptoApp --> FrequencyAnalyzer
@enduml
