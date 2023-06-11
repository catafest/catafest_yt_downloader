import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QProgressBar, QDialog, QComboBox, QLabel, QMessageBox
from PyQt6.QtGui import QIcon, QPixmap
from pytube import YouTube
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialogButtonBox


class FormatChecker:
    def __init__(self, url):
        self.url = url

    def check_formats(self):
        try:
            yt = YouTube(self.url)
            formats = []
            streams = yt.streams.filter(only_video=True)
            for stream in streams:
                if stream.url:
                    format_info = {
                        'resolution': stream.resolution,
                        'file_extension': stream.mime_type.split("/")[-1]
                    }
                    formats.append(format_info)
                    print(" format_info ",format_info)
            return formats
        except Exception as e:
            print("Error:", str(e))
            return []


class FormatInfo:
    def __init__(self, resolution, file_formats):
        self.resolution = resolution
        self.file_formats = file_formats


class ResolutionDialog(QDialog):
    def __init__(self, formats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Resolution and File Format")
        self.formats = formats

        layout = QVBoxLayout(self)

        self.resolution_combo = QComboBox(self)
        for format_info in formats:
            resolution = format_info.resolution
            self.resolution_combo.addItem(resolution)
        layout.addWidget(self.resolution_combo)

        self.file_format_combo = QComboBox(self)
        self.update_file_formats(self.resolution_combo.currentText())
        layout.addWidget(self.file_format_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.resolution_combo.currentIndexChanged.connect(self.on_resolution_changed)

    def update_file_formats(self, resolution):
        self.file_format_combo.clear()
        for format_info in self.formats:
            if format_info.resolution == resolution:
                file_formats = format_info.file_formats
                self.file_format_combo.addItems(file_formats)

    def selected_resolution(self):
        return self.resolution_combo.currentText()

    def selected_file_format(self):
        return self.file_format_combo.currentText()

    def on_resolution_changed(self, index):
        resolution = self.resolution_combo.currentText()
        self.update_file_formats(resolution)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader - selected - only_video =True")
        self.setFixedWidth(640)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.url_edit = QLineEdit()
        layout.addWidget(self.url_edit)

        download_button = QPushButton("Download")
        download_button.clicked.connect(self.show_resolution_dialog)
        layout.addWidget(download_button)

        progress_layout = QHBoxLayout()
        layout.addLayout(progress_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)

        self.progress_icon_label = QLabel(self)
        pixmap = QPixmap("youtube.png")  # Înlocuiți "path_to_icon.png" cu calea către iconul dorit
        #pixmap = pixmap.scaledToHeight(128, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        self.progress_icon_label.setPixmap(pixmap)
        progress_layout.addWidget(self.progress_icon_label)

    def show_resolution_dialog(self):
        url = self.url_edit.text()
        if url:
            format_checker = FormatChecker(url)
            formats = format_checker.check_formats()
            format_infos = []
            for format in formats:
                resolution = format['resolution']
                file_extension = format['file_extension']
                format_info = next((info for info in format_infos if info.resolution == resolution), None)
                if format_info:
                    format_info.file_formats.append(file_extension)
                else:
                    format_info = FormatInfo(resolution, [file_extension])
                    format_infos.append(format_info)

            dialog = ResolutionDialog(format_infos, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                resolution = dialog.selected_resolution()
                file_format = dialog.selected_file_format()
                self.download_video(url, resolution, file_format)
        else:
            print("Please enter a valid YouTube URL.")

    def download_video(self, url, resolution, file_format):
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(only_video=True, resolution=resolution, mime_type="video/" + file_format).first()
            if stream:
                stream.download()
                print("Download completed!")
                QMessageBox.question(self, "Download Completed", "The video has been downloaded successfully.", QMessageBox.StandardButton.Ok)
            else:
                print("Error: The selected video format is not available for download.")
                QMessageBox.question(self, "Download Error", "The selected video format is not available for download.", QMessageBox.StandardButton.Ok)
        except Exception as e:
            print("Error:", str(e))
            QMessageBox.question(self, "Download Error", "An error occurred during the download.", QMessageBox.StandardButton.Ok)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
