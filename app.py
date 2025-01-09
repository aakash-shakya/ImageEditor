import sys
import logging
from PyQt5.QtWidgets import QApplication
from core.editor import ImageEditor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="image_editor.log",
)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = ImageEditor()
    editor.show()
    sys.exit(app.exec_())
