"""
CollabNet Dialogs - GUI für kollaborative Sessions

Ermöglicht das Erstellen, Beitreten und Verwalten von
CollabNet-Collaboration-Sessions
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QSpinBox,
    QTextEdit,
    QGroupBox,
    QTabWidget,
    QWidget,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor


class CollabNetSessionDialog(QDialog):
    """Main dialog for CollabNet session management"""

    create_session_requested = pyqtSignal(str, str, int)  # name, password, max_users
    join_session_requested = pyqtSignal(str, str)  # session_id, password
    disconnect_requested = pyqtSignal()
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("🧠 CollabNet Mode - Collaborative Sessions")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("🧠 CollabNet Collaboration")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Work together in real-time across the network")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Connection status
        self.status_label = QLabel("Status: Not connected")
        self.status_label.setStyleSheet("padding: 10px; background-color: #333; border-radius: 5px;")
        layout.addWidget(self.status_label)

        # Tabs
        tabs = QTabWidget()

        # Tab 1: Create Session
        create_tab = self._create_create_tab()
        tabs.addTab(create_tab, "Create Session")

        # Tab 2: Join Session
        join_tab = self._create_join_tab()
        tabs.addTab(join_tab, "Join Session")

        # Tab 3: Current Session
        session_tab = self._create_session_tab()
        tabs.addTab(session_tab, "Current Session")

        layout.addWidget(tabs)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def _create_create_tab(self) -> QWidget:
        """Create the 'Create Session' tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Session name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Session Name:"))
        self.session_name_input = QLineEdit()
        self.session_name_input.setPlaceholderText("e.g., Beat Making Session")
        name_layout.addWidget(self.session_name_input)
        layout.addLayout(name_layout)

        # Password (optional)
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password (optional):"))
        self.session_password_input = QLineEdit()
        self.session_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.session_password_input.setPlaceholderText("Leave empty for public session")
        password_layout.addWidget(self.session_password_input)
        layout.addLayout(password_layout)

        # Max users
        users_layout = QHBoxLayout()
        users_layout.addWidget(QLabel("Max Users:"))
        self.max_users_spin = QSpinBox()
        self.max_users_spin.setRange(2, 16)
        self.max_users_spin.setValue(8)
        users_layout.addWidget(self.max_users_spin)
        users_layout.addStretch()
        layout.addLayout(users_layout)

        # Info
        info = QLabel("You will be the host of this session. Other users can join and collaborate in real-time.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #888; padding: 10px;")
        layout.addWidget(info)

        # Create button
        create_btn = QPushButton("🚀 Create Session")
        create_btn.setMinimumHeight(50)
        create_btn.clicked.connect(self._on_create_session)
        layout.addWidget(create_btn)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def _create_join_tab(self) -> QWidget:
        """Create the 'Join Session' tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Sessions")
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(refresh_btn)

        # Sessions list
        self.sessions_list = QListWidget()
        self.sessions_list.itemDoubleClicked.connect(self._on_session_double_click)
        layout.addWidget(self.sessions_list)

        # Join controls
        join_group = QGroupBox("Join Selected Session")
        join_layout = QVBoxLayout()

        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.join_password_input = QLineEdit()
        self.join_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.join_password_input.setPlaceholderText("Enter password if required")
        password_layout.addWidget(self.join_password_input)
        join_layout.addLayout(password_layout)

        join_btn = QPushButton("➡️ Join Session")
        join_btn.clicked.connect(self._on_join_session)
        join_layout.addWidget(join_btn)

        join_group.setLayout(join_layout)
        layout.addWidget(join_group)

        tab.setLayout(layout)
        return tab

    def _create_session_tab(self) -> QWidget:
        """Create the 'Current Session' tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Session info
        self.current_session_label = QLabel("Not in a session")
        self.current_session_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.current_session_label)

        # Users list
        users_group = QGroupBox("Connected Users")
        users_layout = QVBoxLayout()

        self.users_list = QListWidget()
        users_layout.addWidget(self.users_list)

        users_group.setLayout(users_layout)
        layout.addWidget(users_group)

        # Chat (future feature)
        chat_group = QGroupBox("Session Chat")
        chat_layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMaximumHeight(150)
        chat_layout.addWidget(self.chat_display)

        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a message...")
        self.chat_input.returnPressed.connect(self._on_send_chat)
        chat_input_layout.addWidget(self.chat_input)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._on_send_chat)
        chat_input_layout.addWidget(send_btn)

        chat_layout.addLayout(chat_input_layout)
        chat_group.setLayout(chat_layout)
        layout.addWidget(chat_group)

        # Disconnect button
        disconnect_btn = QPushButton("🚪 Leave Session")
        disconnect_btn.clicked.connect(self.disconnect_requested.emit)
        layout.addWidget(disconnect_btn)

        tab.setLayout(layout)
        return tab

    def _on_create_session(self):
        """Handle create session button"""
        name = self.session_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Name Required", "Please enter a session name")
            return

        password = self.session_password_input.text()
        max_users = self.max_users_spin.value()

        self.create_session_requested.emit(name, password, max_users)

    def _on_join_session(self):
        """Handle join session button"""
        selected = self.sessions_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Selection Required", "Please select a session to join")
            return

        session_id = selected.data(Qt.ItemDataRole.UserRole)
        password = self.join_password_input.text()

        self.join_session_requested.emit(session_id, password)

    def _on_session_double_click(self, item: QListWidgetItem):
        """Handle double-click on session"""
        self._on_join_session()

    def _on_send_chat(self):
        """Handle send chat message"""
        message = self.chat_input.text().strip()
        if message:
            # TODO: Send chat message via signal
            self.chat_input.clear()

    # ========== Update Methods ==========

    def set_status(self, connected: bool, in_session: bool = False):
        """Update connection status"""
        if connected:
            if in_session:
                self.status_label.setText("Status: ✅ Connected & In Session")
                self.status_label.setStyleSheet("padding: 10px; background-color: #2d5; border-radius: 5px;")
            else:
                self.status_label.setText("Status: ✅ Connected")
                self.status_label.setStyleSheet("padding: 10px; background-color: #25d; border-radius: 5px;")
        else:
            self.status_label.setText("Status: ❌ Not Connected")
            self.status_label.setStyleSheet("padding: 10px; background-color: #d25; border-radius: 5px;")

    def set_sessions_list(self, sessions: List[dict]):
        """Update available sessions list"""
        self.sessions_list.clear()

        for session in sessions:
            text = f"{session['session_name']} - {session['user_count']}/{session['max_users']} users"
            if session['has_password']:
                text += " 🔒"
            text += f" (Host: {session['host']})"

            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, session['session_id'])

            # Color based on availability
            if session['user_count'] >= session['max_users']:
                item.setForeground(QColor("#888"))
            else:
                item.setForeground(QColor("#0f0"))

            self.sessions_list.addItem(item)

    def set_current_session(self, session_name: str, is_host: bool):
        """Update current session info"""
        host_text = " (Host)" if is_host else ""
        self.current_session_label.setText(f"Session: {session_name}{host_text}")

    def add_user(self, username: str, color: str, is_host: bool = False):
        """Add user to users list"""
        host_text = " 👑" if is_host else ""
        item = QListWidgetItem(f"● {username}{host_text}")
        item.setForeground(QColor(color))
        self.users_list.addItem(item)

    def remove_user(self, username: str):
        """Remove user from users list"""
        for i in range(self.users_list.count()):
            item = self.users_list.item(i)
            if username in item.text():
                self.users_list.takeItem(i)
                break

    def clear_users(self):
        """Clear users list"""
        self.users_list.clear()

    def add_chat_message(self, username: str, message: str):
        """Add message to chat"""
        self.chat_display.append(f"<b>{username}:</b> {message}")


class CollabNetConnectDialog(QDialog):
    """Dialog for connecting to CollabNet server"""

    connect_requested = pyqtSignal(str, str, str)  # server_url, username, color

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Connect to CollabNet")
        self.setMinimumWidth(400)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("🧠 Connect to CollabNet Server")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Server URL
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel("Server:"))
        self.server_input = QLineEdit()
        self.server_input.setText("ws://localhost:8765")
        self.server_input.setPlaceholderText("ws://server:port")
        server_layout.addWidget(self.server_input)
        layout.addLayout(server_layout)

        # Username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Your producer name")
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # Color picker
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Avatar Color:"))
        self.color_input = QLineEdit()
        self.color_input.setText("#00ff00")
        self.color_input.setMaximumWidth(100)
        color_layout.addWidget(self.color_input)
        color_layout.addStretch()
        layout.addLayout(color_layout)

        # Connect button
        connect_btn = QPushButton("🔗 Connect")
        connect_btn.setMinimumHeight(40)
        connect_btn.clicked.connect(self._on_connect)
        layout.addWidget(connect_btn)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        self.setLayout(layout)

    def _on_connect(self):
        """Handle connect button"""
        server = self.server_input.text().strip()
        username = self.username_input.text().strip()
        color = self.color_input.text().strip()

        if not server:
            QMessageBox.warning(self, "Server Required", "Please enter a server URL")
            return

        if not username:
            QMessageBox.warning(self, "Username Required", "Please enter a username")
            return

        self.connect_requested.emit(server, username, color)
        self.accept()
