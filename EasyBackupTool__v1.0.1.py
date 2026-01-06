#------------------------------------------------------------------
# Easy Backup Tool 
# v1.0.1
# by diegudio
#------------------------------------------------------------------
import sys, os, shutil, json, ctypes
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QFileDialog, QVBoxLayout, QHBoxLayout, QTreeWidget,
    QTreeWidgetItem, QTextEdit, QMessageBox, 
)

from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

APP_VERSION = "1.01"

def resource_path(relative_path):

    # When running as a PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    # When running from source
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


class BackupApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowIcon(QIcon(resource_path("assets/icon.ico")))
        self.setWindowTitle(f"Easy Backup Tool - v{APP_VERSION}")
        self.setFixedSize(1024, 800)

        # --- Background Image ---
        self.bg_label = QLabel(self)
        bg_path = resource_path("assets/background.png") 
        if os.path.exists(bg_path):
            pixmap = QPixmap(bg_path)
            self.bg_label.setPixmap(
                pixmap.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )

        self.bg_label.setGeometry(0, 0, self.width(), self.height()) #self.bg_label.setGeometry(0, 0, 1150, 800)
        self.bg_label.setObjectName("BackgroundImage")

        # --- Central Widget ---
        central = QWidget(self)
        self.setCentralWidget(central)
        central.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # --- Main Layout ---
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # -----------------------------------------------------------
        # LEFT PANEL (Controls)
        # -----------------------------------------------------------
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_panel.setStyleSheet("""
            background-color: rgba(0, 0, 0, 120);
            border-radius: 10px;
        """)
        left_layout = QVBoxLayout(left_panel)

        logo_path = resource_path("assets/logo.png") #logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet("background-color: transparent;")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(
                180, 180,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.logo_label.setPixmap(scaled_logo)
        left_layout.addWidget(self.logo_label)

        title = QLabel("Backup Flow")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background-color: transparent;")
        left_layout.addWidget(title)

        self.btn_dest = QPushButton("1. Select External HDD")
        self.btn_dest.clicked.connect(self.select_dest)
        left_layout.addWidget(self.btn_dest)

        self.btn_source = QPushButton("2. Add Source Folders")
        self.btn_source.clicked.connect(self.add_sources)
        left_layout.addWidget(self.btn_source)

        self.btn_run = QPushButton("🚀 Start Backup")
        self.btn_run.clicked.connect(self.run_backup)
        left_layout.addWidget(self.btn_run)

        util_title = QLabel("Utilities")
        util_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-top: 20px; background-color: transparent;")
        left_layout.addWidget(util_title)

        self.btn_compare = QPushButton("🔍 Analyze Changes")
        self.btn_compare.clicked.connect(self.run_comparison)
        left_layout.addWidget(self.btn_compare)

        self.btn_unlock = QPushButton("🔓 Unlock Repository")
        self.btn_unlock.clicked.connect(self.manual_unlock)
        left_layout.addWidget(self.btn_unlock)

        self.btn_lock = QPushButton("🔒 Lock Repository")
        self.btn_lock.clicked.connect(self.manual_lock)
        left_layout.addWidget(self.btn_lock)

        self.btn_clear = QPushButton("Clear Session List")
        self.btn_clear.clicked.connect(self.clear_list)
        left_layout.addWidget(self.btn_clear)

        left_layout.addStretch()

        self.btn_about = QPushButton("About EBT")
        self.btn_about.clicked.connect(self.show_about) 
        left_layout.addWidget(self.btn_about)
        
        self.btn_how = QPushButton("How to use it")
        self.btn_how.clicked.connect(self.show_how) 
        left_layout.addWidget(self.btn_how)
      
      
        # -----------------------------------------------------------
        # RIGHT PANEL (TreeView + Log)
        # -----------------------------------------------------------
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: rgba(0, 0, 0, 120); border-radius: 10px;")
        right_layout = QVBoxLayout(right_panel)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Folder Name", "Last Backup Date"])
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: rgba(20, 20, 20, 180);
                color: white;
                border: none;
            }
            QHeaderView::section {
                background-color: rgba(50, 50, 50, 200);
                color: white;
            }
        """)
        tree_title = QLabel("Tree View")
        tree_title.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")        
        right_layout.addWidget(tree_title)
        
        right_layout.addWidget(self.tree)
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
            color: white;
            font-family: Consolas;
            font-size: 12px;
        """)
       
        log_title = QLabel("Log Output")
        log_title.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")        
        right_layout.addWidget(log_title)
        
        right_layout.addWidget(self.log_box)
       
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        # Data
        self.source_folders = []
        self.destination_hdd = None

    # -----------------------------------------------------------
    # Helpers – same logic, PyQt UI
    # -----------------------------------------------------------
    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.append(f"[{timestamp}] {message}")
        self.log_box.ensureCursorVisible()

    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024

    def get_free_space(self, path):
        _, _, free = shutil.disk_usage(path)
        return free

    def set_protection(self, path, protect=True):
        ATTR_READONLY, ATTR_SYSTEM, ATTR_NORMAL = 0x01, 0x04, 0x80
        if os.path.exists(path):
            attrs = (ATTR_READONLY | ATTR_SYSTEM) if protect else ATTR_NORMAL
            try:
                ctypes.windll.kernel32.SetFileAttributesW(path, attrs)
            except Exception as e:
                self.log(f"Windows attribute error on {path}: {e}")

    def get_manifest_data(self):
        hdd_root = self.destination_hdd
        if not hdd_root:
            return {}, ""
        manifest_path = os.path.join(hdd_root, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                try:
                    return json.load(f), manifest_path
                except Exception:
                    return {}, manifest_path
        return {}, manifest_path

    # -----------------------------------------------------------
    # UI Actions
    # -----------------------------------------------------------
    def add_sources(self):
        adding = True
        while adding:
            path = QFileDialog.getExistingDirectory(self, "Select Folder to Add")
            if path:
                if path not in self.source_folders:
                    self.source_folders.append(path)
                    self.log(f"Added: {path}")
                reply = QMessageBox.question(
                    self,
                    "Add More?",
                    "Folder added. Add another?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                adding = reply == QMessageBox.StandardButton.Yes
            else:
                adding = False

    def select_dest(self):
        path = QFileDialog.getExistingDirectory(self, "Select External HDD")
        if path:
            self.destination_hdd = path
            self.log(f"HDD Target: {path}")
            manifest, _ = self.get_manifest_data()
            for s in manifest.get("source_paths", []):
                if s not in self.source_folders:
                    self.source_folders.append(s)
            self.refresh_explorer()

    def refresh_explorer(self):
        self.tree.clear()
        manifest, _ = self.get_manifest_data()
        repo_dates = manifest.get("folder_backups", {})
        if not self.destination_hdd:
            return
        repo_path = os.path.join(self.destination_hdd, "Backup_Repository")
        if os.path.exists(repo_path):
            for folder in os.listdir(repo_path):
                full = os.path.join(repo_path, folder)
                if os.path.isdir(full):
                    date = repo_dates.get(folder, "Unknown")
                    item = QTreeWidgetItem([f"📂 {folder}", date])
                    self.tree.addTopLevelItem(item)

    # -----------------------------------------------------------
    # Conflict resolution dialog (PyQt version)
    # -----------------------------------------------------------
    def ask_conflict_resolution(self, filename: str) -> str:
        msg = QMessageBox(self)
        msg.setWindowTitle("File Conflict")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(
            f"Conflict detected for:\n{filename}\n\n"
            "The source file is newer. What would you like to do?"
        )
        replace_btn = msg.addButton("Replace", QMessageBox.ButtonRole.AcceptRole)
        keep_both_btn = msg.addButton("Keep Both", QMessageBox.ButtonRole.AcceptRole)
        skip_btn = msg.addButton("Skip", QMessageBox.ButtonRole.RejectRole)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == replace_btn:
            return "replace"
        elif clicked == keep_both_btn:
            return "keep_both"
        else:
            return "skip"

    # -----------------------------------------------------------
    # Analysis
    # -----------------------------------------------------------
    def run_comparison(self):
        manifest, _ = self.get_manifest_data()
        sources = self.source_folders if self.source_folders else manifest.get("source_paths", [])
        if not sources:
            QMessageBox.warning(self, "Warning", "No HDD or Source selected.")
            return

        self.log("--- Analyzing Changes ---")
        new, updated, total_required_size = 0, 0, 0
        missing_files, found_on_pc = [], set()

        for folder in sources:
            if not os.path.exists(folder):
                continue
            f_name = os.path.basename(folder)
            for root, _, files in os.walk(folder):
                for f in files:
                    file_path = os.path.join(root, f)
                    rel = os.path.join(f_name, os.path.relpath(file_path, folder))
                    found_on_pc.add(rel)

                    mtime = os.path.getmtime(file_path)
                    f_size = os.path.getsize(file_path)
                    stored_mtime = manifest.get("files", {}).get(rel)

                    if not stored_mtime or mtime > stored_mtime:
                        if not stored_mtime:
                            new += 1
                        else:
                            updated += 1
                        total_required_size += f_size

        for rel in manifest.get("files", {}).keys():
            if rel not in found_on_pc:
                missing_files.append(rel)

        self.log(f"Status: {new} New, {updated} Updated, {len(missing_files)} Missing.")
        for m in missing_files:
            self.log(f"  [MISSING] {m}")

        QMessageBox.information(
            self,
            "Analysis Complete",
            f"Space Required: {self.format_size(total_required_size)}\n"
            f"New: {new}\nUpdated: {updated}"
        )

    # -----------------------------------------------------------
    # Backup
    # -----------------------------------------------------------
    def run_backup(self):
        if not self.destination_hdd or not self.source_folders:
            QMessageBox.critical(self, "Error", "Setup incomplete.")
            return

        self.log("🔍 Scanning for changes...")
        manifest, manifest_path = self.get_manifest_data()
        sources = self.source_folders
        new_files, updated_files, total_size_to_copy = 0, 0, 0
        found_on_pc = set()
        pending_work = []

        for folder in sources:
            if not os.path.exists(folder):
                continue
            f_name = os.path.basename(folder)
            for root, _, files in os.walk(folder):
                for f in files:
                    s_path = os.path.join(root, f)
                    rel = os.path.join(f_name, os.path.relpath(s_path, folder))
                    found_on_pc.add(rel)

                    s_mtime = os.path.getmtime(s_path)
                    f_size = os.path.getsize(s_path)
                    stored_mtime = manifest.get("files", {}).get(rel)

                    if not stored_mtime or s_mtime > stored_mtime:
                        if not stored_mtime:
                            new_files += 1
                        else:
                            updated_files += 1
                        total_size_to_copy += f_size
                        pending_work.append((s_path, rel, s_mtime))

        if not pending_work:
            self.log("✨ All folders are identical to backup. Nothing to copy.")
            QMessageBox.information(self, "Status", "Everything is already up to date!")
            return

        free_space = self.get_free_space(self.destination_hdd)
        if total_size_to_copy > free_space:
            self.log(
                f"❌ ERROR: Insufficient space. Need {self.format_size(total_size_to_copy)} "
                f"but only {self.format_size(free_space)} is free."
            )
            QMessageBox.critical(
                self,
                "Disk Space Error",
                f"Not enough space!\nRequired: {self.format_size(total_size_to_copy)}\n"
                f"Available: {self.format_size(free_space)}"
            )
            return

        self.btn_run.setEnabled(False)
        self.btn_run.setText("Running...")
        self.log(f"🚀 Found {len(pending_work)} items to process ({self.format_size(total_size_to_copy)})...")

        try:
            hdd_root = self.destination_hdd
            repo_path = os.path.join(hdd_root, "Backup_Repository")

            if "files" not in manifest:
                manifest["files"] = {}
            if "folder_backups" not in manifest:
                manifest["folder_backups"] = {}
            manifest["source_paths"] = list(set(self.source_folders + manifest.get("source_paths", [])))

            if not os.path.exists(repo_path):
                os.makedirs(repo_path)
            self.set_protection(repo_path, False)

            for s_path, rel, s_mtime in pending_work:
                d_path = os.path.join(repo_path, rel)

                if os.path.exists(d_path):
                    d_mtime = os.path.getmtime(d_path)
                    if s_mtime > d_mtime:
                        choice = self.ask_conflict_resolution(rel)
                        if choice == "skip":
                            continue
                        elif choice == "keep_both":
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            name, ext = os.path.splitext(d_path)
                            d_path = f"{name}_{timestamp}{ext}"
                            rel = f"{os.path.splitext(rel)[0]}_{timestamp}{ext}"

                os.makedirs(os.path.dirname(d_path), exist_ok=True)
                self.set_protection(os.path.dirname(d_path), False)
                shutil.copy2(s_path, d_path)
                self.set_protection(d_path, True)
                manifest["files"][rel] = s_mtime
                self.log(f"Saved: {rel}")
                QApplication.processEvents()

            for folder in self.source_folders:
                manifest["folder_backups"][os.path.basename(folder)] = datetime.now().strftime("%Y-%m-%d %H:%M")

            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=4)

            self.set_protection(repo_path, True)
            self.log("✅ Backup Successful.")
            self.refresh_explorer()
        except Exception as e:
            self.log(f"❌ Error: {e}")
        finally:
            self.btn_run.setEnabled(True)
            self.btn_run.setText("🚀 Start Backup")

    # -----------------------------------------------------------
    # Lock / Unlock / Clear
    # -----------------------------------------------------------
    def manual_unlock(self):
        hdd_root = self.destination_hdd
        if hdd_root:
            repo_path = os.path.join(hdd_root, "Backup_Repository")
            if os.path.exists(repo_path):
                self.set_protection(repo_path, False)
                for root, dirs, files in os.walk(repo_path):
                    for d in dirs:
                        self.set_protection(os.path.join(root, d), False)
                    for f in files:
                        self.set_protection(os.path.join(root, f), False)
                self.log("🔓 Repository fully UNLOCKED.")

    def manual_lock(self):
        hdd_root = self.destination_hdd
        if hdd_root:
            repo_path = os.path.join(hdd_root, "Backup_Repository")
            if os.path.exists(repo_path):
                for root, dirs, files in os.walk(repo_path):
                    for d in dirs:
                        self.set_protection(os.path.join(root, d), True)
                    for f in files:
                        self.set_protection(os.path.join(root, f), True)
                self.set_protection(repo_path, True)
                self.log("🔒 Repository fully LOCKED.")

    def clear_list(self):
        self.source_folders = []
        self.log("Session cleared.")

    def show_about(self):
        about = QMessageBox(self)
        about.setWindowTitle("About Easy Backup Tool")
        about.setIcon(QMessageBox.Icon.Information)
        
        about.setTextFormat(Qt.TextFormat.RichText)
        about.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        
        about.setText(
            "<h2>Easy Backup Tool (EBT)</h2>"
            f"<p><b>Version:</b> {APP_VERSION}</p>"
            "<p><b>Author:</b> diegudio</p>"
            "<p>Easy Backup Tool (aka EBT) is a tool designed to make "
            "incremental backups simple, safe, and transparent.</p>"
            "<p>EBT performs incremental backups, meaning only new or modified files are copied, "
            "saving time and space. The backup history information is saved in a manifest file "
            "in the selected backup drive.</p>"
            "<p>EBT is not a professional back-up tool, but just a utility that makes the "
            "process of keeping back-ups easier for the home user.</p>"

            "<p><b>Main Features:</b></p>"
            "<ul>"
            "<li>Incremental file synchronization</li>"
            "<li>Automatic change detection</li>"
            "<li>Repository explorer with history</li>"
            "<li>File protection against accidental deletion</li>"
            "<li>Space‑aware backup validation</li>"
            "</ul>"
            
            "<p>EBT is a multiplatform tool. The baseline script can be found in this "
            "<a href='https://github.com/diegudio-real/easy_backup_tool'>"
            "<b>GitHub repository</b></a></p>"
                 
            "<p>EBT is licensed under "
            "<a href='https://www.gnu.org/licenses/agpl-3.0.en.html'>"
            "<b>GNU Affero General Public License v3.0</b></a></p>"
            
            "<p>If you enjoy this tool and want to support development, "
            "you can "
            "<a href='https://paypal.me/diegorodriguez1978'>"
            "<b>donate via PayPal</b></a></p>"
            "</ul>"
            ""
            "<p>Thank you for donating!</p>"
            "<p>&nbsp;</p>"        
            "<div style='font-size: 10px;'><b>Software Disclaimer</b></div>"
            "<div style='font-size: 09px;'>"
            "<p>Easy Backup Tool (EBT) is provided “as is” without any warranties of any kind. "
            "The user is solely responsible for the accuracy, integrity, and security of their own data, "
            "including all files selected for backup or restoration. "
            "EBT does not guarantee that the software will operate without interruption, errors, "
            "or unexpected behavior. No warranty or assurance—express, implied, or statutory—is provided "
            "regarding performance, reliability, data handling, or suitability for any particular purpose. "
            "The user acknowledges that all backup operations involve inherent risks, including but not "
            "limited to data corruption, transmission errors, hardware failures, or misconfiguration. "
            "By using EBT, the user accepts full responsibility for verifying backup results and ensuring "
            "that their storage devices and system environment are functioning correctly. "
            "The developer of EBT shall not be held liable for any loss of data, damages, or issues "
            "arising from the use or inability to use the software.</p>"
            "</div>"
        )
        
        # Optional: add a custom OK button
        about.setStandardButtons(QMessageBox.StandardButton.Ok)

        about.exec()

    def show_how(self):
        about = QMessageBox(self)
        about.setWindowTitle("How to")
        about.setIcon(QMessageBox.Icon.Information)

        about.setText(
            f"<h2>How to use Easy Backup Tool (EBT)</h2><p><b>Version:</b> {APP_VERSION}</p>"
            
            "<ol>"
            "<li><b>Select External HDD</b><br>"
            "Choose the drive where your backup repository will be stored.</li>"
            "<li><b>Add Source Folders</b><br>"
            "Pick one or more folders from your PC that you want to back-up.</li>"
            "<li><b>Analyze Changes (optional)</b><br>"
            "See what files are new, updated, or missing before running a backup.</li>"
            "<li><b>Start Backup</b><br>"
            "EBT scans your folders, copies only changed files, and updates the manifest.</li>"
            "<li><b>Lock / Unlock Repository (optional)</b><br>"
            "Use these tools to protect your backup from accidental deletion.</li>"
            "</ol>"
            "<p>If you enjoy this tool and want to support development, "
            "you can "
            "<a href='https://paypal.me/diegorodriguez1978'>"
            "<b>donate via PayPal</b></a></p>"
            "</ul>"     
        )

        # Optional: add a custom OK button
        about.setStandardButtons(QMessageBox.StandardButton.Ok)

        about.exec()

# QApplication Styling
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QPushButton {
            background-color: rgba(255, 255, 255, 40);
            color: white;
            font-size: 15px;
            font-weight: bold;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 60);
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 70);
        }
        QPushButton:disabled {
            background-color: rgba(255, 255, 255, 20);
            color: rgba(255, 255, 255, 80);
        }

        
        /* Default label styling */
        QLabel {
            color: white;
        }

        /* Background image label override */
        #BackgroundImage {
            background-color: transparent;
            color: transparent;
            border: none;
        }

 
        QTreeWidget {
            background-color: rgba(30, 30, 30, 180);
            color: white;
            border-radius: 8px;
            padding: 5px;
        }
        
        QHeaderView::section {
            background-color: rgba(60, 60, 60, 200);
            color: white;
            padding: 5px;
            border: none;
        }

        QTextEdit {
            background-color: rgba(0, 0, 0, 150);
            color: white;
            border-radius: 8px;
            padding: 8px;
            font-family: Consolas;
            font-size: 13px;
        }
        
        QMessageBox {
            background-color: #2b2b2b;
            color: white;
            font-size: 14px;
        }
        QMessageBox QLabel {
            color: white;
            font-size: 14px;
        }
        QMessageBox QPushButton {
            background-color: rgba(255, 255, 255, 40);
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 60);
            font-weight: bold;
        }
        QMessageBox QPushButton:hover {
            background-color: rgba(255, 255, 255, 70);
        }
""")


    window = BackupApp()
    window.show()
    sys.exit(app.exec())
