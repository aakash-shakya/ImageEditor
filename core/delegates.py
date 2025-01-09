from PyQt5.QtWidgets import QStyledItemDelegate, QStyle
from PyQt5.QtCore import QRect, QEvent
from PyQt5.QtGui import QIcon

class DeleteIconDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, image_editor=None):
        super().__init__(parent)
        self.image_editor = image_editor
        self.delete_icon = QIcon("delete_icon.png")  # Path to your delete icon

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if option.state & QStyle.StateFlag.State_MouseOver:
            # Draw the delete icon on hover
            icon_rect = QRect(option.rect.right() - 20, option.rect.top(), 16, 16)
            self.delete_icon.paint(painter, icon_rect)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonPress:
            # Check if the delete icon was clicked
            icon_rect = QRect(option.rect.right() - 20, option.rect.top(), 16, 16)
            if icon_rect.contains(event.pos()):
                # Emit a signal or call a method to delete the item
                self.image_editor.delete_item(index)
                return True
        return super().editorEvent(event, model, option, index)
