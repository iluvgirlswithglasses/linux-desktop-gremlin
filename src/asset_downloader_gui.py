import json
import sys
from pathlib import Path
from typing import Dict

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from .asset_downloader import download_asset
from .configs_loader import BASE_DIR


def load_asset_list() -> Dict[str, str]:
    with open("upstream-assets.json", "r") as f:
        return json.load(f)


class DownloadWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, asset_name, url):
        super().__init__()
        self.asset_name = asset_name
        self.url = url

    def run(self):
        try:
            download_asset(self.url)
            self.finished.emit(True, self.asset_name)
        except Exception as e:
            self.finished.emit(False, str(e))


class AssetDownloaderGui(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gremlins Downloader")
        self.setMinimumSize(450, 500)

        self.assets_data = load_asset_list()
        self.data_bucket = 69420  # Unique role for storing data in QListWidgetItem

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.info_label = QLabel("Double click to download:")
        self.info_label.setStyleSheet("color: #dddddd; font-weight: bold;")
        layout.addWidget(self.info_label)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Bottom Buttons
        btn_layout = QHBoxLayout()
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)

        # Apply your picker style to the close button
        self.close_btn.setStyleSheet(
            "background-color: #454545; color: #cccccc; padding: 8px;"
        )

        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

        # Setup Styling (matching picker.py)
        self.setStyleSheet(
            """
            QDialog { background-color: #2b2b2b; }
            QListWidget { background-color: #363636; border: 1px solid #454545; border-radius: 8px; color: white; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #404040; }
            QListWidget::item:selected { background-color: #528bff; }
            QPushButton { border-radius: 4px; font-weight: bold; }
        """
        )

        self.refresh_list()
        self.list_widget.itemDoubleClicked.connect(self.start_download)

    def is_installed(self, asset_name):
        """Checks if the asset exists in the gremlins folder."""
        # Check standard gremlins directory
        target_path = Path(BASE_DIR) / "gremlins" / asset_name
        return target_path.exists() and target_path.is_dir()

    def refresh_list(self):
        self.list_widget.clear()
        for name, url in self.assets_data.items():
            installed = self.is_installed(name)

            display_text = f"{name} {'(Installed)' if installed else ''}"
            item = QListWidgetItem(display_text)
            item.setData(self.data_bucket, (name, url))

            if installed:
                item.setFlags(
                    item.flags() & ~Qt.ItemFlag.ItemIsEnabled
                )  # Disable clicking installed ones

            self.list_widget.addItem(item)

    def start_download(self, item):
        asset_name, url = item.data(self.data_bucket)
        print(asset_name, url)

        self.info_label.setText(f"Downloading {asset_name}...")
        self.list_widget.setEnabled(False)

        self.worker = DownloadWorker(asset_name, url)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, success, message):
        self.list_widget.setEnabled(True)
        self.info_label.setText("Double click to download:")

        if success:
            QMessageBox.information(
                self, "Download Complete", "Gremlin installed successfully!"
            )
            self.refresh_list()
        else:
            QMessageBox.critical(self, "Error", f"Failed to download: {message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssetDownloaderGui()
    window.show()
    sys.exit(app.exec())
