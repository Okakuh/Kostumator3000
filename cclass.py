from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QTextEdit
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QIcon
from PyQt6.QtCore import QSize
from os import path, listdir
from pathlib import Path

import settings
import settings as ss
import functions


class UnicodeConvertorSettings(QDialog):
    def __init__(self, title: str, message: str, symbols_unicode_convertor_will_skip: str):
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
        self.layout.addWidget(QLabel(message))

        self.symbols = QTextEdit(self)

        self.layout.addWidget(self.symbols)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.symbols.setPlainText(self.symbols_unicode_convertor_will_skip)


class MyLineEdit(QLineEdit):
    def __init__(self, parent, maket_text_edit: QLineEdit, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent_self = parent

        self.setAcceptDrops(True)
        self.setGeometry(maket_text_edit.geometry())
        self.setStyleSheet(maket_text_edit.styleSheet())
        self.setFont(maket_text_edit.font())

    def dragEnterEvent(self, event) -> None:
        dropped_path = event.mimeData().text()
        if "file:///" in dropped_path:
            if dropped_path.count("file:///") == 1:
                if path.isdir(dropped_path.removeprefix("file:///")):
                    event.accept()
                    return
        event.ignore()

    def dropEvent(self, event) -> None:
        event.accept()
        dropped_path = event.mimeData().text().removeprefix("file:///")

        self.setText(dropped_path)
        self.parent_self.save_path_changed()
        self.parent_self.p_save_folder = dropped_path


class AskSureDialog(QDialog):
    def __init__(self, title: str, message: str):
        super().__init__()

        self.title = title
        self.message = message

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


class IconButton(QPushButton):
    def __init__(self, parent, folder_in_preset: str, maket_button: QPushButton, default_icon: str,
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)  
        self.default_icon = default_icon
        self.user_icon = default_icon
        self.folder_in_preset = folder_in_preset

        self.icon_width = maket_button.iconSize().width()
        self.icon_height = maket_button.iconSize().height()

        self.setAcceptDrops(True)
        self.setGeometry(maket_button.geometry())
        self.setIconSize(QSize(self.icon_width, self.icon_height))
        self.setStyleSheet(maket_button.styleSheet())

        self.set_icon(QPixmap(self.user_icon))

        self.clicked.connect(self.clear)

        self.file_id = 0
        self.last_preset = None

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

        self.user_icon = first_file
        self.set_icon(QPixmap(first_file))

    def clear(self) -> None:
        self.user_icon = self.default_icon
        self.set_icon(QPixmap(self.user_icon))

    def set_icon(self, icon: QPixmap) -> None:
        self.setIcon(QIcon(icon.scaled(self.icon_width, self.icon_height)))

    def has_user_icon(self) -> bool:
        return self.default_icon != self.user_icon and self.user_icon != settings.p_icon_button_disabled

    def get_icon(self) -> str:
        return self.user_icon

    def slide_show(self, current_preset):
        if not self.isEnabled():
            return

        if not self.has_user_icon():
            return

        path_to_folder = f"{settings.p_fldr_presets}/{current_preset}/{settings.name_in_preset_ways_to_icons}/{self.folder_in_preset}"

        files_properties = listdir(path_to_folder)
        if not files_properties:
            return

        if self.last_preset != current_preset:
            self.last_preset = current_preset
            self.file_id = 0

        if self.file_id + 1 > len(files_properties):
            self.file_id = 0

        file_properties_name = Path(files_properties[self.file_id]).stem
        path_to_overlay_image = f"{settings.p_fldr_presets}/{current_preset}/{settings.name_in_preset_overlay_images}/{file_properties_name}.png"

        self.set_icon(functions.merge_images(self.user_icon, path_to_overlay_image))

        self.file_id += 1

    def disable(self) -> None:
        self.setDisabled(True)
        self.set_icon(QPixmap(settings.p_icon_button_disabled))

    def enable(self) -> None:
        self.setEnabled(True)
        self.set_icon(QPixmap(self.default_icon))

    def valid(self) -> bool:
        return self.has_user_icon() and self.isEnabled()


class ArmorButton(QPushButton):
    def __init__(self, parent, maket_button: QPushButton, default_icon: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.my_parent = parent

        self.default_icon = default_icon
        self.user_icon = default_icon

        self.icon_width = maket_button.iconSize().width()
        self.icon_height = maket_button.iconSize().height()

        self.setAcceptDrops(True)
        self.setGeometry(maket_button.geometry())
        self.setIconSize(QSize(self.icon_width, self.icon_height))
        self.setStyleSheet(maket_button.styleSheet())

        self.set_icon(QPixmap(self.user_icon))

        self.clicked.connect(self.clear)

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

        self.user_icon = first_file
        self.set_icon(QPixmap(first_file))

    def clear(self) -> None:
        self.user_icon = self.default_icon
        self.set_icon(QPixmap(self.user_icon))

    def set_icon(self, icon: QPixmap) -> None:
        self.setIcon(QIcon(icon.scaled(self.icon_width, self.icon_height)))

    def has_user_icon(self) -> bool:
        return self.default_icon != self.user_icon

    def get_icon(self) -> str:
        return self.user_icon

    def valid(self) -> bool:
        return self.has_user_icon() and self.isEnabled()


class ErrorID:
    def __init__(self):
        self.__error_id = 0

    def set_id(self, error_id: int) -> None:
        self.__error_id = error_id

    def get_id(self) -> int:
        return self.__error_id
