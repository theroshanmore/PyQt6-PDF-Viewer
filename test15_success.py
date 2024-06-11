import sys
import os
import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel, QListWidget, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QPixmap, QAction
import fitz  # PyMuPDF

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Viewer with Page Marking")
        self.setGeometry(50, 50, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Folder list
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_pdf_from_list)
        self.file_list.setFixedWidth(200)
        self.layout.addWidget(self.file_list)

        # PDF viewer
        self.viewer_layout = QVBoxLayout()
        self.layout.addLayout(self.viewer_layout)

        self.page_label = QLabel()
        self.viewer_layout.addWidget(self.page_label)

        # Navigation and marking buttons
        self.button_layout = QVBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.prev_button = QPushButton("Previous Page")
        self.prev_button.clicked.connect(self.prev_page)
        self.button_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next Page")
        self.next_button.clicked.connect(self.next_page)
        self.button_layout.addWidget(self.next_button)

        # Creating class radio buttons group
        self.radio_button_group = QButtonGroup(self)

        # Creating radio buttons
        self.class1_start_radio_button = QRadioButton("Class1 Start")
        self.class1_start_radio_button.clicked.connect(lambda: self.mark_page("Class1", "start"))

        self.class1_end_radio_button = QRadioButton("Class1 End")
        self.class1_end_radio_button.clicked.connect(lambda: self.mark_page("Class1", "end"))

        self.class2_start_radio_button = QRadioButton("Class2 Start")
        self.class2_start_radio_button.clicked.connect(lambda: self.mark_page("Class2", "start"))

        self.class2_end_radio_button = QRadioButton("Class2 End")
        self.class2_end_radio_button.clicked.connect(lambda: self.mark_page("Class2", "end"))

        # Adding radio buttons to button group
        self.radio_button_group.addButton(self.class1_start_radio_button)
        self.radio_button_group.addButton(self.class1_end_radio_button)
        self.radio_button_group.addButton(self.class2_start_radio_button)
        self.radio_button_group.addButton(self.class2_end_radio_button)

        # Adding buttons to button layout
        self.button_layout.addWidget(self.class1_start_radio_button)
        self.button_layout.addWidget(self.class1_end_radio_button)
        self.button_layout.addWidget(self.class2_start_radio_button)
        self.button_layout.addWidget(self.class2_end_radio_button)

        self.save_button = QPushButton("Save Marks")
        self.save_button.clicked.connect(self.save_marks)
        self.button_layout.addWidget(self.save_button)

        self.load_button = QPushButton("Open PDF")
        self.load_button.clicked.connect(self.open_pdf)
        self.button_layout.addWidget(self.load_button)

        self.current_file = None
        self.current_page = 0
        self.total_pages = 0
        self.marks = {
            "Class1": {"start": None, "end": None, "pages": []},
            "Class2": {"start": None, "end": None, "pages": []}
        }

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
        self.update_radio_buttons()

    def render_page_as_pixmap(self, doc, page_number):
        page = doc.load_page(page_number)
        pixmap = page.get_pixmap()
        img_bytes = pixmap.tobytes("png")
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

    def save_marks(self):
        # Generate the list of pages between start and end for each class
        for class_key in self.marks:
            start = self.marks[class_key]["start"]
            end = self.marks[class_key]["end"]
            if start is not None and end is not None:
                self.marks[class_key]["pages"] = list(range(start, end + 1))

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

    def update_radio_buttons(self):
        self.class1_start_radio_button.setChecked(self.current_page + 1 == self.marks["Class1"]["start"])
        self.class1_end_radio_button.setChecked(self.current_page + 1 == self.marks["Class1"]["end"])
        self.class2_start_radio_button.setChecked(self.current_page + 1 == self.marks["Class2"]["start"])
        self.class2_end_radio_button.setChecked(self.current_page + 1 == self.marks["Class2"]["end"])

    def mark_page(self, class_key, mark_type):
        current_page_number = self.current_page + 1
        self.marks[class_key][mark_type] = current_page_number
        print(f"{mark_type.capitalize()} page for {class_key} marked as {current_page_number}")
        if self.marks[class_key]["start"] is not None and self.marks[class_key]["end"] is not None:
            self.marks[class_key]["pages"] = list(range(self.marks[class_key]["start"], self.marks[class_key]["end"] + 1))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
