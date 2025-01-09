import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QWidget,
    QSlider,
    QStatusBar,
    QAction,
    QDockWidget,
    QScrollArea,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
    QSplitter,
    QComboBox,
    QLineEdit,
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageEnhance
import io
from .themes import ThemeManager
from .delegates import DeleteIconDelegate
from .filters import Filter

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
        self.selected_parent = None

        # Setup UI components
        self.setup_ui()
        self.setup_menus()
        self.setup_dock_widgets()
        self.setup_status_bar()

        self.theme_manager = ThemeManager(self)

        # Apply default theme
        self.theme_manager.apply_theme(theme=self.current_theme, parent=self)

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
        theme_menu = pref_menu.addMenu("Theme")

        # Create theme actions dynamically
        self.theme_actions = {}
        themes = ThemeManager.config

        for theme, text in themes.items():
            action = QAction(text, self)
            action.triggered.connect(lambda checked, t=theme: ThemeManager.apply_theme(t, self))
            self.theme_actions[theme] = action
            theme_menu.addAction(action)

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

    def delete_item(self, index):
        """Delete the selected item from the history tree and update the image history."""
        item = self.history_tree.itemFromIndex(index)
        if item:
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                self.history_tree.takeTopLevelItem(self.history_tree.indexOfTopLevelItem(item))


            # Remove the corresponding image from the image history
            if 0 <= index.row() < len(self.image_history):
                self.image_history.pop(index.row())
                self.history_index = index.row()-1

            # Update the displayed image
            if self.image_history:
                self.current_image = self.image_history[self.history_index]
                self.display_image(self.current_image)
            else:
                self.current_image = None
                self.image_label.clear()
                self.image_label.setText("No image loaded")

            logging.info(f"Deleted action: {item.text(0)}")

    def setup_ui(self):
        # Create main central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 10, 0)

        # Create splitter for flexible layout
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setSizes([250, 1000])  # Set initial sizes for the splitter

        # History Tree Widget (Left Side)
        self.history_tree = QTreeWidget()
        self.history_tree.setHeaderLabels(["Action", "Timestamp"])
        self.history_tree.setIndentation(15)
        self.history_tree.setItemsExpandable(True)  
        self.history_tree.setExpandsOnDoubleClick(True) 
        self.history_tree.setMaximumWidth(250)
        self.history_tree.itemClicked.connect(self.set_selected_parent)
        self.history_tree_scrollable_area = QScrollArea()
        self.history_tree_scrollable_area.setWidget(self.history_tree)
        self.history_tree_scrollable_area.setWidgetResizable(True)
        self.history_tree.itemDoubleClicked.connect(self.rename_history_layer)


        self.history_tree.setItemDelegateForColumn(1, DeleteIconDelegate(self.history_tree, self))

        

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

    def set_selected_parent(self, item):
        """Set the clicked item as the selected parent."""
        self.selected_parent = item

    def adjust_dock_height(self, dock_widget,width, height):
        """Adjust the height of the specified QDockWidget."""
        # Set minimum and maximum height
        dock_widget.setMinimumHeight(height)
        dock_widget.setMaximumHeight(height)
        dock_widget.setMinimumWidth(width)

        # Resize the dock widget
        dock_widget.resize(dock_widget.width(), height)

    def setup_dock_widgets(self):
        # Adjustments Dock (Right Side)
        adjustments_dock = QDockWidget("Adjustments", self)
        adjustments_dock.setMaximumWidth(300)
        adjustments_widget = QWidget()
        layout = QVBoxLayout()

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
            slider.valueChanged.connect(lambda value, n=name: setattr(self, f"{n.lower()}_value", value))
            slider.sliderReleased.connect(lambda n=name: self.adjust_image(n, getattr(self, f"{n.lower()}_value")))
            label = QLabel(name)
            label.setFixedHeight(20)
            layout.addWidget(label)
            layout.addWidget(slider)

        adjustments_widget.setLayout(layout)
        adjustments_dock.setWidget(adjustments_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, adjustments_dock)
        self.adjust_dock_height(adjustments_dock, 250, 300)

        filters_widget = QWidget()
        filters_layout = QVBoxLayout()
        filters_layout.setSpacing(0) 
        filters_layout.setContentsMargins(0, 0, 0, 0) 

        self.filter_dropdown = QComboBox()
        self.filter_dropdown.setFixedHeight(30)
        self.filter_dropdown.addItems(["Grayscale", "Blur", "Sharpen", "Negative"])
        self.filter_dropdown.currentIndexChanged.connect(self.apply_filter_from_dropdown)
        filters_layout.addWidget(self.filter_dropdown)
        filters_widget.setLayout(filters_layout)

        filters_dock = QDockWidget("Filters", self)
        filters_dock.setWidget(filters_widget)
        self.adjust_dock_height(filters_dock, 250, 200)
        self.addDockWidget(Qt.RightDockWidgetArea, filters_dock)

    def apply_filter_from_dropdown(self, index):
        """Apply a filter based on the selected dropdown option."""
        filter_methods = {
            0: Filter.grayscale,
            1: Filter.blur,
            2: Filter.sharpen,
            3: Filter.negative
        }
        self.current_image = filter_methods.get(index)(self.current_image, self.add_to_history, self.display_image, self.log_activity, self.show_error)

    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def log_activity(self, action_name):
        """Log an activity to the history tree widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        child_item = QTreeWidgetItem([action_name, timestamp])

        if self.selected_parent:
            self.selected_parent.addChild(child_item)
            self.selected_parent.setExpanded(True)
            self.selected_parent = None
        else:
            self.history_tree.addTopLevelItem(child_item) 

        # keep only 50 action logs
        if self.history_tree.topLevelItemCount() > 50:
            self.history_tree.takeTopLevelItem(0)

        self.history_tree.clearSelection()

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


    def redo(self):
        if self.history_index < len(self.image_history) - 1:
            self.history_index += 1
            self.current_image = self.image_history[self.history_index]
            self.display_image(self.current_image)
    
    def adjust_image(self, adjustment_type, value):
        if self.current_image:
            try:
                if adjustment_type == "Brightness":
                    enhancer = ImageEnhance.Brightness(self.current_image)
                    self.current_image = enhancer.enhance(value / 100)
                elif adjustment_type == "Contrast":
                    enhancer = ImageEnhance.Contrast(self.current_image)
                    self.current_image = enhancer.enhance(value / 100)
                elif adjustment_type == "Saturation":
                    enhancer = ImageEnhance.Color(self.current_image)
                    self.current_image = enhancer.enhance(value / 100)
                else:
                    return

                self.add_to_history(self.current_image)
                self.display_image(self.current_image)

                # Log activity
                self.log_activity(f"{adjustment_type}")
            except Exception as e:
                self.show_error(f"Error adjusting image: {str(e)}")

    def rename_history_layer(self, item):
        self.rename_text_box = QLineEdit(item.text(0))
        self.rename_text_box.setText(item.text(0))
        self.rename_text_box.selectAll()
        self.rename_text_box.show()
        self.rename_text_box.setFocus()
        self.rename_text_box.returnPressed.connect(lambda: self.rename_history_layer_finish(item))
        self.history_tree.setItemWidget(item, 0, self.rename_text_box)

    def rename_history_layer_finish(self, item):
        new_name = self.rename_text_box.text()
        if new_name:
            item.setText(0, new_name)
        self.history_tree.setItemWidget(item, 0, None)
        self.rename_text_box.deleteLater()
        self.history_tree.clearSelection()

