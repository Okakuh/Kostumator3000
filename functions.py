from os import path
from shutil import rmtree
from PIL import Image
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QPixmap, QPainter
from subprocess import Popen
from json import load, dump

from settings import button_enabled_style, button_disabled_style


def delete_folders(folders: list[str]) -> None:
    for folder in folders:
        rmtree(folder)


def disable_button(button: QPushButton) -> None:
    button.setDisabled(True)
    button.setStyleSheet(button_disabled_style)


def enable_button(button: QPushButton) -> None:
    button.setDisabled(False)
    button.setStyleSheet(button_enabled_style)


def make_unicode(text: str, symbols_not_to_convert: str) -> str:
    result = ""
    for char in text:
        if char not in symbols_not_to_convert:
            result += r'\u{:04X}'.format(ord(char))
        else:
            result += char
    return result


def read_json(path_to_json: str) -> dict:
    with open(file=path_to_json, mode="r", encoding="utf-8") as f:
        return load(f)


def write_json(path_to_json: str, data: dict) -> None:
    with open(file=path_to_json, mode="w", encoding="utf-8") as sett:
        dump(data, sett, indent=3, ensure_ascii=False)


def merge_images(base_image: str, overlay_image: str) -> QPixmap:
    base_image = QPixmap(base_image)

    painter = QPainter(base_image)
    painter.drawPixmap(0, 0, QPixmap(overlay_image))
    painter.end()

    return base_image


def normalize_path(string: str) -> str:
    while string[-1] == " ":
        string = string.removesuffix(" ")
    return path.normpath(string).replace("\\", "/")


def show_warning(button: QPushButton, message: str) -> None:
    button.show()
    button.setToolTip(message)
    button.setToolTipDuration(-1)


def hide_warning(button: QPushButton) -> None: button.close()


def open_in_explorer(path_to_open: str) -> None:
    Popen(f'explorer /open, {path.normpath(path_to_open)}')


def edit_file_properties(*, file: str, data_to_replase: dict[str, str]) -> None:
    with open(file=file) as file1:
        file1 = file1.read()
        for key, value in data_to_replase.items():
            file1 = file1.replace(key, value)

    with open(file=file, mode='w') as file2:
        file2.write(file1)
