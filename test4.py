import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel, QListWidget, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QPixmap
import fitz  # PyMuPDF

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Viewer with Page Marking")
        self.setGeometry(100, 100, 1000, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.page_label = QLabel()
        self.layout.addWidget(self.page_label)

        self.navigation_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous Page")
        self.prev_button.clicked.connect(self.prev_page)
        self.navigation_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next Page")
        self.next_button.clicked.connect(self.next_page)
        self.navigation_layout.addWidget(self.next_button)

        self.layout.addLayout(self.navigation_layout)

        self.radio_button_group = QButtonGroup(self)
        self.start_radio_button = QRadioButton("Start")
        self.end_radio_button = QRadioButton("End")
        self.radio_button_group.addButton(self.start_radio_button)
        self.radio_button_group.addButton(self.end_radio_button)

        self.layout.addWidget(self.start_radio_button)
        self.layout.addWidget(self.end_radio_button)

        self.mark_button = QPushButton("Mark Page")
        self.mark_button.clicked.connect(self.mark_page)
        self.layout.addWidget(self.mark_button)

        self.save_button = QPushButton("Save Marks")
        self.save_button.clicked.connect(self.save_marks)
        self.layout.addWidget(self.save_button)

        self.load_button = QPushButton("Open PDF")
        self.load_button.clicked.connect(self.open_pdf)
        self.layout.addWidget(self.load_button)

        self.current_file = None
        self.current_page = 0
        self.total_pages = 0
        self.marks = {}

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            self.current_file = file_path
            self.current_page = 0
            self.load_pdf(file_path)
            self.total_pages = fitz.open(file_path).page_count

    def load_pdf(self, file_path):
        self.display_pdf(file_path, self.current_page)

    def display_pdf(self, file_path, page_number):
        doc = fitz.open(file_path)
        pixmap = self.render_page_as_pixmap(doc, page_number)
        self.page_label.setPixmap(pixmap)

    def render_page_as_pixmap(self, doc, page_number):
        page = doc.load_page(page_number)
        pixmap = page.get_pixmap()
        img_bytes = pixmap.tobytes()
        pixmap = QPixmap()
        pixmap.loadFromData(img_bytes)
        return pixmap

    def prev_page(self):
        if self.current_file and self.current_page > 0:
            self.current_page -= 1
            self.display_pdf(self.current_file, self.current_page)

    def next_page(self):
        if self.current_file and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_pdf(self.current_file, self.current_page)

    def mark_page(self):
        if self.current_file:
            mark_type = "Start" if self.start_radio_button.isChecked() else "End"
            self.marks[self.current_page] = mark_type
            print(f"Page {self.current_page + 1} marked as {mark_type}")

    def save_marks(self):
        if self.marks:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Marks", "", "Text Files (*.txt)")
            if save_path:
                with open(save_path, 'w') as f:
                    for page, mark in sorted(self.marks.items()):
                        f.write(f"Page {page + 1}: {mark}\n")
                print(f"Marks saved to {save_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
