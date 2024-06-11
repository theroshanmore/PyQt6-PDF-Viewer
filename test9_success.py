import sys
import os
import json
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel, QListWidget, QRadioButton, QButtonGroup, QLineEdit
)
from PyQt6.QtGui import QPixmap
import fitz  # PyMuPDF
from PyQt6.QtGui import QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Viewer with Page Marking")
        self.setGeometry(0, 28, 1000, 750)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Folder list
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_pdf_from_list)
        self.file_list.setFixedWidth(300)
        self.layout.addWidget(self.file_list)

        # PDF viewer
        self.viewer_layout = QVBoxLayout()
        self.layout.addLayout(self.viewer_layout)

        self.page_label = QLabel()
        self.viewer_layout.addWidget(self.page_label)

        # Navigation and marking buttons
        self.button_layout = QVBoxLayout()
        self.viewer_layout.addLayout(self.button_layout)

        self.prev_button = QPushButton("Previous Page")
        self.prev_button.clicked.connect(self.prev_page)
        self.button_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next Page")
        self.next_button.clicked.connect(self.next_page)
        self.button_layout.addWidget(self.next_button)

        self.radio_button_group = QButtonGroup(self)
        self.start_radio_button = QRadioButton("Start")
        self.end_radio_button = QRadioButton("End")
        self.radio_button_group.addButton(self.start_radio_button)
        self.radio_button_group.addButton(self.end_radio_button)
        self.button_layout.addWidget(self.start_radio_button)
        self.button_layout.addWidget(self.end_radio_button)

        self.class_input = QLineEdit()
        self.class_input.setPlaceholderText("Enter Class Name")
        self.button_layout.addWidget(self.class_input)

        self.mark_button = QPushButton("Mark Page")
        self.mark_button.clicked.connect(self.mark_page)
        self.button_layout.addWidget(self.mark_button)

        self.save_button = QPushButton("Save Marks")
        self.save_button.clicked.connect(self.save_marks)
        self.button_layout.addWidget(self.save_button)

        self.load_button = QPushButton("Open PDF")
        self.load_button.clicked.connect(self.open_pdf)
        self.button_layout.addWidget(self.load_button)

        self.current_file = None
        self.current_page = 0
        self.total_pages = 0
        self.marks = {}

        self.create_file_menu()

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
        image = QPixmap()
        image.loadFromData(img_bytes)
        return image

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
            class_name = self.class_input.text()
            if not class_name:
                print("Please enter a class name.")
                return

            if class_name not in self.marks:
                self.marks[class_name] = {}

            if self.start_radio_button.isChecked():
                self.marks[class_name]['start'] = self.current_page + 1
                print(f"Start page for {class_name} marked as {self.current_page + 1}")
            elif self.end_radio_button.isChecked():
                self.marks[class_name]['end'] = self.current_page + 1
                print(f"End page for {class_name} marked as {self.current_page + 1}")

    def save_marks(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Marks", "", "JSON Files (*.json)")
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(self.marks, f, indent=4)
            print(f"Marks saved to {save_path}")

    def create_file_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        open_action = QAction('Open Directory', self)
        open_action.triggered.connect(self.open_directory_dialog)
        file_menu.addAction(open_action)

    def open_directory_dialog(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.populate_file_list(directory)

    def populate_file_list(self, directory):
        self.file_list.clear()
        for filename in os.listdir(directory):
            if filename.lower().endswith('.pdf'):
                self.file_list.addItem(os.path.join(directory, filename))
    
    def load_pdf_from_list(self, item):
        filepath = item.text()
        self.current_file = filepath
        self.current_page = 0
        self.load_pdf(filepath)
        self.total_pages = fitz.open(filepath).page_count

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
