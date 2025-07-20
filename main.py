import sys
import os
import platform
from pathlib import Path
import json
import base64
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QTextEdit, QMessageBox
from PyQt5.QtCore import QProcess

def get_config_dir():
    system = platform.system()
    if system == "Linux":
        config_dir = Path.home() / ".config" / "openspeedrun"
    elif system == "Darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "openspeedrun"
    elif system == "Windows":
        config_dir = Path.home() / "AppData" / "Local" / "openspeedrun"
    else:
        # Fallback for other systems
        config_dir = Path.home() / ".openspeedrun"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

class LSSConverterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('LSS to JSON Converter')
        self.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout()

        self.label = QLabel('Select a .lss file to convert', self)
        layout.addWidget(self.label)

        self.select_button = QPushButton('Select File', self)
        self.select_button.clicked.connect(self.select_file)
        layout.addWidget(self.select_button)

        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.setLayout(layout)
        self.converted_json_data = None
        self.converted_icons_data = None
        self.current_lss_file_name = None

    def select_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Select .lss File", "", "LiveSplit Files (*.lss)", options=options)
        if file_name:
            self.run_conversion(file_name)

    def run_conversion(self, file_path):
        self.output_area.clear()
        self.current_lss_file_name = file_path # Store the original file path
        process = QProcess(self)
        process.setProcessChannelMode(QProcess.MergedChannels)
        process.readyReadStandardOutput.connect(lambda: self.output_area.append(process.readAllStandardOutput().data().decode()))
        process.finished.connect(lambda: self.conversion_finished(process))
        process.start("python3", ["converter.py", file_path])

    def conversion_finished(self, process):
        if process.exitCode() == 0:
            output = process.readAllStandardOutput().data().decode()
            try:
                result = json.loads(output)
                self.converted_json_data = result.get('main_data')
                self.converted_icons_data = result.get('icons', [])
                
                # Automatic saving logic
                if self.converted_json_data:
                    default_dir = get_config_dir()
                    original_file_name = os.path.basename(self.current_lss_file_name) if self.current_lss_file_name else 'converted_splits'
                    suggested_file_name = f"{os.path.splitext(original_file_name)[0]}.json"
                    
                    # Construct the full path for the JSON file
                    json_file_path = os.path.join(default_dir, suggested_file_name)
                    
                    try:
                        # Ensure the directory for the JSON file exists
                        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

                        # Save the main JSON data
                        with open(json_file_path, 'w') as f:
                            json.dump(self.converted_json_data, f, indent=2)

                        # Save icons
                        if self.converted_icons_data:
                            icons_dir = os.path.join(default_dir, 'icons')
                            os.makedirs(icons_dir, exist_ok=True)
                            for icon in self.converted_icons_data:
                                icon_full_path = os.path.join(default_dir, icon['path'])
                                os.makedirs(os.path.dirname(icon_full_path), exist_ok=True)
                                with open(icon_full_path, 'wb') as f:
                                    f.write(base64.b64decode(icon['data']))

                        self.label.setText(f"Conversion successful! File saved to {json_file_path}")
                    except Exception as e:
                        self.label.setText(f"Conversion successful, but failed to save file: {e}")
                        QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
                else:
                    self.label.setText("Conversion successful, but no data to save.")

            except json.JSONDecodeError:
                self.label.setText("Conversion failed: Invalid JSON output from converter.py")
                self.output_area.append(output) # Show raw output for debugging
        else:
            self.label.setText("Conversion failed. See output below for details.")
            self.output_area.append(process.readAllStandardOutput().data().decode())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LSSConverterGUI()
    ex.show()
    sys.exit(app.exec_())