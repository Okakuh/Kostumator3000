from os import path
from shutil import rmtree
from PIL import Image
from subprocess import Popen
from json import load, dump

from cclass import *
from vars import button_enabled_style, button_disabled_style


def edit_unicode_convertor_settings(symbols_unicode_convertor_will_skip: str,
                                    window_title: str,
                                    window_message: str) -> tuple[bool, str]:
    unicode_settings = UnicodeConvertorSettings(window_title, window_message, symbols_unicode_convertor_will_skip)

    if unicode_settings.exec():
        symbols = unicode_settings.symbols.toPlainText()
        return True, symbols
    return False, ""


def create_texture_buttons(parent) -> None:
    parent.button_helmet = TextureButton(parent, 'helmet', parent.maket_helmet,
                                         f'{parent.main_path}/program/empty_buttons/helmet.png')

    parent.button_chestlate = TextureButton(parent, 'chestplate', parent.maket_chestplate,
                                            f'{parent.main_path}/program/empty_buttons/chestplate.png')

    parent.button_leggings = TextureButton(parent, 'leggings', parent.maket_leggings,
                                           f'{parent.main_path}/program/empty_buttons/leggings.png')

    parent.button_boots = TextureButton(parent, 'boots', parent.maket_boots,
                                        f'{parent.main_path}/program/empty_buttons/boots.png')

    parent.button_layer_1 = TextureButton(parent, 'layer_1', parent.maket_layer_1,
                                          f'{parent.main_path}/program/empty_buttons/layer_1.png')

    parent.button_layer_2 = TextureButton(parent, 'layer_2', parent.maket_layer_2,
                                          f'{parent.main_path}/program/empty_buttons/layer_2.png')


def delete_folders(folders: list[str]) -> None:
    for folder in folders:
        if path.exists(folder):
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
    if path.exists(path_to_json):
        with open(file=path_to_json, mode="r", encoding="utf-8") as f:
            text = load(f)
            return text


def edit_json(path_to_json: str, data: dict) -> None:
    if path.exists(path_to_json):
        with open(file=path_to_json, mode="w", encoding="utf-8") as sett:
            dump(data, sett, indent=3)


def create_icon(costume_icon: str, overlay_image: str, path_to_save_icon: str) -> None:

    # Функция для наложения "орб ресурса" на иконки костюма

    costume_icon = Image.open(costume_icon).convert("RGBA")
    overlay_image = Image.open(overlay_image).resize(costume_icon.size, Image.NEAREST).convert("RGBA")

    pixels_overlay_image = overlay_image.load()
    pixels_costume_icon = costume_icon.load()

    x, y = overlay_image.size

    for i in range(x):
        for j in range(y):
            if pixels_overlay_image[i, j] != (0, 0, 0, 0):
                pixels_costume_icon[i, j] = pixels_overlay_image[i, j]

    costume_icon.save(path_to_save_icon, quality=100)

    costume_icon.close()
    overlay_image.close()


def normalize_slash(string: str) -> str:
    while string[-1] == " ":
        string = string.removesuffix(" ")
    return path.normpath(string).replace("\\", "/")


def show_warning(warn_button: QPushButton, message: str) -> None:
    warn_button.show()
    warn_button.setToolTip(message)
    warn_button.setToolTipDuration(-1)


def hide_warning(warn_button: QPushButton) -> None: warn_button.close()


def open_in_explorer(path_to_open: str) -> None:
    path_to_open = path.normpath(path_to_open)

    if path.exists(path_to_open):
        Popen(f'explorer /open, {path_to_open}')
