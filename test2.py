from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFileDialog, QListWidget, QRadioButton, QButtonGroup, QSizePolicy
from PyQt6.QtGui import QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
import os

class SearchLineEdit(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key.Key_Return:
            self.parent.search_text(self.text())

class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()

        self.setWindowTitle("PDF Viewer")
        self.setGeometry(0, 28, 1200, 750)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_pdf_from_list)
        self.file_list.setFixedWidth(300)  # Set a fixed width for the file list
        self.layout.addWidget(self.file_list)

        self.webView = QWebEngineView()
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.webView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.webView)

        self.right_container = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_container.setLayout(self.right_layout)
        
        self.right_list = QListWidget()
        self.right_list.setFixedWidth(300)  # Set a fixed width for the right dialog area
        self.right_layout.addWidget(self.right_list)

        # Adding Radio Buttons
        self.radio_button_group = QButtonGroup(self.right_container)
        
        self.start_radio_button = QRadioButton("Start")
        self.radio_button_group.addButton(self.start_radio_button)
        self.right_layout.addWidget(self.start_radio_button)
        
        self.end_radio_button = QRadioButton("End")
        self.radio_button_group.addButton(self.end_radio_button)
        self.right_layout.addWidget(self.end_radio_button)
        
        self.layout.addWidget(self.right_container)

        self.create_file_menu()

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
        file_url = QUrl.fromLocalFile(filepath)
        self.webView.setUrl(file_url)
        self.populate_right_list(filepath)

    def populate_right_list(self, filepath):
        self.right_list.clear()
        self.right_list.addItem(f"PDF File: {os.path.basename(filepath)}")
        # Add more information as needed

    # def search_text(self, text):
    #     flag = QWebEnginePage.FindFlag.FindCaseSensitively
    #     if text:
    #         self.webView.page().findText(text, flag)
    #     else:
    #         self.webView.page().stopFinding()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
