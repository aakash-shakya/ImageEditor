import sys
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QWidget,
    QSlider,
    QStatusBar,
    QMenuBar,
    QAction,
    QDockWidget,
    QScrollArea,
    QGridLayout,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
    QSplitter,
)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor, QPalette
from PyQt5.QtCore import Qt, QSize

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="image_editor.log",
)


class ThemeManager:
    DARK_STYLESHEET = """
    QMainWindow {
        background-color: #3c3f41;
        color: #ffffff;
    }
    QLabel {
        color: #ffffff;
        background-color: transparent;
    }
    QTreeWidget {
        background-color: #3c3f41;
        color: #ffffff;
        border: 1px solid #555;
    }
    QTreeWidget::item {
        background-color: #3c3f41;
        color: #ffffff;
    }
    QTreeWidget::item:selected {
        background-color: #4c5052;
    }
    QDockWidget {
        background-color: #3c3f41;
        color: #ffffff;
    }
    QPushButton {
        background-color: #3c3f41;
        color: #ffffff;
        border: 1px solid #555;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #4c5052;
    }
    QSlider {
        background-color: transparent;
    }
    QSlider::groove:horizontal {
        background-color: #FF5733;
        height: 8px;
    }
    QSlider::handle:horizontal {
        background-color: #ffffff;
        width: 18px;
        margin: -5px 0;
        border-radius: 9px;
    }
    QMenuBar {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QMenuBar::item {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QMenuBar::item:selected {
        background-color: #4c5052;
    }
    QMenu {
        background-color: #2b2b2b;
        color: #ffffff;
        border: 1px solid #555;
    }
    QMenu::item:selected {
        background-color: #4c5052;
    }
    QScrollArea {
        background-color: #1e1e1e;
        border: none;
    }
    QSplitter::handle {
        background-color: #555555;
    }
    """

    LIGHT_STYLESHEET = """
    QMainWindow {
        background-color: #ffffff;
        color: #000000;
    }
    QLabel {
        color: #000000;
    }
    QTreeWidget {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #cccccc;
    }
    QTreeWidget::item {
        background-color: #ffffff;
        color: #000000;
    }
    QTreeWidget::item:selected {
        background-color: #e0e0e0;
    }
    QDockWidget {
        background-color: #f0f0f0;
        color: #000000;
    }
    QPushButton {
        background-color: #e0e0e0;
        color: #000000;
        border: 1px solid #cccccc;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #d0d0d0;
    }
    QSlider::groove:horizontal {
        background-color: #5D3FD3;
        height: 8px;
    }
    QSlider::handle:horizontal {
        background-color: #6F8FAF;
        width: 18px;
        margin: -5px 0;
        border-radius: 9px;
    }
    QMenuBar {
        background-color: #f0f0f0;
        color: #000000;
    }
    QMenuBar::item {
        background-color: #f0f0f0;
        color: #000000;
    }
    QMenuBar::item:selected {
        background-color: #e0e0e0;
    }
    QMenu {
        background-color: #f0f0f0;
        color: #000000;
        border: 1px solid #cccccc;
    }
    QMenu::item:selected {
        background-color: #e0e0e0;
    }
    QScrollArea {
        background-color: #ffffff;
        border: black;
    }
    QSplitter::handle {
        background-color: #cccccc;
    }
    """


class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Image Editor")
        self.resize(1600, 900)

        # Theme management
        self.current_theme = "light"

        # Image management
        self.original_image = None
        self.current_image = None
        self.image_history = []
        self.history_index = -1

        # Setup UI components
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_dock_widgets()
        self.setup_status_bar()

        # Apply default theme
        self.apply_theme(self.current_theme)

    def setup_menus(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")
        file_actions = [
            ("&Open", self.open_image, "Ctrl+O"),
            ("&Save", self.save_image, "Ctrl+S"),
            ("Save &As", self.save_image_as, "Ctrl+Shift+S"),
            ("&Exit", self.close, "Ctrl+Q"),
        ]

        for text, method, shortcut in file_actions:
            action = QAction(text, self)
            action.setShortcut(shortcut)
            action.triggered.connect(method)
            file_menu.addAction(action)

        # Preferences Menu
        pref_menu = menubar.addMenu("&Preferences")

        # Theme Submenu
        theme_menu = pref_menu.addMenu("Theme")

        # Create theme actions dynamically
        self.theme_actions = {}
        themes = {"light": "Switch to Light Theme", "dark": "Switch to Dark Theme"}

        for theme, text in themes.items():
            # Only show the opposite of current theme
            action = QAction(text, self)
            action.triggered.connect(lambda checked, t=theme: self.apply_theme(t))
            self.theme_actions[theme] = action
            theme_menu.addAction(action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        edit_actions = [
            ("Undo", self.undo, "Ctrl+Z"),
            ("Redo", self.redo, "Ctrl+Y"),
            ("Cut", None, "Ctrl+X"),
            ("Copy", None, "Ctrl+C"),
            ("Paste", None, "Ctrl+V"),
        ]

        for text, method, shortcut in edit_actions:
            action = QAction(text, self)
            action.setShortcut(shortcut)
            if method:
                action.triggered.connect(method)
            else:
                action.setEnabled(False)
            edit_menu.addAction(action)

    def apply_theme(self, theme):
        """Apply the selected theme to the application."""
        self.current_theme = theme
        if theme == "dark":
            self.setStyleSheet(ThemeManager.DARK_STYLESHEET)
        else:
            self.setStyleSheet(ThemeManager.LIGHT_STYLESHEET)

        # Update the preferences menu to show the correct theme option
        for t, action in self.theme_actions.items():
            action.setVisible(t != theme)

        logging.info(f"Theme changed to: {theme}")

    def setup_ui(self):
        # Create main central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # Create splitter for flexible layout
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setSizes([250, 1000])  # Set initial sizes for the splitter

        # History Tree Widget (Left Side)
        self.history_tree = QTreeWidget()
        self.history_tree.setHeaderLabels(["Action", "Timestamp"])
        self.history_tree.setMaximumWidth(250)

        # Scroll Area for Image (Center)
        self.scroll_area = QScrollArea()
        self.image_label = QLabel("Open an image to start editing")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)

        # Add widgets to splitter
        self.splitter.addWidget(self.history_tree)
        self.splitter.addWidget(self.scroll_area)

        # Set splitter stretch factors
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 4)

        # Set central layout
        main_layout.addWidget(self.splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def setup_toolbars(self):
        toolbar = self.addToolBar("Image Tools")
        tools = [
            ("Open", self.open_image, "open_icon.png"),
            ("Save", self.save_image, "save_icon.png"),
            ("Undo", self.undo, "undo_icon.png"),
            ("Redo", self.redo, "redo_icon.png"),
        ]

        for name, method, icon_path in tools:
            action = QAction(
                QIcon(icon_path) if os.path.exists(icon_path) else QIcon(), name, self
            )
            action.triggered.connect(method)
            toolbar.addAction(action)

    def adjust_dock_height(self, dock_widget, height):
        """Adjust the height of the specified QDockWidget."""
        # Set minimum and maximum height
        dock_widget.setMinimumHeight(height)
        dock_widget.setMaximumHeight(height)

        # Resize the dock widget
        dock_widget.resize(dock_widget.width(), height)

    def setup_dock_widgets(self):
        # Adjustments Dock (Right Side)
        adjustments_dock = QDockWidget("Adjustments", self)
        adjustments_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Sliders for image adjustments
        adjustment_types = [
            ("Brightness", 0, 200, 100),
            ("Contrast", 0, 200, 100),
            ("Saturation", 0, 200, 100),
        ]

        for name, min_val, max_val, default in adjustment_types:
            slider = QSlider(Qt.Horizontal)
            slider.setRange(min_val, max_val)
            slider.setValue(default)
            slider.setFixedHeight(18)
            slider.valueChanged.connect(
                lambda value, n=name: self.adjust_image(n, value)
            )
            label = QLabel(name)
            label.setFixedHeight(20)
            layout.addWidget(label)
            layout.addWidget(slider)

        adjustments_widget.setLayout(layout)
        adjustments_dock.setWidget(adjustments_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, adjustments_dock)
        self.adjust_dock_height(adjustments_dock, 300)

        # Filters Dock (Right Side)
        filters_dock = QDockWidget("Filters", self)
        filters_widget = QWidget()
        filters_layout = QGridLayout()

        filters = [
            ("Grayscale", self.apply_grayscale),
            ("Blur", self.apply_blur),
            ("Sharpen", self.apply_sharpen),
            ("Negative", self.apply_negative),
        ]

        for i, (filter_name, method) in enumerate(filters):
            btn = QPushButton(filter_name)
            btn.clicked.connect(method)
            filters_layout.addWidget(btn, i // 4, i % 4)

        filters_widget.setLayout(filters_layout)
        filters_dock.setWidget(filters_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, filters_dock)

    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def log_activity(self, action_name):
        """Log an activity to the history tree widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        item = QTreeWidgetItem(self.history_tree)
        item.setText(0, action_name)
        item.setText(1, timestamp)

        # Keep only last 20 history entries
        if self.history_tree.topLevelItemCount() > 20:
            self.history_tree.takeTopLevelItem(0)

    def open_image(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
            )
            if file_path:
                logging.info(f"Opening image: {file_path}")
                self.original_image = Image.open(file_path)
                self.current_image = self.original_image.copy()
                self.add_to_history(self.current_image)
                self.display_image(self.current_image)
                self.status_bar.showMessage(
                    f"Opened: {os.path.basename(file_path)}", 3000
                )

                # Log activity
                self.log_activity("Open Image")
        except Exception as e:
            logging.error(f"Error opening image: {str(e)}")
            self.show_error(f"Error opening image: {str(e)}")

    def display_image(self, image):
        try:
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)

            qimage = QImage()
            qimage.loadFromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(qimage)

            scaled_pixmap = pixmap.scaled(
                self.scroll_area.width(),
                self.scroll_area.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

            self.image_label.setPixmap(scaled_pixmap)
        except Exception as e:
            logging.error(f"Error displaying image: {str(e)}")
            self.show_error(f"Error displaying image: {str(e)}")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def save_image(self):
        if self.current_image:
            try:
                self.current_image.save("temp_image.png")
                self.status_bar.showMessage("Image saved as temp_image.png", 3000)

                # Log activity
                self.log_activity("Save Image")
            except Exception as e:
                logging.error(f"Error saving image: {str(e)}")
                self.show_error(f"Error saving image: {str(e)}")

    def save_image_as(self):
        if self.current_image:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
            )
            if file_path:
                try:
                    self.current_image.save(file_path)
                    self.status_bar.showMessage(
                        f"Image saved as: {os.path.basename(file_path)}", 3000
                    )

                    # Log activity
                    self.log_activity("Save Image As")
                except Exception as e:
                    logging.error(f"Error saving image: {str(e)}")
                    self.show_error(f"Error saving image: {str(e)}")

    def add_to_history(self, image):
        if self.history_index < len(self.image_history) - 1:
            self.image_history = self.image_history[: self.history_index + 1]

        self.image_history.append(image)
        self.history_index += 1

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.image_history[self.history_index]
            self.display_image(self.current_image)

            # Log activity
            self.log_activity("Undo Action")

    def redo(self):
        if self.history_index < len(self.image_history) - 1:
            self.history_index += 1
            self.current_image = self.image_history[self.history_index]
            self.display_image(self.current_image)

            # Log activity
            self.log_activity("Redo Action")

    def adjust_image(self, adjustment_type, value):
        if self.current_image:
            try:
                if adjustment_type == "Brightness":
                    enhancer = ImageEnhance.Brightness(self.current_image)
                    enhanced_image = enhancer.enhance(value / 100)
                elif adjustment_type == "Contrast":
                    enhancer = ImageEnhance.Contrast(self.current_image)
                    enhanced_image = enhancer.enhance(value / 100)
                elif adjustment_type == "Saturation":
                    enhancer = ImageEnhance.Color(self.current_image)
                    enhanced_image = enhancer.enhance(value / 100)
                else:
                    return

                self.add_to_history(enhanced_image)
                self.display_image(enhanced_image)

                # Log activity
                self.log_activity(f"{adjustment_type} Adjustment")
            except Exception as e:
                self.show_error(f"Error adjusting image: {str(e)}")

    def apply_grayscale(self):
        if self.current_image:
            try:
                self.current_image = self.current_image.convert("L")
                self.add_to_history(self.current_image)
                self.display_image(self.current_image)

                # Log activity
                self.log_activity("Grayscale Filter")
            except Exception as e:
                self.show_error(f"Error applying grayscale: {str(e)}")

    def apply_blur(self):
        if self.current_image:
            try:
                self.current_image = self.current_image.filter(ImageFilter.BLUR)
                self.add_to_history(self.current_image)
                self.display_image(self.current_image)

                # Log activity
                self.log_activity("Blur Filter")
            except Exception as e:
                self.show_error(f"Error applying blur: {str(e)}")

    def apply_sharpen(self):
        if self.current_image:
            try:
                self.current_image = self.current_image.filter(ImageFilter.SHARPEN)
                self.add_to_history(self.current_image)
                self.display_image(self.current_image)

                # Log activity
                self.log_activity("Sharpen Filter")
            except Exception as e:
                self.show_error(f"Error applying sharpen: {str(e)}")

    def apply_negative(self):
        if self.current_image:
            try:
                self.current_image = ImageOps.invert(self.current_image)
                self.add_to_history(self.current_image)
                self.display_image(self.current_image)

                # Log activity
                self.log_activity("Negative Filter")
            except Exception as e:
                self.show_error(f"Error applying negative: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = ImageEditor()
    editor.show()
    sys.exit(app.exec_())
