"""
Command Palette Dialog - Quick access UI for all DAIW features

Provides a searchable command palette similar to VS Code's Cmd+K interface.
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QLabel, QWidget, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QKeyEvent, QPalette, QColor

from daiw.brain.command_palette import CommandPalette, Command


class CommandListItem(QWidget):
    """Custom widget for command list items"""

    def __init__(self, command: Command, parent=None):
        super().__init__(parent)

        self.command = command

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(command.icon)
        icon_label.setFont(QFont("", 16))
        icon_label.setFixedWidth(30)
        layout.addWidget(icon_label)

        # Text container
        text_container = QVBoxLayout()
        text_container.setSpacing(2)

        # Title
        title_label = QLabel(command.title)
        title_label.setFont(QFont("", 12, QFont.Weight.Bold))
        text_container.addWidget(title_label)

        # Description
        desc_label = QLabel(command.description)
        desc_label.setFont(QFont("", 9))
        desc_label.setStyleSheet("color: #888;")
        text_container.addWidget(desc_label)

        layout.addLayout(text_container, 1)

        # Shortcut (if available)
        if command.shortcut:
            shortcut_label = QLabel(command.shortcut)
            shortcut_label.setFont(QFont("", 9))
            shortcut_label.setStyleSheet(
                "background-color: #444; color: #fff; "
                "padding: 2px 6px; border-radius: 3px;"
            )
            layout.addWidget(shortcut_label)


class CommandPaletteDialog(QDialog):
    """
    Command Palette Dialog

    Features:
    - Fuzzy search
    - Keyboard navigation
    - Recent commands
    - Category filtering
    - Keyboard shortcuts display
    """

    # Signals
    command_executed = pyqtSignal(str)  # command_id

    def __init__(self, command_palette: CommandPalette, parent=None):
        super().__init__(parent)

        self.command_palette = command_palette
        self.current_results: List[Command] = []

        # Window setup
        self.setWindowTitle("Command Palette")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Size
        self.setMinimumWidth(600)
        self.setMaximumWidth(800)
        self.setMinimumHeight(400)
        self.setMaximumHeight(600)

        # Setup UI
        self._setup_ui()

        # Center on screen
        self._center_on_screen()

        # Debounce timer for search
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)

    def _setup_ui(self) -> None:
        """Setup the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Container frame
        container = QFrame()
        container.setObjectName("container")
        container.setStyleSheet("""
            QFrame#container {
                background-color: #2b2b2b;
                border-radius: 10px;
                border: 1px solid #444;
            }
        """)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a command or search...")
        self.search_input.setFont(QFont("", 14))
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                color: #fff;
                border: none;
                border-bottom: 1px solid #555;
                padding: 12px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.returnPressed.connect(self._on_execute_selected)
        container_layout.addWidget(self.search_input)

        # Results list
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #fff;
                border: none;
                outline: none;
                padding: 8px;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QListWidget::item {
                border-radius: 5px;
                padding: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #0d7eea;
            }
            QListWidget::item:hover {
                background-color: #3c3c3c;
            }
        """)
        self.results_list.itemActivated.connect(self._on_item_activated)
        container_layout.addWidget(self.results_list)

        # Help text
        help_text = QLabel("↑↓ Navigate • Enter Execute • Esc Close")
        help_text.setFont(QFont("", 9))
        help_text.setStyleSheet("""
            QLabel {
                color: #888;
                padding: 8px 12px;
                background-color: #2b2b2b;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        help_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(help_text)

        main_layout.addWidget(container)

        # Initial search (show recent)
        self._perform_search()

    def _center_on_screen(self) -> None:
        """Center dialog on screen"""
        if self.parent():
            parent_geo = self.parent().geometry()
            self.move(
                parent_geo.center().x() - self.width() // 2,
                parent_geo.center().y() - self.height() // 2
            )

    def _on_search_text_changed(self, text: str) -> None:
        """Handle search text change"""
        # Debounce search
        self.search_timer.stop()
        self.search_timer.start(150)  # 150ms delay

    def _perform_search(self) -> None:
        """Perform the actual search"""
        query = self.search_input.text()
        results = self.command_palette.search(query, max_results=15)

        self.current_results = results
        self._update_results_list(results)

    def _update_results_list(self, commands: List[Command]) -> None:
        """Update the results list with commands"""
        self.results_list.clear()

        for command in commands:
            # Create list item
            item = QListWidgetItem(self.results_list)

            # Create custom widget
            widget = CommandListItem(command)
            item.setSizeHint(widget.sizeHint())

            # Add to list
            self.results_list.addItem(item)
            self.results_list.setItemWidget(item, widget)

        # Select first item
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

    def _on_item_activated(self, item: QListWidgetItem) -> None:
        """Handle item activation (double-click)"""
        self._execute_selected_command()

    def _on_execute_selected(self) -> None:
        """Handle Enter key press"""
        self._execute_selected_command()

    def _execute_selected_command(self) -> None:
        """Execute the currently selected command"""
        current_row = self.results_list.currentRow()
        if 0 <= current_row < len(self.current_results):
            command = self.current_results[current_row]

            # Execute command
            success = self.command_palette.execute_command(command.id)

            if success:
                # Emit signal
                self.command_executed.emit(command.id)

                # Close dialog
                self.accept()
            else:
                # Show error (optional)
                print(f"Failed to execute command: {command.id}")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard events"""
        key = event.key()

        if key == Qt.Key.Key_Escape:
            # Close dialog
            self.reject()

        elif key == Qt.Key.Key_Down:
            # Move selection down
            current = self.results_list.currentRow()
            if current < self.results_list.count() - 1:
                self.results_list.setCurrentRow(current + 1)

        elif key == Qt.Key.Key_Up:
            # Move selection up
            current = self.results_list.currentRow()
            if current > 0:
                self.results_list.setCurrentRow(current - 1)

        elif key == Qt.Key.Key_PageDown:
            # Page down
            current = self.results_list.currentRow()
            new_pos = min(current + 5, self.results_list.count() - 1)
            self.results_list.setCurrentRow(new_pos)

        elif key == Qt.Key.Key_PageUp:
            # Page up
            current = self.results_list.currentRow()
            new_pos = max(current - 5, 0)
            self.results_list.setCurrentRow(new_pos)

        elif key == Qt.Key.Key_Home:
            # Go to top
            self.results_list.setCurrentRow(0)

        elif key == Qt.Key.Key_End:
            # Go to bottom
            self.results_list.setCurrentRow(self.results_list.count() - 1)

        else:
            # Let default handling occur
            super().keyPressEvent(event)

    def showEvent(self, event) -> None:
        """Handle show event"""
        super().showEvent(event)

        # Focus search input
        self.search_input.setFocus()
        self.search_input.selectAll()

        # Refresh results
        self._perform_search()

    def set_search_text(self, text: str) -> None:
        """
        Set initial search text

        Args:
            text: Initial search query
        """
        self.search_input.setText(text)
        self._perform_search()

    def clear_search(self) -> None:
        """Clear search input"""
        self.search_input.clear()
        self._perform_search()
