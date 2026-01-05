import sys
import os
import json
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                               QListWidget, QPushButton, QLabel, QFrame, QSplitter)
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QPixmap, QIcon, QFont, QColor, QPainter

class GremlinPicker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gremlin Picker")
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.resize(700, 500)
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Apply Dark Theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QListWidget {
                background-color: #363636;
                border: 1px solid #454545;
                border-radius: 8px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #528bff;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #454545;
            }
            QPushButton {
                background-color: #528bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #3a75ea;
            }
            QPushButton:pressed {
                background-color: #2a65da;
            }
            QLabel#Title {
                font-size: 18px;
                font-weight: bold;
                color: #dddddd;
                margin-bottom: 10px;
            }
            QLabel#PreviewLabel {
                border: 2px dashed #454545;
                border-radius: 8px;
                color: #888888;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Left Panel: List ---
        left_layout = QVBoxLayout()
        
        title_label = QLabel("Select Character")
        title_label.setObjectName("Title")
        left_layout.addWidget(title_label)
        
        self.list_widget = QListWidget()
        self.populate_list()
        self.list_widget.currentItemChanged.connect(self.on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.launch_gremlin)
        left_layout.addWidget(self.list_widget)

        self.launch_btn = QPushButton("Spawn Gremlin")
        self.launch_btn.clicked.connect(self.launch_gremlin)
        self.launch_btn.setCursor(Qt.PointingHandCursor)
        left_layout.addWidget(self.launch_btn)
        
        main_layout.addLayout(left_layout, 1)

        # --- Right Panel: Preview ---
        right_layout = QVBoxLayout()
        
        preview_title = QLabel("Preview")
        preview_title.setObjectName("Title")
        right_layout.addWidget(preview_title)

        self.preview_label = QLabel("Select a gremlin\nto see preview")
        self.preview_label.setObjectName("PreviewLabel")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(300, 300)
        self.preview_label.setSizePolicy(
            self.preview_label.sizePolicy().horizontalPolicy(), 
            self.preview_label.sizePolicy().verticalPolicy()
        )
        right_layout.addWidget(self.preview_label)
        
        main_layout.addLayout(right_layout, 1)

    def populate_list(self):
        spritesheet_dir = os.path.join(self.project_root, "spritesheet")
        if os.path.exists(spritesheet_dir):
            gremlins = sorted([
                d for d in os.listdir(spritesheet_dir) 
                if os.path.isdir(os.path.join(spritesheet_dir, d))
            ])
            for g in gremlins:
                self.list_widget.addItem(g)
                
    def on_selection_changed(self, current, previous):
        if not current:
            return
        
        name = current.text()
        self.update_preview(name)

    def update_preview(self, name):
        base_path = os.path.join(self.project_root, "spritesheet", name)
        config_path = os.path.join(base_path, "sprite-map.json")
        
        if not os.path.exists(config_path):
            self.preview_label.setText("No config found")
            self.preview_label.setPixmap(QPixmap())
            return

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Get idle image and dimensions
            image_name = config.get("Idle", "")
            if not image_name:
                # Fallback
                image_name = config.get("WalkIdle", "")
            
            if not image_name:
                 self.preview_label.setText("No idle image defined")
                 return

            image_path = os.path.join(base_path, image_name)
            if not os.path.exists(image_path):
                self.preview_label.setText("Image file missing")
                return

            # Load and crop
            full_pixmap = QPixmap(image_path)
            if full_pixmap.isNull():
                self.preview_label.setText("Failed to load image")
                return

            frame_w = config.get("FrameWidth", 100)
            frame_h = config.get("FrameHeight", 100)
            
            # Crop top-left frame
            cropped = full_pixmap.copy(0, 0, frame_w, frame_h)
            
            # Scale to a fixed size to prevent the label from growing infinitely
            scaled = cropped.scaled(
                QSize(350, 350), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            self.preview_label.setPixmap(scaled)
            self.preview_label.setText("") # Clear text
            
        except Exception as e:
            print(f"Preview error: {e}")
            self.preview_label.setText("Preview Error")

    def launch_gremlin(self):
        item = self.list_widget.currentItem()
        if item:
            print(item.text())
            sys.exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GremlinPicker()
    window.show()
    app.exec()
    sys.exit(1)