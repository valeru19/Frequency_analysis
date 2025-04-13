import os
from collections import Counter, defaultdict
from math import gcd
from functools import reduce
import matplotlib
matplotlib.use("QtAgg")  # Qt backend (использует тот, что установлен)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget,
                               QFileDialog, QMessageBox, QSpinBox, QGroupBox, QScrollArea)

# Полная таблица частот для русского алфавита (включая пробел)
FREQ_RUS = {
    ' ': 0.175,  # пробел
    'о': 0.1097, 'е': 0.0845, 'а': 0.0801, 'и': 0.0735, 'н': 0.0670,
    'т': 0.0626, 'с': 0.0547, 'р': 0.0473, 'в': 0.0454, 'л': 0.0440,
    'к': 0.0349, 'м': 0.0321, 'д': 0.0298, 'п': 0.0281, 'у': 0.0262,
    'я': 0.0201, 'ы': 0.0190, 'ь': 0.0174, 'г': 0.0170, 'з': 0.0165,
    'б': 0.0159, 'ч': 0.0144, 'й': 0.0121, 'х': 0.0097, 'ж': 0.0094,
    'ш': 0.0073, 'ю': 0.0064, 'ц': 0.0048, 'щ': 0.0036, 'э': 0.0032,
    'ф': 0.0026, 'ъ': 0.0004, 'ё': 0.0004
}

# Русский алфавит (строчные буквы + пробел)
RUS_LOWER = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
RUS_UPPER = RUS_LOWER.upper()
ALPHABET_SIZE = len(RUS_LOWER)


class MplCanvas(FigureCanvas):
    """Класс для встраивания графиков matplotlib в PySide6"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)


class FrequencyAnalyzer:
    @staticmethod
    def analyze_text(text):
        """Анализ частотных характеристик текста"""
        # Подсчет отдельных букв
        letters = [c.lower() for c in text if c.lower() in RUS_LOWER]
        letter_counts = Counter(letters)

        # Подсчет биграмм (включая пробелы)
        bigrams = []
        for i in range(len(letters) - 1):
            bigram = letters[i] + letters[i + 1]
            bigrams.append(bigram)
        bigram_counts = Counter(bigrams)

        return letter_counts, bigram_counts

    @staticmethod
    def create_frequency_plots(letter_counts, bigram_counts):
        """Создание графиков частотных характеристик"""
        # Топ 10 букв
        top_letters = letter_counts.most_common(10)
        letters, l_counts = zip(*top_letters)

        # Создаем canvas для букв
        letters_canvas = MplCanvas(width=6, height=4, dpi=100)
        letters_canvas.axes.bar(letters, l_counts)
        letters_canvas.axes.set_title("10 самых частых букв")
        letters_canvas.axes.set_xlabel("Буквы")
        letters_canvas.axes.set_ylabel("Количество")

        # Топ 10 биграмм
        top_bigrams = bigram_counts.most_common(10)
        bigrams, b_counts = zip(*top_bigrams)

        # Создаем canvas для биграмм
        bigrams_canvas = MplCanvas(width=8, height=4, dpi=100)  # Увеличили ширину для биграмм
        x_pos = range(len(bigrams))
        bigrams_canvas.axes.bar(x_pos, b_counts)
        bigrams_canvas.axes.set_title("10 самых частых биграмм")
        bigrams_canvas.axes.set_xlabel("Биграммы")
        bigrams_canvas.axes.set_ylabel("Количество")

        # Устанавливаем подписи для биграмм
        bigrams_canvas.axes.set_xticks(x_pos)
        bigrams_canvas.axes.set_xticklabels([f"'{b[0]}'{b[1]}'" for b in bigrams], rotation=45, ha='right')

        return letters_canvas, bigrams_canvas


class CryptoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Русский криптоанализатор")
        self.setMinimumSize(1000, 800)

        # Словарь для хранения счетчиков файлов по режимам
        self.file_counters = {
            "caesar_enc": 1,
            "caesar_dec": 1,
            "vigenere_enc": 1,
            "vigenere_dec": 1
        }

        # Словари для хранения ключей
        self.caesar_keys = {}  # {filename: key}
        self.vigenere_keys = {}  # {filename: key}

        self.current_file = None
        self.original_text = ""
        self.current_mode = None
        self.created_files = []

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        self.create_caesar_tab(tabs)
        self.create_vigenere_tab(tabs)
        self.create_analysis_tab(tabs)
        self.create_frequency_tab(tabs)

        clear_btn = QPushButton("Очистить созданные файлы")
        clear_btn.clicked.connect(self.clear_created_files)
        main_layout.addWidget(clear_btn)

        self.status_bar = self.statusBar()

    def create_caesar_tab(self, tabs):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        file_group = QHBoxLayout()
        self.caesar_file_label = QLabel("Файл не выбран")
        file_btn = QPushButton("Выбрать файл")
        file_btn.clicked.connect(lambda: self.select_file(self.caesar_file_label, "caesar"))
        file_group.addWidget(self.caesar_file_label)
        file_group.addWidget(file_btn)
        layout.addLayout(file_group)

        key_group = QHBoxLayout()
        key_group.addWidget(QLabel("Ключ (0-32):"))
        self.caesar_key_input = QSpinBox()
        self.caesar_key_input.setRange(0, ALPHABET_SIZE - 1)
        key_group.addWidget(self.caesar_key_input)
        layout.addLayout(key_group)

        btn_group = QHBoxLayout()
        encrypt_btn = QPushButton("Зашифровать")
        encrypt_btn.clicked.connect(self.caesar_encrypt)
        decrypt_btn = QPushButton("Расшифровать")
        decrypt_btn.clicked.connect(self.caesar_decrypt)
        btn_group.addWidget(encrypt_btn)
        btn_group.addWidget(decrypt_btn)
        layout.addLayout(btn_group)

        self.caesar_result = QTextEdit()
        self.caesar_result.setReadOnly(True)
        layout.addWidget(self.caesar_result)

        tabs.addTab(tab, "Шифр Цезаря")

    def create_vigenere_tab(self, tabs):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        file_group = QHBoxLayout()
        self.vigenere_file_label = QLabel("Файл не выбран")
        file_btn = QPushButton("Выбрать файл")
        file_btn.clicked.connect(lambda: self.select_file(self.vigenere_file_label, "vigenere"))
        file_group.addWidget(self.vigenere_file_label)
        file_group.addWidget(file_btn)
        layout.addLayout(file_group)

        key_group = QHBoxLayout()
        key_group.addWidget(QLabel("Ключ (русские буквы):"))
        self.vigenere_key_input = QLineEdit()
        key_group.addWidget(self.vigenere_key_input)
        layout.addLayout(key_group)

        btn_group = QHBoxLayout()
        encrypt_btn = QPushButton("Зашифровать")
        encrypt_btn.clicked.connect(self.vigenere_encrypt)
        decrypt_btn = QPushButton("Расшифровать")
        decrypt_btn.clicked.connect(self.vigenere_decrypt)
        btn_group.addWidget(encrypt_btn)
        btn_group.addWidget(decrypt_btn)
        layout.addLayout(btn_group)

        self.vigenere_result = QTextEdit()
        self.vigenere_result.setReadOnly(True)
        layout.addWidget(self.vigenere_result)

        tabs.addTab(tab, "Шифр Виженера")

    def create_analysis_tab(self, tabs):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        file_group = QHBoxLayout()
        self.analysis_file_label = QLabel("Файл не выбран")
        file_btn = QPushButton("Выбрать файл")
        file_btn.clicked.connect(lambda: self.select_file(self.analysis_file_label, "analysis"))
        file_group.addWidget(self.analysis_file_label)
        file_group.addWidget(file_btn)
        layout.addLayout(file_group)

        caesar_group = QGroupBox("Анализ Цезаря")
        caesar_layout = QVBoxLayout(caesar_group)
        caesar_btn = QPushButton("Проанализировать")
        caesar_btn.clicked.connect(self.analyze_caesar)
        caesar_layout.addWidget(caesar_btn)
        self.caesar_analysis_result = QTextEdit()
        self.caesar_analysis_result.setReadOnly(True)
        caesar_layout.addWidget(self.caesar_analysis_result)
        layout.addWidget(caesar_group)

        vigenere_group = QGroupBox("Анализ Виженера")
        vigenere_layout = QVBoxLayout(vigenere_group)
        vigenere_btn = QPushButton("Проанализировать")
        vigenere_btn.clicked.connect(self.analyze_vigenere)
        vigenere_layout.addWidget(vigenere_btn)
        self.vigenere_analysis_result = QTextEdit()
        self.vigenere_analysis_result.setReadOnly(True)
        vigenere_layout.addWidget(self.vigenere_analysis_result)
        layout.addWidget(vigenere_group)

        tabs.addTab(tab, "Криптоанализ")

    def create_frequency_tab(self, tabs):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        file_group = QHBoxLayout()
        self.freq_file_label = QLabel("Файл не выбран")
        file_btn = QPushButton("Выбрать файл")
        file_btn.clicked.connect(lambda: self.select_file(self.freq_file_label, "frequency"))
        file_group.addWidget(self.freq_file_label)
        file_group.addWidget(file_btn)
        layout.addLayout(file_group)

        analyze_btn = QPushButton("Анализировать частотные характеристики")
        analyze_btn.clicked.connect(self.analyze_frequency)
        layout.addWidget(analyze_btn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.freq_scroll_content = QWidget()
        self.freq_scroll_layout = QVBoxLayout(self.freq_scroll_content)
        scroll.setWidget(self.freq_scroll_content)
        layout.addWidget(scroll)

        tabs.addTab(tab, "Частотный анализ")

    def select_file(self, label_widget, mode):
        file_path = QFileDialog.getOpenFileName(self, "Выберите файл")[0]
        if file_path:
            self.current_file = file_path
            self.current_mode = mode
            label_widget.setText(os.path.basename(file_path))
            self.original_text = self.read_file(file_path)

            if mode == "caesar":
                self.caesar_result.clear()
            elif mode == "vigenere":
                self.vigenere_result.clear()
            elif mode == "analysis":
                self.caesar_analysis_result.clear()
                self.vigenere_analysis_result.clear()
            elif mode == "frequency":
                for i in reversed(range(self.freq_scroll_layout.count())):
                    widget = self.freq_scroll_layout.itemAt(i).widget()
                    if widget is not None:
                        widget.deleteLater()

    def read_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.show_error(f"Ошибка чтения файла: {str(e)}")
            return ""

    def write_file(self, filename, content):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.created_files.append(filename)
            return True
        except Exception as e:
            self.show_error(f"Ошибка записи файла: {str(e)}")
            return False

    def clear_created_files(self):
        deleted = 0
        remaining_files = []

        for filepath in self.created_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    deleted += 1
                else:
                    remaining_files.append(filepath)
            except Exception as e:
                remaining_files.append(filepath)
                self.show_error(f"Ошибка удаления {filepath}: {str(e)}")

        self.created_files = remaining_files
        for key in self.file_counters:
            self.file_counters[key] = 1
        self.show_info(f"Удалено {deleted} файлов. Не удалось удалить {len(remaining_files)}")

    def caesar_transform(self, text, key):
        result = []
        key = key % ALPHABET_SIZE

        for char in text:
            lower_char = char.lower()
            if lower_char in RUS_LOWER:
                alphabet = RUS_UPPER if char.isupper() else RUS_LOWER
                index = alphabet.find(char)
                new_index = (index + key) % ALPHABET_SIZE
                result.append(alphabet[new_index])
            else:
                result.append(char)

        return ''.join(result)

    def caesar_encrypt(self):
        if not self.current_file:
            self.show_error("Файл не выбран!")
            return

        key = self.caesar_key_input.value()
        encrypted = self.caesar_transform(self.original_text, key)

        counter = self.file_counters["caesar_enc"]
        output_file = f"encC_{counter}.txt"

        if self.write_file(output_file, encrypted):
            self.caesar_keys[output_file] = key
            self.caesar_result.setPlainText(
                f"Ключ: {key}\n\n" + encrypted[:1000] + ("\n..." if len(encrypted) > 1000 else ""))
            self.status_bar.showMessage(f"Файл зашифрован: {output_file} (ключ: {key})", 5000)
            self.file_counters["caesar_enc"] += 1

    def caesar_decrypt(self):
        if not self.current_file:
            self.show_error("Файл не выбран!")
            return

        key = self.caesar_key_input.value()
        decrypted = self.caesar_transform(self.original_text, -key)

        counter = self.file_counters["caesar_dec"]
        output_file = f"decC_{counter}.txt"

        if self.write_file(output_file, decrypted):
            self.caesar_result.setPlainText(
                f"Ключ: {key}\n\n" + decrypted[:1000] + ("\n..." if len(decrypted) > 1000 else ""))
            self.status_bar.showMessage(f"Файл расшифрован: {output_file} (ключ: {key})", 5000)
            self.file_counters["caesar_dec"] += 1

    def vigenere_transform(self, text, key, encrypt=True):
        result = []
        clean_key = self.prepare_key(key)
        if not clean_key:
            self.show_error("Ключ должен содержать только русские буквы и пробелы!")
            return ""

        key_len = len(clean_key)
        key_pos = 0

        for char in text:
            lower_char = char.lower()
            if lower_char in RUS_LOWER:
                alphabet = RUS_UPPER if char.isupper() else RUS_LOWER
                char_index = alphabet.find(char)
                key_char = clean_key[key_pos % key_len]
                key_index = RUS_LOWER.find(key_char)

                if encrypt:
                    new_index = (char_index + key_index) % ALPHABET_SIZE
                else:
                    new_index = (char_index - key_index) % ALPHABET_SIZE

                result.append(alphabet[new_index])
                key_pos += 1
            else:
                result.append(char)

        return ''.join(result)

    def prepare_key(self, key):
        cleaned = ''.join(c.lower() for c in key if c.lower() in RUS_LOWER)
        return cleaned if cleaned else None

    def vigenere_encrypt(self):
        if not self.current_file:
            self.show_error("Файл не выбран!")
            return

        key = self.vigenere_key_input.text().strip()
        if not key:
            self.show_error("Введите ключ!")
            return

        encrypted = self.vigenere_transform(self.original_text, key, encrypt=True)
        if not encrypted:
            return

        counter = self.file_counters["vigenere_enc"]
        output_file = f"encV_{counter}.txt"

        if self.write_file(output_file, encrypted):
            self.vigenere_keys[output_file] = key
            self.vigenere_result.setPlainText(
                f"Ключ: {key}\n\n" + encrypted[:1000] + ("\n..." if len(encrypted) > 1000 else ""))
            self.status_bar.showMessage(f"Файл зашифрован: {output_file} (ключ: {key})", 5000)
            self.file_counters["vigenere_enc"] += 1

    def vigenere_decrypt(self):
        if not self.current_file:
            self.show_error("Файл не выбран!")
            return

        key = self.vigenere_key_input.text().strip()
        if not key:
            self.show_error("Введите ключ!")
            return

        decrypted = self.vigenere_transform(self.original_text, key, encrypt=False)
        if not decrypted:
            return

        counter = self.file_counters["vigenere_dec"]
        output_file = f"decV_{counter}.txt"

        if self.write_file(output_file, decrypted):
            self.vigenere_result.setPlainText(
                f"Ключ: {key}\n\n" + decrypted[:1000] + ("\n..." if len(decrypted) > 1000 else ""))
            self.status_bar.showMessage(f"Файл расшифрован: {output_file} (ключ: {key})", 5000)
            self.file_counters["vigenere_dec"] += 1

    def analyze_caesar(self):
        if not self.current_file:
            self.show_error("Файл не выбран!")
            return

        clean_text = ''.join(c.lower() for c in self.original_text if c.lower() in RUS_LOWER)
        if not clean_text:
            self.show_error("Текст не содержит русских букв!")
            return

        counter = Counter(clean_text)
        most_common = counter.most_common(1)[0][0]

        best_key = 0
        best_score = -1

        for assumed_char, expected_freq in FREQ_RUS.items():
            key = (RUS_LOWER.find(most_common) - RUS_LOWER.find(assumed_char)) % ALPHABET_SIZE
            decrypted = self.caesar_transform(self.original_text, -key)

            decrypted_clean = ''.join(c.lower() for c in decrypted if c.lower() in RUS_LOWER)
            if not decrypted_clean:
                continue

            decrypted_counter = Counter(decrypted_clean)
            total = sum(decrypted_counter.values())
            score = sum(min(decrypted_counter.get(c, 0) / total, freq) for c, freq in FREQ_RUS.items())

            if score > best_score:
                best_score = score
                best_key = key

        decrypted = self.caesar_transform(self.original_text, -best_key)

        result_text = f"Найденный ключ: {best_key}\n\n"
        result_text += decrypted[:1000] + ("\n..." if len(decrypted) > 1000 else "")

        self.caesar_analysis_result.setPlainText(result_text)
        self.status_bar.showMessage(f"Анализ завершен. Ключ: {best_key}", 5000)

    def analyze_vigenere(self):
        if not self.current_file:
            self.show_error("Файл не выбран!")
            return

        clean_text = ''.join(c.lower() for c in self.original_text if c.lower() in RUS_LOWER)
        if not clean_text:
            self.show_error("Текст не содержит русских букв!")
            return

        key_length = self.find_key_length(clean_text)
        if not key_length:
            self.show_error("Не удалось определить длину ключа")
            return

        key = self.find_vigenere_key(clean_text, key_length)
        decrypted = self.vigenere_transform(self.original_text, key, encrypt=False)

        result_text = f"Предполагаемая длина ключа: {key_length}\n"
        result_text += f"Найденный ключ: '{key}'\n\n"
        result_text += decrypted[:1000] + ("\n..." if len(decrypted) > 1000 else "")

        self.vigenere_analysis_result.setPlainText(result_text)
        self.status_bar.showMessage(f"Анализ завершен. Длина ключа: {key_length}", 5000)

    def analyze_frequency(self):
        """Анализ частотных характеристик текста"""
        if not self.current_file:
            self.show_error("Файл не выбран!")
            return

        # Очищаем предыдущие результаты
        for i in reversed(range(self.freq_scroll_layout.count())):
            widget = self.freq_scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Анализируем текст (включая пробелы в биграммах)
        letter_counts, bigram_counts = FrequencyAnalyzer.analyze_text(self.original_text)

        # Создаем текстовый отчет
        report = QTextEdit()
        report.setReadOnly(True)
        text = "Частотные характеристики текста:\n\n"
        text += "10 самых частых букв:\n"
        total_letters = sum(letter_counts.values())
        for letter, count in letter_counts.most_common(10):
            text += f"'{letter}': {count} ({count / total_letters:.2%})\n"

        text += "\n10 самых частых биграмм:\n"
        total_bigrams = sum(bigram_counts.values())
        for bigram, count in bigram_counts.most_common(10):
            text += f"'{bigram[0]}'{bigram[1]}': {count} ({count / total_bigrams:.2%})\n"

        report.setPlainText(text)
        self.freq_scroll_layout.addWidget(report)

        # Создаем и добавляем графики
        letters_canvas, bigrams_canvas = FrequencyAnalyzer.create_frequency_plots(letter_counts, bigram_counts)
        self.freq_scroll_layout.addWidget(letters_canvas)
        self.freq_scroll_layout.addWidget(bigrams_canvas)

        self.status_bar.showMessage("Анализ частотных характеристик завершен", 5000)

    def find_key_length(self, text, max_len=20):
        seq_len = 4
        sequences = {}

        for i in range(len(text) - seq_len):
            seq = text[i:i + seq_len]
            if seq in sequences:
                sequences[seq].append(i)
            else:
                sequences[seq] = [i]

        repeated_seqs = {k: v for k, v in sequences.items() if len(v) > 1}
        if not repeated_seqs:
            return None

        distances = []
        for positions in repeated_seqs.values():
            for i in range(1, len(positions)):
                distances.append(positions[i] - positions[0])

        if not distances:
            return None

        overall_gcd = reduce(gcd, distances)

        if overall_gcd == 1:
            divisors = Counter()
            for d in distances:
                for i in range(2, min(d, max_len) + 1):
                    if d % i == 0:
                        divisors[i] += 1

            if not divisors:
                return None

            most_common = divisors.most_common(3)
            return most_common[0][0] if most_common[0][0] <= max_len else None
        else:
            return overall_gcd if 1 < overall_gcd <= max_len else None

    def find_vigenere_key(self, text, key_length):
        key = []
        groups = [text[i::key_length] for i in range(key_length)]

        for group in groups:
            counter = Counter(group)
            most_common = counter.most_common(1)[0][0]

            best_shift = 0
            best_score = -1

            for assumed_char, expected_freq in FREQ_RUS.items():
                shift = (RUS_LOWER.find(most_common) - RUS_LOWER.find(assumed_char)) % ALPHABET_SIZE

                decrypted_part = self.caesar_transform(group, -shift)
                decrypted_counter = Counter(decrypted_part.lower())
                total = sum(decrypted_counter.values())
                if total == 0:
                    continue

                score = sum(min(decrypted_counter.get(c, 0) / total, freq) for c, freq in FREQ_RUS.items())

                if score > best_score:
                    best_score = score
                    best_shift = shift

            key_char = RUS_LOWER[best_shift]
            key.append(key_char)

        return ''.join(key)

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)

    def show_info(self, message):
        QMessageBox.information(self, "Информация", message)


if __name__ == "__main__":
    app = QApplication([])
    window = CryptoApp()
    window.show()
    app.exec()
