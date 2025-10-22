from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal, Slot, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..analysis.runner import run_analysis


class AnalysisWorkerSignals(QObject):
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(str)


class AnalysisWorker(QRunnable):
    def __init__(self, config_path, log_path, data_root, output_dir, auto_export):
        super().__init__()
        self.config_path = config_path
        self.log_path = log_path
        self.data_root = data_root
        self.output_dir = output_dir
        self.auto_export = auto_export
        self.signals = AnalysisWorkerSignals()

    @Slot()
    def run(self):
        try:
            result = run_analysis(
                config_path=self.config_path,
                log_path=self.log_path,
                data_root=self.data_root,
                output_dir=self.output_dir,
                auto_export=self.auto_export,
                progress=self.signals.progress.emit,
            )
            self.signals.finished.emit(result)
        except Exception as exc:  # pylint: disable=broad-except
            self.signals.error.emit(str(exc))


class ConfigEditorDialog(QDialog):
    config_saved = Signal(str)

    def __init__(self, parent, template_path: Path):
        super().__init__(parent)
        self.setWindowTitle("Edit Default Configuration")
        self.resize(600, 500)
        self._template_path = template_path

        layout = QVBoxLayout(self)

        self.editor = QPlainTextEdit()
        self.editor.setPlainText(self._load_template())
        layout.addWidget(self.editor)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        save_button = self.button_box.addButton("Save As...", QDialogButtonBox.ActionRole)
        save_button.clicked.connect(self._save_config)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _load_template(self) -> str:
        if self._template_path and self._template_path.exists():
            try:
                return self._template_path.read_text(encoding="utf-8")
            except Exception:  # pragma: no cover - fallback used rarely
                pass
        return (
            "General:\n"
            "  app_name: load_cell_calculation\n"
            "  version: 2.2\n"
            "  link: https://github.com/shoetify/LoadCell_Analysis\n\n"
            "Data_reading:\n\n"
            "  WindSpeed_relationship: y=0.1726x-0.06956\n\n"
            "  Sample_rate: 1000\n\n"
            "  Stable_time_0Hz: 50\n\n"
            "  Stable_time_others: 15\n\n"
            "  Gap_before_next_wind_speed: 2\n\n"
            "Data_calculation:\n\n"
            "  polynomial_fitting_degree: 1\n\n"
            "  smoothy_average_points: 1\n\n"
            "  lowpass_filtered_frequency: 0\n\n"
            "  cylinder_diameter: 0.06\n\n"
            "  test_section_length: 1.32\n"
        )

    @Slot()
    def _save_config(self):
        initial_dir = str(self._template_path.parent if self._template_path else Path.cwd())
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save configuration as",
            initial_dir,
            "YAML Files (*.yaml *.yml)",
        )
        if not file_path:
            return

        try:
            Path(file_path).write_text(self.editor.toPlainText(), encoding="utf-8")
        except Exception as exc:  # pylint: disable=broad-except
            QMessageBox.critical(self, "Save failed", f"Could not save configuration:\n{exc}")
            return

        QMessageBox.information(self, "Configuration saved", f"Saved to:\n{file_path}")
        self.config_saved.emit(file_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Load Cell Analysis")
        self.thread_pool = QThreadPool.globalInstance()
        self.analysis_results = []
        self.analysis_payload = None
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = self._build_header()
        layout.addWidget(header)

        file_group = QGroupBox("Project Files")
        file_form = QFormLayout(file_group)

        self.config_edit, config_widget = self._create_config_picker()
        self.log_edit, log_btn = self._create_file_picker("Excel Files (*.xlsx)")
        self.data_dir_edit, data_btn = self._create_directory_picker()
        self.output_dir_edit, output_btn = self._create_directory_picker()

        file_form.addRow("Config file:", config_widget)
        file_form.addRow("Experiment log:", self._join_widget(self.log_edit, log_btn))
        file_form.addRow("Data directory:", self._join_widget(self.data_dir_edit, data_btn))
        file_form.addRow("Output directory (optional):", self._join_widget(self.output_dir_edit, output_btn))

        layout.addWidget(file_group)

        options_group = QGroupBox("Options")
        options_layout = QHBoxLayout(options_group)
        self.auto_export_check = QCheckBox("Export Excel summaries automatically")
        self.auto_export_check.setChecked(True)
        options_layout.addWidget(self.auto_export_check)
        options_layout.addStretch()
        layout.addWidget(options_group)

        run_layout = QHBoxLayout()
        self.run_button = QPushButton("Run Analysis")
        self.run_button.clicked.connect(self._handle_run_clicked)
        run_layout.addStretch()
        run_layout.addWidget(self.run_button)
        layout.addLayout(run_layout)

        splitter = QSplitter(Qt.Vertical)

        log_group = QGroupBox("Progress")
        log_layout = QVBoxLayout(log_group)
        self.progress_log = QPlainTextEdit()
        self.progress_log.setReadOnly(True)
        log_layout.addWidget(self.progress_log)

        result_group = QGroupBox("Results")
        result_layout = QVBoxLayout(result_group)

        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Dataset:"))
        self.dataset_combo = QComboBox()
        self.dataset_combo.currentIndexChanged.connect(self._update_result_table)
        selector_layout.addWidget(self.dataset_combo, stretch=1)
        self.open_export_button = QPushButton("Open Exported File")
        self.open_export_button.clicked.connect(self._open_export_file)
        self.open_export_button.setEnabled(False)
        selector_layout.addWidget(self.open_export_button)
        result_layout.addLayout(selector_layout)

        self.result_table = QTableWidget()
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setAlternatingRowColors(True)
        result_layout.addWidget(self.result_table)

        splitter.addWidget(log_group)
        splitter.addWidget(result_group)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter, stretch=1)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

    def _build_header(self):
        container = QGroupBox()
        container.setTitle("")
        header_layout = QHBoxLayout(container)
        header_layout.setContentsMargins(12, 12, 12, 12)
        header_layout.setSpacing(16)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        logo_path = Path(__file__).resolve().parents[2] / "assets" / "LOGO.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                scaled = pixmap.scaled(160, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled)
        else:
            logo_label.setText("LOGO.png not found")

        header_layout.addWidget(logo_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        info_text = (
            "Supervisor: Tongming Zhou\n"
            "Version: 1.0.0\n"
            "Supported email: difei.xiao@research.uwa.edu.au"
        )
        info_label = QLabel(info_text)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14pt;")
        info_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        header_layout.addWidget(info_label, stretch=1, alignment=Qt.AlignCenter)

        return container

    def _create_file_picker(self, filter_text):
        line = QLineEdit()
        button = QPushButton("Browse")

        def pick_file():
            current = line.text() or str(Path.cwd())
            path, _ = QFileDialog.getOpenFileName(self, "Select file", current, filter_text)
            if path:
                line.setText(path)

        button.clicked.connect(pick_file)
        return line, button

    def _create_config_picker(self):
        line = QLineEdit()
        browse_btn = QPushButton("Browse")
        edit_btn = QPushButton("Edit Default")

        def pick_file():
            current = line.text() or str(Path.cwd())
            path, _ = QFileDialog.getOpenFileName(self, "Select configuration file", current, "YAML Files (*.yaml *.yml)")
            if path:
                line.setText(path)

        def edit_default():
            dialog = ConfigEditorDialog(self, self._default_config_path())
            dialog.config_saved.connect(line.setText)
            dialog.exec()

        browse_btn.clicked.connect(pick_file)
        edit_btn.clicked.connect(edit_default)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(line, stretch=1)
        layout.addWidget(browse_btn)
        layout.addWidget(edit_btn)

        return line, container

    def _create_directory_picker(self):
        line = QLineEdit()
        button = QPushButton("Browse")

        def pick_directory():
            current = line.text() or str(Path.cwd())
            path = QFileDialog.getExistingDirectory(self, "Select directory", current)
            if path:
                line.setText(path)

        button.clicked.connect(pick_directory)
        return line, button

    @staticmethod
    def _join_widget(line_edit, button):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(line_edit, stretch=1)
        layout.addWidget(button)
        return container

    @Slot()
    def _handle_run_clicked(self):
        config_path = self.config_edit.text().strip()
        log_path = self.log_edit.text().strip()
        data_dir = self.data_dir_edit.text().strip()
        output_dir = self.output_dir_edit.text().strip()

        if not config_path or not log_path:
            QMessageBox.warning(self, "Missing information", "Please select both a config file and a log file.")
            return

        if not data_dir:
            data_dir = str(Path(log_path).parent)

        auto_export = self.auto_export_check.isChecked()

        self.progress_log.clear()
        self.status_label.setText("Running analysis...")
        self.run_button.setEnabled(False)
        self.dataset_combo.clear()
        self.result_table.clear()
        self.result_table.setRowCount(0)
        self.result_table.setColumnCount(0)
        self.analysis_results = []
        self.analysis_payload = None
        self.open_export_button.setEnabled(False)

        worker = AnalysisWorker(config_path, log_path, data_dir, output_dir or None, auto_export)
        worker.signals.progress.connect(self._append_progress)
        worker.signals.error.connect(self._handle_error)
        worker.signals.finished.connect(self._handle_finished)

        self.thread_pool.start(worker)

    @Slot(str)
    def _append_progress(self, message):
        self.progress_log.appendPlainText(message)
        self.progress_log.verticalScrollBar().setValue(self.progress_log.verticalScrollBar().maximum())

    @Slot(str)
    def _handle_error(self, message):
        self.run_button.setEnabled(True)
        self.status_label.setText("Analysis failed.")
        QMessageBox.critical(self, "Analysis failed", message)

    @Slot(object)
    def _handle_finished(self, payload):
        self.run_button.setEnabled(True)
        self.status_label.setText("Analysis completed successfully.")
        self.analysis_payload = payload
        self.analysis_results = payload.get("results", [])

        if not self.analysis_results:
            QMessageBox.information(self, "No results", "Analysis completed but no datasets were produced.")
            return

        for entry in self.analysis_results:
            self.dataset_combo.addItem(entry.name)

        self._update_result_table(0)

    @Slot(int)
    def _update_result_table(self, index):
        if index < 0 or index >= len(self.analysis_results):
            self.result_table.clear()
            self.result_table.setRowCount(0)
            self.result_table.setColumnCount(0)
            self.open_export_button.setEnabled(False)
            return

        entry = self.analysis_results[index]
        df = entry.dataframe

        self.result_table.setRowCount(len(df.index))
        self.result_table.setColumnCount(len(df.columns))
        self.result_table.setHorizontalHeaderLabels([str(col) for col in df.columns])

        for row_idx in range(len(df.index)):
            for col_idx, column in enumerate(df.columns):
                value = df.iloc[row_idx, col_idx]
                if isinstance(value, float):
                    display_value = f"{value:.4f}"
                else:
                    display_value = str(value)
                item = QTableWidgetItem(display_value)
                item.setTextAlignment(Qt.AlignCenter)
                self.result_table.setItem(row_idx, col_idx, item)

        self.result_table.resizeColumnsToContents()
        self.open_export_button.setEnabled(bool(entry.output_path))

    @Slot()
    def _open_export_file(self):
        index = self.dataset_combo.currentIndex()
        if index < 0 or index >= len(self.analysis_results):
            return

        entry = self.analysis_results[index]
        if not entry.output_path:
            QMessageBox.information(self, "No export available", "This dataset was not exported automatically.")
            return

        if not entry.output_path.exists():
            QMessageBox.warning(self, "File missing", f"Exported file not found:\n{entry.output_path}")
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(entry.output_path)))

    def _default_config_path(self) -> Path:
        candidate = Path(__file__).resolve().parents[2] / "config.yaml"
        return candidate if candidate.exists() else Path.cwd() / "config.yaml"


def launch():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(900, 700)
    window.show()
    app.exec()


if __name__ == "__main__":
    launch()
