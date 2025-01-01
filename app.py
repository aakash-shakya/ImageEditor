import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt
import json


class MindMapApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mind Mapper")
        self.showMaximized()

        self.init_ui()
        self.db_connection = sqlite3.connect('mind_map.db')
        self.create_db()

    def init_ui(self):
        """Set up the UI components."""
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Tree Widget (for Mind Map structure)
        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(["Mind Map"])
        self.layout.addWidget(self.tree)

        # Horizontal Layout for Node Manipulation Buttons
        self.node_buttons_layout = QHBoxLayout()
        self.add_button = QPushButton('Add Node', self)
        self.edit_button = QPushButton('Edit Node', self)
        self.delete_button = QPushButton('Delete Node', self)

        # Add node-related buttons to the top layout
        self.node_buttons_layout.addWidget(self.add_button)
        self.node_buttons_layout.addWidget(self.edit_button)
        self.node_buttons_layout.addWidget(self.delete_button)

        # Add the node button layout to the main layout
        self.layout.addLayout(self.node_buttons_layout)

        # Horizontal Layout for DB Manipulation Buttons
        self.db_buttons_layout = QHBoxLayout()
        self.save_button = QPushButton('Save to Database', self)
        self.load_button = QPushButton('Load from Database', self)

        # Add DB-related buttons to the second layout
        self.db_buttons_layout.addWidget(self.save_button)
        self.db_buttons_layout.addWidget(self.load_button)

        # Add the DB button layout to the main layout
        self.layout.addLayout(self.db_buttons_layout)

        # Button connections
        self.add_button.clicked.connect(self.add_node)
        self.edit_button.clicked.connect(self.edit_node)
        self.delete_button.clicked.connect(self.delete_node)
        self.save_button.clicked.connect(self.save_to_db)
        self.load_button.clicked.connect(self.load_from_db)

    def create_db(self):
        """Create the SQLite database to store mind maps."""
        cursor = self.db_connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER,
                content TEXT
            )
        """)
        self.db_connection.commit()

    def add_node(self):
        """Add a new node to the mind map."""
        item_text, ok = QInputDialog.getText(self, "Add Node", "Enter node content:")
        if ok and item_text:
            current_item = self.tree.selectedItems()
            parent_item = current_item[0] if current_item else None
            parent_id = None if parent_item is None else parent_item.data(0, Qt.UserRole)

            node_item = QTreeWidgetItem([item_text])
            self.tree.addTopLevelItem(node_item) if parent_item is None else parent_item.addChild(node_item)

            # Save to the SQLite database
            cursor = self.db_connection.cursor()
            cursor.execute("INSERT INTO nodes (parent_id, content) VALUES (?, ?)", (parent_id, item_text))
            self.db_connection.commit()

    def edit_node(self):
        """Edit the selected node's content."""
        selected_items = self.tree.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            new_text, ok = QInputDialog.getText(self, "Edit Node", "Enter new content for the node:")
            if ok and new_text:
                current_item.setText(0, new_text)
                # Update the content in the database
                cursor = self.db_connection.cursor()
                cursor.execute("UPDATE nodes SET content = ? WHERE content = ?", (new_text, current_item.text(0)))
                self.db_connection.commit()

    def delete_node(self):
        """Delete the selected node."""
        selected_items = self.tree.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM nodes WHERE content = ?", (current_item.text(0),))
            self.db_connection.commit()
            current_item.parent().removeChild(current_item) if current_item.parent() else self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(current_item))

    def save_to_db(self):
        """Save the current mind map to the database."""
        cursor = self.db_connection.cursor()
        cursor.execute("DELETE FROM nodes")  # Clear existing nodes before saving
        self.db_connection.commit()

        self.save_node_recursively(self.tree.invisibleRootItem(), None)

    def save_node_recursively(self, tree_item, parent_id):
        """Recursively save nodes to the database."""
        cursor = self.db_connection.cursor()
        cursor.execute("INSERT INTO nodes (parent_id, content) VALUES (?, ?)", (parent_id, tree_item.text(0)))
        self.db_connection.commit()
        node_id = cursor.lastrowid

        for i in range(tree_item.childCount()):
            self.save_node_recursively(tree_item.child(i), node_id)

    def load_from_db(self):
        """Load mind map from the database."""
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT id, parent_id, content FROM nodes")
        rows = cursor.fetchall()

        # Build tree structure
        self.tree.clear()
        nodes = {}
        for row in rows:
            node_id, parent_id, content = row
            node_item = QTreeWidgetItem([content])
            nodes[node_id] = node_item

            if parent_id is None:
                self.tree.addTopLevelItem(node_item)
            else:
                parent_item = nodes.get(parent_id)
                if parent_item:
                    parent_item.addChild(node_item)

        self.db_connection.commit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MindMapApp()
    window.show()
    sys.exit(app.exec_())
