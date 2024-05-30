from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QTextEdit
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize
from os import path


class UnicodeConvertorSettings(QDialog):
    def __init__(self, title: str, message: str, symbols_unicode_convertor_will_skip: str) -> None:
        self.title = title
        self.message = message
        self.symbols_unicode_convertor_will_skip = symbols_unicode_convertor_will_skip
        super().__init__()

        self.setWindowTitle(self.title)

        qbtn = QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(qbtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(self.message)
        self.layout.addWidget(message)

        self.symbols = QTextEdit(self)

        self.layout.addWidget(self.symbols)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.symbols.setPlainText(self.symbols_unicode_convertor_will_skip)


class MyLineEdit(QLineEdit):
    def __init__(self, parent, maket_text_edit: QLineEdit, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent_self = parent

        self.setAcceptDrops(True)
        self.setGeometry(maket_text_edit.geometry())
        self.setStyleSheet(maket_text_edit.styleSheet())
        self.setFont(maket_text_edit.font())

    def dragEnterEvent(self, event) -> None:
        if MyLineEdit.check(event.mimeData().text()):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        event.accept()
        file = event.mimeData().text().removeprefix("file:///")

        self.setText(file)
        self.parent_self.save_path_changed()
        self.parent_self.save_folder_path = file

    @staticmethod
    def check(pahtes: str) -> bool:
        if "file:///" in pahtes:
            if pahtes.count("file:///") == 1:
                path_to_drop = pahtes.removeprefix("file:///")
                if path.isdir(path_to_drop):
                    return True
        return False


class CustomDialog(QDialog):
    def __init__(self, title: str, message: str) -> None:
        self.title = title
        self.message = message
        super().__init__()

        self.setWindowTitle(self.title)

        qbtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(qbtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(self.message)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class TextureButton(QPushButton):
    def __init__(self, parent, name: str, maket_button: QPushButton, default_icon: str, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.my_parent = parent
        self.name = name
        self.default_icon = default_icon

        self.icon = self.default_icon[:]
        self.icon_width = maket_button.iconSize().width()
        self.icon_height = maket_button.iconSize().height()

        self.setAcceptDrops(True)
        self.setGeometry(maket_button.geometry())
        self.setIconSize(QSize(self.icon_width, self.icon_height))
        self.setIcon(QIcon(QPixmap(self.default_icon).scaled(self.icon_width, self.icon_height)))
        self.setStyleSheet(maket_button.styleSheet())

        self.clicked.connect(self.clear_and_set_default)

    def dragEnterEvent(self, event) -> None:

        if "file:///" in event.mimeData().text():
            if event.mimeData().text().replace('file:', '').split('///')[1].strip().split('.')[-1].lower() == 'png':
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        first_file = event.mimeData().text().replace('file:', '').split('///')[1].strip()

        self.setIcon(QIcon(QPixmap(first_file).scaled(self.icon_width, self.icon_height)))
        self.icon = first_file

        if self.name in self.my_parent.icons_buttons and self not in self.my_parent.icons_list:
            self.my_parent.icons_list.append(self)

        if self.name in self.my_parent.armor_buttons and self not in self.my_parent.armor_texture_list:
            self.my_parent.armor_texture_list.append(self)

    def clear_and_set_default(self) -> None:
        self.setIcon(QIcon(QPixmap(self.default_icon).scaled(self.icon_width, self.icon_height)))
        self.icon = self.default_icon[:]

        if self.name in self.my_parent.icons_buttons:
            if self in self.my_parent.icons_list:
                self.my_parent.icons_list.remove(self)

        if self.name in self.my_parent.armor_buttons:
            if self in self.my_parent.armor_texture_list:
                self.my_parent.armor_texture_list.remove(self)
