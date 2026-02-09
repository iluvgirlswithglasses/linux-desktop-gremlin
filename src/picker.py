import sys
import os
import json
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                               QListWidget, QPushButton, QLabel, QDialog, QFormLayout,
                               QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit,
                               QDialogButtonBox, QComboBox, QMessageBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtMultimedia import QMediaDevices, QAudioDevice
from pathlib import Path

# Import path resolution logic
import sys
import os

# Ensure project root is in path so we can import 'src' package
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.configs_loader import GREMLIN_DIRS, _resolve_char_path, ResourceType
    from src.asset_downloader_gui import AssetDownloaderGui
except ImportError:
    # Fallback if running from root as 'python -m src.picker'
    from .configs_loader import GREMLIN_DIRS, _resolve_char_path, ResourceType
    from .asset_downloader_gui import AssetDownloaderGui

# =================================================================================
# CLASS: SettingsDialog (Global Config)
# =================================================================================
class SettingsDialog(QDialog):
    def __init__(self, project_root, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 350)
        self.project_root = project_root
        self.config_path = os.path.join(project_root, "config.json")
        self.config_data = {}
        
        # UI Setup
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Load Config
        self.load_config()

        # Fields
        self.starting_char_combo = QComboBox()
        self.populate_chars()
        if "StartingChar" in self.config_data:
            self.starting_char_combo.setCurrentText(self.config_data["StartingChar"])
            
        self.starting_char_combo.setToolTip("The character that spawns if you run the script without arguments.")
            
        self.systray_check = QCheckBox()
        self.systray_check.setChecked(self.config_data.get("Systray", False))
        self.systray_check.setToolTip("Show an icon in your system tray/taskbar for easy access.")
        
        self.emote_key_enabled_check = QCheckBox()
        self.emote_key_enabled_check.setChecked(self.config_data.get("EmoteKeyEnabled", True))
        
        self.emote_key_input = QLineEdit()
        self.emote_key_input.setMaxLength(1)
        self.emote_key_input.setText(self.config_data.get("EmoteKey", "P"))
        self.emote_key_input.setToolTip("Press this key to make the gremlin do a special animation.")
        
        # Audio Device Selector
        self.audio_device_combo = QComboBox()
        self.audio_device_combo.addItem("Default")
        self.audio_outputs = QMediaDevices.audioOutputs()
        for device in self.audio_outputs:
            self.audio_device_combo.addItem(device.description())
            
        current_device = self.config_data.get("AudioDevice", "Default")
        index = self.audio_device_combo.findText(current_device)
        if index >= 0:
            self.audio_device_combo.setCurrentIndex(index)
        self.audio_device_combo.setToolTip("Select the audio output device for the gremlin's sound effects.")

        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0.0, 1.0)
        self.volume_spin.setSingleStep(0.1)
        self.volume_spin.setValue(self.config_data.get("Volume", 0.8))

        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.1, 5.0)
        self.scale_spin.setSingleStep(0.1)
        self.scale_spin.setValue(self.config_data.get("Scale", 1.0))
        self.scale_spin.setToolTip("Scale the gremlin size (e.g. 0.5 = half size, 2.0 = double size).")

        self.anim_speed_spin = QDoubleSpinBox()
        self.anim_speed_spin.setRange(0.1, 5.0)
        self.anim_speed_spin.setSingleStep(0.1)
        self.anim_speed_spin.setValue(self.config_data.get("AnimationSpeed", 1.0))
        self.anim_speed_spin.setToolTip("Adjust animation playback speed (e.g. 0.5 = slower, 2.0 = faster).")

        # Add to form
        form_layout.addRow("Default Character:", self.starting_char_combo)
        form_layout.addRow("Enable System Tray:", self.systray_check)
        form_layout.addRow("Enable Emote Key:", self.emote_key_enabled_check)
        form_layout.addRow("Emote Key (e.g., P):", self.emote_key_input)
        form_layout.addRow("Audio Output:", self.audio_device_combo)
        form_layout.addRow("Volume (0.0 - 1.0):", self.volume_spin)
        form_layout.addRow("Global Scale:", self.scale_spin)
        form_layout.addRow("Animation Speed:", self.anim_speed_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.Reset)
        buttons.accepted.connect(self.save_config)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Reset).clicked.connect(self.reset_to_defaults)
        
        # Custom Button Styling
        save_btn = buttons.button(QDialogButtonBox.Save)
        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        reset_btn = buttons.button(QDialogButtonBox.Reset)
        
        if save_btn:
            save_btn.setText("Save")
            save_btn.setIcon(QIcon())
            save_btn.setStyleSheet("background-color: #528bff; color: white; border: none; padding: 8px 16px; border-radius: 4px;")
            save_btn.setCursor(Qt.PointingHandCursor)
            
        if cancel_btn:
            cancel_btn.setText("Cancel")
            cancel_btn.setIcon(QIcon())
            cancel_btn.setStyleSheet("background-color: #d32f2f; color: white; border: none; padding: 8px 16px; border-radius: 4px;")
            cancel_btn.setCursor(Qt.PointingHandCursor)

        if reset_btn:
            reset_btn.setText("Reset")
            reset_btn.setIcon(QIcon())
            reset_btn.setStyleSheet("background-color: #f0ad4e; color: white; border: none; padding: 8px 16px; border-radius: 4px;")
            reset_btn.setCursor(Qt.PointingHandCursor)

        layout.addWidget(buttons)

        # Apply Stylesheet
        style = (
            "QDialog { background-color: #2b2b2b; color: white; } "
            "QLabel { color: #dddddd; font-size: 14px; } "
            "QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit { background-color: #363636; color: white; border: 1px solid #454545; padding: 6px; border-radius: 4px; selection-background-color: #528bff; } "
            "QComboBox::drop-down { border: none; } "
            "QComboBox::down-arrow { image: none; border-left: 2px solid #555555; width: 0px; height: 0px; border-top: 2px solid #555555; margin-right: 10px; } "
            "QComboBox QAbstractItemView { background-color: #363636; color: white; selection-background-color: #528bff; selection-color: white; } "
            "QSpinBox::up-button, QDoubleSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::down-button { background-color: transparent; width: 20px; border-left: 1px solid #454545; } "
            "QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover, QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover { background-color: #555555; } "
            "QCheckBox { color: white; spacing: 8px; } "
            "QCheckBox::indicator { width: 18px; height: 18px; } "
            "QPushButton { border-radius: 4px; padding: 8px 16px; font-weight: bold; border: none; }"
        )
        self.setStyleSheet(style)

    def populate_chars(self):
        found_chars = set()
        
        # 1. Check Bundled Gremlin Dirs
        for directory in GREMLIN_DIRS:
            if directory.exists():
                for item in directory.iterdir():
                    if item.is_dir():
                        found_chars.add(item.name)

        # 2. Check Legacy Spritesheet Dir
        spritesheet_dir = os.path.join(self.project_root, "spritesheet")
        if os.path.exists(spritesheet_dir):
            for d in os.listdir(spritesheet_dir):
                if os.path.isdir(os.path.join(spritesheet_dir, d)):
                    found_chars.add(d)
        
        self.starting_char_combo.addItems(sorted(list(found_chars)))

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config_data = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config_data = {}
        else:
            self.config_data = {}

    def reset_to_defaults(self):
        self.systray_check.setChecked(False)
        self.emote_key_enabled_check.setChecked(True)
        self.emote_key_input.setText("P")
        self.audio_device_combo.setCurrentIndex(0) # Default
        self.volume_spin.setValue(0.8)
        self.scale_spin.setValue(1.0)
        self.anim_speed_spin.setValue(1.0)
        
        # Reset default character to Mambo
        index = self.starting_char_combo.findText("mambo", Qt.MatchFixedString)
        if index >= 0:
            self.starting_char_combo.setCurrentIndex(index)

    def save_config(self):
        self.config_data["StartingChar"] = self.starting_char_combo.currentText()
        self.config_data["Systray"] = self.systray_check.isChecked()
        self.config_data["EmoteKeyEnabled"] = self.emote_key_enabled_check.isChecked()
        self.config_data["EmoteKey"] = self.emote_key_input.text().upper()
        self.config_data["AudioDevice"] = self.audio_device_combo.currentText()
        self.config_data["Volume"] = self.volume_spin.value()
        self.config_data["Scale"] = self.scale_spin.value()
        self.config_data["AnimationSpeed"] = self.anim_speed_spin.value()

        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config_data, f, indent=4)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save config: {e}")

# =================================================================================
# CLASS: EmoteConfigDialog (Character Specific)
# =================================================================================
class EmoteConfigDialog(QDialog):
    def __init__(self, character_name, project_root, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Emote Config: {character_name}")
        self.setFixedSize(400, 300)
        self.character_name = character_name
        
        # Use new resolution logic
        root_path, is_bundled = _resolve_char_path(character_name)
        if is_bundled:
            self.config_path = str(root_path / "sprites" / "emote-config.json")
        else:
            self.config_path = os.path.join(project_root, "spritesheet", character_name, "emote-config.json")
            
        self.config_data = {}

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.load_config()

        self.annoy_check = QCheckBox()
        self.annoy_check.setChecked(self.config_data.get("AnnoyEmote", True))
        
        self.min_trigger = QSpinBox()
        self.min_trigger.setRange(1, 1440) 
        self.min_trigger.setValue(self.config_data.get("MinEmoteTriggerMinutes", 5))
        
        self.max_trigger = QSpinBox()
        self.max_trigger.setRange(1, 1440)
        self.max_trigger.setValue(self.config_data.get("MaxEmoteTriggerMinutes", 15))
        
        self.duration = QSpinBox()
        self.duration.setRange(100, 60000)
        self.duration.setSingleStep(100)
        self.duration.setValue(self.config_data.get("EmoteDuration", 3600))

        form_layout.addRow("Enable Annoy Emote:", self.annoy_check)
        form_layout.addRow("Min Trigger (min):", self.min_trigger)
        form_layout.addRow("Max Trigger (min):", self.max_trigger)
        form_layout.addRow("Duration (ms):", self.duration)

        layout.addLayout(form_layout)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.Reset)
        buttons.accepted.connect(self.save_config)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Reset).clicked.connect(self.reset_to_defaults)

        # Style buttons
        save_btn = buttons.button(QDialogButtonBox.Save)
        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        reset_btn = buttons.button(QDialogButtonBox.Reset)
        
        if save_btn:
            save_btn.setText("Save")
            save_btn.setIcon(QIcon())
            save_btn.setStyleSheet("background-color: #528bff; color: white; border: none; padding: 8px 16px; border-radius: 4px;")
            save_btn.setCursor(Qt.PointingHandCursor)
            
        if cancel_btn:
            cancel_btn.setText("Cancel")
            cancel_btn.setIcon(QIcon())
            cancel_btn.setStyleSheet("background-color: #d32f2f; color: white; border: none; padding: 8px 16px; border-radius: 4px;")
            cancel_btn.setCursor(Qt.PointingHandCursor)

        if reset_btn:
            reset_btn.setText("Reset")
            reset_btn.setIcon(QIcon())
            reset_btn.setStyleSheet("background-color: #f0ad4e; color: white; border: none; padding: 8px 16px; border-radius: 4px;")
            reset_btn.setCursor(Qt.PointingHandCursor)

        layout.addWidget(buttons)
        
        # Apply Stylesheet
        style = (
            "QDialog { background-color: #2b2b2b; color: white; } "
            "QLabel { color: #dddddd; font-size: 14px; } "
            "QSpinBox { background-color: #363636; color: white; border: 1px solid #454545; padding: 6px; border-radius: 4px; selection-background-color: #528bff; } "
            "QSpinBox::up-button, QSpinBox::down-button { background-color: transparent; width: 20px; border-left: 1px solid #454545; } "
            "QSpinBox::up-button:hover, QSpinBox::down-button:hover { background-color: #555555; } "
            "QCheckBox { color: white; spacing: 8px; } "
            "QCheckBox::indicator { width: 18px; height: 18px; }"
        )
        self.setStyleSheet(style)

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config_data = json.load(f)
            except:
                self.config_data = {}
        else:
            self.config_data = {
                "AnnoyEmote": True,
                "MinEmoteTriggerMinutes": 5,
                "MaxEmoteTriggerMinutes": 15,
                "EmoteDuration": 3600
            }

    def reset_to_defaults(self):
        self.annoy_check.setChecked(True)
        self.min_trigger.setValue(5)
        self.max_trigger.setValue(15)
        self.duration.setValue(3600)

    def save_config(self):
        self.config_data["AnnoyEmote"] = self.annoy_check.isChecked()
        self.config_data["MinEmoteTriggerMinutes"] = self.min_trigger.value()
        self.config_data["MaxEmoteTriggerMinutes"] = self.max_trigger.value()
        self.config_data["EmoteDuration"] = self.duration.value()

        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config_data, f, indent=4)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save emote config: {e}")

# =================================================================================
# CLASS: GremlinPicker (Main Window)
# =================================================================================
class GremlinPicker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gremlin Picker")
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.resize(700, 500)
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.project_root, "config.json")
        
        # Apply Dark Theme
        style = (
            "QWidget { background-color: #2b2b2b; color: #ffffff; font-family: 'Segoe UI', sans-serif; font-size: 14px; } "
            "QListWidget { background-color: #363636; border: 1px solid #454545; border-radius: 8px; padding: 5px; outline: none; } "
            "QListWidget::item { padding: 8px; border-radius: 4px; } "
            "QListWidget::item:selected { background-color: #528bff; color: white; } "
            "QListWidget::item:hover { background-color: #454545; } "
            "QPushButton { background-color: #528bff; color: white; border: none; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 15px; } "
            "QPushButton:hover { background-color: #3a75ea; } "
            "QPushButton:pressed { background-color: #2a65da; } "
            "QLabel#Title { font-size: 18px; font-weight: bold; color: #dddddd; margin-bottom: 10px; } "
            "QLabel#PreviewLabel { border: 2px dashed #454545; border-radius: 8px; color: #888888; }"
        )
        self.setStyleSheet(style)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Left Panel: List ---
        left_layout = QVBoxLayout()
        
        title_label = QLabel("Select Character")
        title_label.setObjectName("Title")
        left_layout.addWidget(title_label)
        
        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self.on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.launch_gremlin)
        left_layout.addWidget(self.list_widget)

        # Buttons Layout
        btn_layout = QHBoxLayout()
        
        self.launch_btn = QPushButton("Spawn Gremlin")
        self.launch_btn.clicked.connect(self.launch_gremlin)
        self.launch_btn.setCursor(Qt.PointingHandCursor)
        
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.open_downloader)
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        
        self.settings_btn = QPushButton("Config")
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #454545;
                color: #cccccc;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)

        btn_layout.addWidget(self.launch_btn, stretch=2)
        btn_layout.addWidget(self.download_btn, stretch=1)
        btn_layout.addWidget(self.settings_btn, stretch=1)
        left_layout.addLayout(btn_layout)
        
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
        
        self.emote_config_btn = QPushButton("Emote Config")
        self.emote_config_btn.setCursor(Qt.PointingHandCursor)
        self.emote_config_btn.clicked.connect(self.open_emote_config)
        self.emote_config_btn.setStyleSheet("""
            QPushButton {
                background-color: #454545;
                color: #cccccc;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        right_layout.addWidget(self.emote_config_btn)
        
        main_layout.addLayout(right_layout, 1)

        # Populate list AFTER UI is fully built
        self.populate_list()

    def open_emote_config(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Warning", "Please select a character first.")
            return
            
        char_name = item.text()
        dialog = EmoteConfigDialog(char_name, self.project_root, self)
        dialog.exec()

    def populate_list(self):
        found_chars = set()
        
        # 1. Check Bundled Gremlin Dirs
        for directory in GREMLIN_DIRS:
            if directory.exists():
                for item in directory.iterdir():
                    if item.is_dir():
                        found_chars.add(item.name)

        # 2. Check Legacy Spritesheet Dir
        spritesheet_dir = os.path.join(self.project_root, "spritesheet")
        if os.path.exists(spritesheet_dir):
            for d in os.listdir(spritesheet_dir):
                if os.path.isdir(os.path.join(spritesheet_dir, d)):
                    found_chars.add(d)

        # Load config to find default char
        default_char = ""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    default_char = data.get("StartingChar", "")
            except:
                pass

        for g in sorted(list(found_chars)):
            item = self.list_widget.addItem(g)
            # Select if it matches default
            if g == default_char:
                # We need to find the item we just added to select it
                # QListWidget.addItem returns None in PySide6 usually, so we access by row
                row = self.list_widget.count() - 1
                self.list_widget.setCurrentRow(row)
                self.update_preview(default_char)
                
    def on_selection_changed(self, current, previous):
        if not current:
            return
        
        name = current.text()
        self.update_preview(name)

    def update_preview(self, name):
        # Use new resolution logic
        root_path, is_bundled = _resolve_char_path(name)
        
        if is_bundled:
             config_path = root_path / "sprites" / "sprite-map.json"
             base_img_path = root_path / "sprites"
        else:
             config_path = Path(self.project_root) / "spritesheet" / name / "sprite-map.json"
             base_img_path = Path(self.project_root) / "spritesheet" / name
        
        if not config_path.exists():
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

            image_path = base_img_path / image_name
            if not image_path.exists():
                self.preview_label.setText("Image file missing")
                return

            # Load and crop
            full_pixmap = QPixmap(str(image_path))
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

    def open_settings(self):
        dialog = SettingsDialog(self.project_root, self)
        dialog.exec()

    def open_downloader(self):
        dialog = AssetDownloaderGui(self)
        dialog.exec()
        # Refresh list after download
        self.list_widget.clear()
        self.populate_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GremlinPicker()
    window.show()
    app.exec()
    sys.exit(1)
