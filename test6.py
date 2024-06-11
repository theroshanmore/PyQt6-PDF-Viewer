import sys
import os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel, QListWidget, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QPixmap
import fitz  # PyMuPDF
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()

        self.setWindowTitle("PDF Viewer with Page Marking")
        self.setGeometry(0, 28, 1000, 750)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.page_label = QLabel()
        self.layout.addWidget(self.page_label)

        # Folder
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_pdf_from_list)
        self.file_list.setFixedWidth(300)  # Set a fixed width for the file list
        self.layout.addWidget(self.file_list)

        self.webView = QWebEngineView()
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        
        self.layout.addWidget(self.webView)


        self.create_file_menu()

        self.navigation_layout = QVBoxLayout()
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

            save_pdf_path, _ = QFileDialog.getSaveFileName(self, "Save Marked Pages as PDF", "", "PDF Files (*.pdf)")
            if save_pdf_path:
                self.save_marked_pages_as_pdf(save_pdf_path)
                print(f"Marked pages saved to {save_pdf_path}")

    def save_marked_pages_as_pdf(self, save_pdf_path):
        doc = fitz.open(self.current_file)
        new_doc = fitz.open()

        for page_number, mark in sorted(self.marks.items()):
            page = doc.load_page(page_number)
            new_doc.insert_pdf(doc, from_page=page_number, to_page=page_number)

        new_doc.save(save_pdf_path)

    # Folders
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
        self.webView.setUrl(QUrl.fromLocalFile(filepath))

    
    def populate_right_list(self, filepath):
        self.right_list.clear()
        self.right_list.addItems()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
