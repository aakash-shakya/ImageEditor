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
        padding:3px;
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
    QMessageBox{
    background-color:#3c3f41;
    color:#fff;
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
    QTreeWidget::section {
        text-align: center; 
        padding: 4px;       
    }   
    QTreeWidget::item {
        background-color: #ffffff;
        color: #000000;
    }
    QTreeWidget::item:selected {
        background-color: #E2DFD2;
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
        background-color: #E2DFD2;
        color: #000000;
        padding:3px;
    }
    QMenuBar::item {
        background-color: #E2DFD2;
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

    config = {"light": "Switch to Light Theme", "dark": "Switch to Dark Theme"}

    def __init__(self, editor_instance):
        self.editor_instance = editor_instance

    @classmethod
    def apply_theme(cls, theme, parent):
        """Apply the selected theme to the application."""
        parent.current_theme = theme
        if theme == "dark":
            parent.setStyleSheet(ThemeManager.DARK_STYLESHEET)
        else:
            parent.setStyleSheet(ThemeManager.LIGHT_STYLESHEET)

        # Update the preferences menu to show the correct theme option
        for t, action in parent.theme_actions.items():
            action.setVisible(t != theme)
