from time import strftime, time_ns, sleep
from os import listdir, path, getcwd, mkdir, renames, walk
from shutil import copy, copytree
from PyQt6 import uic, QtCore, QtGui
import threading
from pyperclip import copy as copy_to_clipboard
import pyperclip
import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QWidget

from functions import *
from cclass import *


class Costumer(QWidget):
    icons_buttons = ['helmet', 'chestplate', 'leggings', 'boots']
    armor_buttons = ['layer_1', 'layer_2']

    main_path = getcwd()

    settings_json = f"{main_path}\\program\\settings.json"
    path_to_presets = f"{main_path}\\program\\presets"
    logs_folder = f"{main_path}\\program\\logs"
    make_unicode_will_skip = ""

    kill_threads = False
    last_preset_folder_state = None

    icons_list = []
    armor_texture_list = []

    save_folder_path = ''

    def __init__(self):
        super().__init__()

        self.save_folder_is_ok = True
        self.chosed_preset_is_ok = True
        self.display_name_is_ok = True
        self.folder_name_is_ok = True

        #  Settings
        if True:
            self.ui = uic.loadUi(f"{Costumer.main_path}\\program\\costumator.ui", self)

            self.save_folder = MyLineEdit(self, maket_text_edit=self.maket_save_folder)

            self.widgets_id = {"Display name": self.display_name,
                               "Folder name": self.folder_name,
                               "Save costume to": self.save_folder,
                               "Path to icon folder": self.path_to_icon_folder,
                               "Path to leather armor changeble layer": self.leather_armor_layer,
                               "Path to leather armor icon changeble layer": self.leather_icon_layer}

            self.setMinimumSize(self.ui.geometry().width(), self.ui.geometry().height())
            self.setMaximumSize(self.ui.geometry().width(), self.ui.geometry().height())

        #   Create texture buttons
        if True:
            self.button_helmet = TextureButton(self,
                                               'helmet',
                                               self.maket_helmet,
                                               f'{Costumer.main_path}/program/empty_buttons/helmet.png')

            self.button_chestlate = TextureButton(self,
                                                  'chestplate',
                                                  self.maket_chestplate,
                                                  f'{Costumer.main_path}/program/empty_buttons/chestplate.png')

            self.button_leggings = TextureButton(self,
                                                 'leggings',
                                                 self.maket_leggings,
                                                 f'{Costumer.main_path}/program/empty_buttons/leggings.png')

            self.button_boots = TextureButton(self,
                                              'boots',
                                              self.maket_boots,
                                              f'{Costumer.main_path}/program/empty_buttons/boots.png')

            self.button_layer_1 = TextureButton(self, 'layer_1',
                                                self.maket_layer_1,
                                                f'{Costumer.main_path}/program/empty_buttons/layer_1.png')

            self.button_layer_2 = TextureButton(self, 'layer_2',
                                                self.maket_layer_2,
                                                f'{Costumer.main_path}/program/empty_buttons/layer_2.png')

        #   Functional buttons.clicked.connect
        if True:
            # Main battons create, create 3d, clear
            self.button_create.clicked.connect(self.click_create)
            self.button_3d.clicked.connect(self.click_3d)
            self.button_clear.clicked.connect(self.all_clear)

            # Display name buttons
            self.button_copy_unicode_display_name\
                .clicked.connect(lambda: copy_to_clipboard(make_unicode(self.display_name.text(),
                                                                        Costumer.make_unicode_will_skip)))
            self.open_unicode_convertor_settings.clicked.connect(self.click_uni_settings)

            # Save folder buttons
            self.button_open_in_explorer_save_folder\
                .clicked.connect(lambda: open_in_explorer(Costumer.save_folder_path))
            self.button_delete_created_folders.clicked.connect(self.delete_existing_folders)

            # Preset buttons
            self.refresh_presets.clicked.connect(self.set_preset_settings)
            self.set_current_settings_to_preset.clicked.connect(self.set_current_settings_to_preset_func)
            self.button_open_in_explorer_preset \
                .clicked.connect(lambda: open_in_explorer(Costumer.path_to_presets))

        #   Enter field.textEdited.connect
        if True:
            self.save_folder.textEdited.connect(self.save_path_changed)
            self.display_name.textEdited.connect(self.display_name_changed)
            self.folder_name.textEdited.connect(self.folder_name_changed)

            self.chosed_preset.currentTextChanged.connect(self.set_preset_settings)

        #   On start code
        if True:
            settings = read_json(Costumer.settings_json)
            self.chosed_preset.addItem(settings["last_preset"])
            self.chosed_preset.setCurrentText(settings["last_preset"])

            self.created_folder_check_thread = threading.Thread(target=self.watch_created_costume_folder_thread)
            self.created_folder_check_thread.start()

            self.preset_folder_check_thread = threading.Thread(target=self.watch_preset_folder_thread)
            self.preset_folder_check_thread.start()

            self.display_name_changed()

    def set_current_settings_to_preset_func(self):
        settings_json = f"{Costumer.path_to_presets}\\{self.chosed_preset.currentText()}\\settings.json"

        dlg = CustomDialog("Sure?", "Set current settings as preset default?")
        if dlg.exec():
            settings = read_json(settings_json)

            for widget_name_in_settings in self.widgets_id.keys():
                settings["input_fields_text"][widget_name_in_settings] = self.widgets_id[widget_name_in_settings].text()

            edit_json(settings_json, settings)

    def delete_existing_folders(self) -> None:
        ask = CustomDialog("Sure?", "Delete folders with this name?")
        if ask.exec():
            delete_folders([f"{Costumer.save_folder_path}\\{self.folder_name.text()}",
                            f"{Costumer.save_folder_path}\\{self.folder_name.text()}_"])

            self.folder_name_changed()

    def update_presets(self):
        if not Costumer.last_preset_folder_state == listdir(Costumer.path_to_presets):
            Costumer.last_preset_folder_state = listdir(Costumer.path_to_presets)

            currend_preset = self.chosed_preset.currentText()

            preset_list = []
            for path1 in listdir(Costumer.path_to_presets):
                if path.isdir(f"{Costumer.path_to_presets}/{path1}"):
                    preset_list.append(path1)

            self.chosed_preset.clear()

            for preset_folder in preset_list:
                self.chosed_preset.addItem(preset_folder)

            if currend_preset != "" and currend_preset in preset_list:
                self.chosed_preset.setCurrentText(currend_preset)
            else:
                if len(preset_list) != 0:
                    self.chosed_preset.setCurrentText(preset_list[0])

            if self.chosed_preset.currentText() != "":
                hide_warning(self.warn_preset)
                self.chosed_preset_is_ok = True

                self.set_preset_settings()

                enable_button(self.set_current_settings_to_preset)
                enable_button(self.refresh_presets)
            else:
                self.chosed_preset_is_ok = False

                show_warning(self.warn_preset, "No presets found!")

                disable_button(self.set_current_settings_to_preset)
                disable_button(self.refresh_presets)

                self.display_name_changed()
                self.save_path_changed()
        self.setFocus()

    def set_preset_settings(self):
        preset_folder = self.chosed_preset.currentText()
        path_to_preset_settings_json = f"{Costumer.path_to_presets}\\{preset_folder}\\settings.json"

        if preset_folder == "" or not path.exists(path_to_preset_settings_json):
            return

        preset_settings = read_json(path_to_preset_settings_json)

        for widget in preset_settings["input_fields_text"].keys():
            self.widgets_id[widget].setText(preset_settings["input_fields_text"][widget])

        Costumer.make_unicode_will_skip = preset_settings["symbols_unicode_convertor_will_skip"]

        self.display_name_changed()
        self.save_path_changed()

    def display_name_changed(self):
        text = self.display_name.text()

        if text != '':
            if '\\' in text or '№' in text or '?' in text or '§' in text:
                show_warning(self.warn_display_name, "This symbols will not work properly "
                                                     "if used in the item name: \\ № ? §")
                self.display_name_is_ok = False
                disable_button(self.button_copy_unicode_display_name)
            elif len(text) > 50:
                show_warning(self.warn_display_name, "Too long display name! Maximum 50 characters!\n"
                                                     "Player will not be able to rename item in anvil!")
                self.display_name_is_ok = False
            else:
                hide_warning(self.warn_display_name)
                self.display_name_is_ok = True
                enable_button(self.button_copy_unicode_display_name)
        else:
            hide_warning(self.warn_display_name)
            self.display_name_is_ok = True

        self.update_create_and_3d()

    def folder_name_changed(self):
        text = self.folder_name.text()

        skip = False
        error = 0
        if text.replace(" ", "") == '':
            show_warning(self.warn_folder, "Required field!")
            disable_button(self.button_delete_created_folders)

            error = 1
        else:
            if not skip:
                for letter in text:
                    if letter not in "abcdefghijklmnopqrstuvwxyz1234567890_":
                        error = 1
                        skip = True
                        show_warning(self.warn_folder, """This field can only contain underscores,
                                                                \nsmall letters of the English alphabet and numbers!
                                                                \nMinecraft will not work with other symbols!""")
                        break

            if not skip:
                temp_message = "Delete or move existing folders: "
                temp_error = 0

                if path.exists(f"{Costumer.save_folder_path}\\{text}_"):
                    temp_message += f"'{text}_'"
                    error = 1
                    temp_error = 1

                if path.exists(f"{Costumer.save_folder_path}\\{text}"):
                    temp_message += f"'{text}'"
                    error = 1
                    temp_error = 1

                if temp_error == 1:
                    show_warning(self.warn_folder, temp_message)
                    enable_button(self.button_delete_created_folders)
                else:
                    disable_button(self.button_delete_created_folders)

        if error == 1:
            self.folder_name_is_ok = False
        else:
            hide_warning(self.warn_folder)
            self.folder_name_is_ok = True

        self.update_create_and_3d()

    def update_create_and_3d(self):
        if not self.chosed_preset_is_ok or not self.display_name_is_ok \
                or not self.folder_name_is_ok or not self.save_folder_is_ok:

            disable_button(self.button_create)
            disable_button(self.button_3d)
        else:
            enable_button(self.button_create)
            enable_button(self.button_3d)

    def save_path_changed(self):
        text = self.save_folder.text()

        if text != '':
            while text[-1] == '\\' or text[-1] == '/':
                text = text[:-1]

        if path.exists(text):
            hide_warning(self.warn_save_path)
            self.save_folder_is_ok = True
            Costumer.save_folder_path = normalize_slash(text)
            enable_button(self.button_open_in_explorer_save_folder)

            self.folder_name_changed()
        else:
            disable_button(self.button_open_in_explorer_save_folder)
            show_warning(self.warn_save_path, "Invalid path!")
            self.save_folder_is_ok = False
            self.update_create_and_3d()

    def click_uni_settings(self):
        if_changed, symbols = edit_unicode_convertor_settings(Costumer.make_unicode_will_skip,
                                                              "Unicode convertor settings",
                                                              "Symbols unicode convertor will skip:")

        if if_changed:
            Costumer.make_unicode_will_skip = symbols
            if path.exists(f"{Costumer.path_to_presets}\\{self.chosed_preset.currentText()}\\settings.json"):
                settings = read_json(
                    f"{Costumer.path_to_presets}\\{self.chosed_preset.currentText()}\\settings.json")
                settings["symbols_unicode_convertor_will_skip"] = symbols
                edit_json(
                    f"{Costumer.path_to_presets}\\{self.chosed_preset.currentText()}\\settings.json", settings)

    def all_clear(self):
        while len(Costumer.icons_list) != 0:
            Costumer.icons_list[0].clear_and_set_default()

        while len(Costumer.armor_texture_list) != 0:
            Costumer.armor_texture_list[0].clear_and_set_default()

        self.display_name.setText("")
        self.folder_name.setText("")

        self.folder_name_changed()
        self.display_name_changed()

    def click_3d(self):
        disable_button(self.button_create)
        disable_button(self.button_3d)

        display_name = self.display_name.text()
        unicode_display_name = make_unicode(display_name, Costumer.make_unicode_will_skip)

        path_to_icon_folder = normalize_slash(self.path_to_icon_folder.text())
        leather_armor_layer = normalize_slash(self.leather_armor_layer.text())
        leather_icon_layer = normalize_slash(self.leather_icon_layer.text())

        path_to_preset_folder = f"{Costumer.path_to_presets}\\{self.chosed_preset.currentText()}"

        folder_name = self.folder_name.text()
        folder_name_underscore = folder_name + "_"

        copytree(f"{path_to_preset_folder}\\3D", f"{Costumer.save_folder_path}\\{folder_name_underscore}")

        all_files_properties = []

        for root, _, file in walk(f"{Costumer.save_folder_path}\\{folder_name_underscore}"):
            for file_properties in file:
                if ".properties" in file_properties:
                    all_files_properties.append({"path": root + "\\", "name": file_properties})

        for file_properties in all_files_properties:
            with open(file=file_properties["path"] + file_properties["name"]) as file1:
                file1 = file1.read()
                file1 = file1.replace('FOLDER_NAME', f"{folder_name}")
                file1 = file1.replace('UNICODE_DISPLAY_NAME', unicode_display_name)
                file1 = file1.replace('DISPLAY_NAME', display_name)
                file1 = file1.replace('CHANGEBLE_LEATHER_ARMOR_LAYER', leather_armor_layer)
                file1 = file1.replace('PATH_TO_ICON_FOLDER', path_to_icon_folder)
                file1 = file1.replace('CHANGEBLE_LEATHER_ICON_LAYER', leather_icon_layer)

            with open(file=file_properties["path"] + file_properties["name"], mode='w') as file2:
                file2.write(file1)

            renames(file_properties["path"] + file_properties["name"],
                    file_properties["path"] + folder_name_underscore + file_properties["name"])

    def click_create(self):
        disable_button(self.button_create)
        disable_button(self.button_3d)

        if len(Costumer.armor_texture_list) != 0:
            self.create_main_folder()

        if len(Costumer.icons_list) != 0:
            self.create_icon_folder()

    def create_main_folder(self):
        # Созадет оригинальную папку
        # Копирует нужные папки с файлами пропертис для иконок и текстур моделек брони
        # Копирует выбранные текстуры для моделек брони
        # Редактирует наполнение всех файлов пропертис
        # Копирует нужные файлы для папки 3Д костюма, если нажата нужная кнопкаsave

        display_name = self.display_name.text()
        unicode_display_name = make_unicode(display_name, Costumer.make_unicode_will_skip)

        path_to_icon_folder = normalize_slash(self.path_to_icon_folder.text())
        leather_armor_layer = normalize_slash(self.leather_armor_layer.text())
        leather_icon_layer = normalize_slash(self.leather_icon_layer.text())

        path_to_preset_folder = f"{Costumer.path_to_presets}\\{self.chosed_preset.currentText()}"

        folder_name = self.folder_name.text()
        folder_name_underscore = folder_name + "_"

        mkdir(f"{Costumer.save_folder_path}\\{folder_name_underscore}")

        # Копирование и переименование текстур для брони
        for button in Costumer.armor_texture_list:
            layer_old_name = button.icon.split('/')[-1][0:-4]

            copy(button.icon,
                 f"{Costumer.save_folder_path}\\{folder_name_underscore}")

            renames(f"{Costumer.save_folder_path}\\{folder_name_underscore}\\{layer_old_name}.png",
                    f"{Costumer.save_folder_path}\\{folder_name_underscore}\\{folder_name}_{button.name}.png")

        # Копирование файлов пропертис для брони если не выбрана ни одна иконка
        if len(Costumer.icons_list) == 0:
            for button in Costumer.armor_texture_list:
                if button.name == "layer_1":
                    for armor_part in ['helmet', 'chestplate', 'boots']:
                        copy(f"{path_to_preset_folder}\\armor_file_properties\\{armor_part}.properties",
                             f"{Costumer.save_folder_path}\\{folder_name_underscore}\\{armor_part}"
                             f".properties")

                if button.name == "layer_2":
                    copy(f"{path_to_preset_folder}\\armor_file_properties\\leggings.properties",
                         f"{Costumer.save_folder_path}\\{folder_name_underscore}\\leggings.properties")
        else:
            for button in Costumer.icons_list:
                copy(f"{path_to_preset_folder}\\armor_file_properties\\{button.name}.properties",
                     f"{Costumer.save_folder_path}\\{folder_name_underscore}\\{button.name}.properties")

        all_files_properties = []

        for root, _, file in walk(f"{Costumer.save_folder_path}\\{folder_name_underscore}"):
            for file_properties in file:
                if ".properties" in file_properties:
                    all_files_properties.append({"path": root + "\\", "name": file_properties})

        # Редактирование наполнения файлов пропертис для иконок и переименование этих файлов
        for file_properties in all_files_properties:
            with open(file=file_properties["path"] + file_properties["name"]) as file1:
                file1 = file1.read()
                file1 = file1.replace('PATH_TO_ICON_FOLDER', path_to_icon_folder)
                file1 = file1.replace('FOLDER_NAME', folder_name)
                file1 = file1.replace('UNICODE_DISPLAY_NAME', unicode_display_name)
                file1 = file1.replace('DISPLAY_NAME', display_name)
                file1 = file1.replace('CHANGEBLE_LEATHER_ARMOR_LAYER', leather_armor_layer)
                file1 = file1.replace('CHANGEBLE_LEATHER_ICON_LAYER', leather_icon_layer)

            with open(file=file_properties["path"] + file_properties["name"], mode='w') as file2:
                file2.write(file1)

            renames(file_properties["path"] + file_properties["name"],
                    file_properties["path"] + folder_name_underscore + file_properties["name"])

    def create_icon_folder(self):
        # Создает папку для иконок
        # Накладывает "орбы ресурсов" на иконки костюма перед этим изменив размеры иконки костюма до 16х16

        display_name = self.display_name.text()
        unicode_display_name = make_unicode(display_name, Costumer.make_unicode_will_skip)

        path_to_icon_folder = normalize_slash(self.path_to_icon_folder.text())

        preset_folder = self.chosed_preset.currentText()
        path_to_preset_folder = f"{Costumer.path_to_presets}\\{preset_folder}"
        path_to_ways_for_icons = f"{path_to_preset_folder}\\ways_to_icons"

        leather_armor_layer = normalize_slash(self.leather_armor_layer.text())
        leather_icon_layer = normalize_slash(self.leather_icon_layer.text())

        folder_name = self.folder_name.text()
        folder_name_underscore = folder_name + "_"

        mkdir(f"{Costumer.save_folder_path}\\{folder_name}")

        # for button in Costumer.icons_list:
        #     path_button_folder = \
        #         f"{Costumer.save_folder_path}\\{folder_name_underscore}\\{folder_name}_icons_{button.name}"

        for button in Costumer.icons_list:
            path_button_folder = \
                f"{Costumer.save_folder_path}\\{folder_name_underscore}\\{button.name}"

            copytree(f"{path_to_ways_for_icons}\\{button.name}",
                     path_button_folder)

            for root, _, files in walk(path_button_folder):
                for file_properties in files:
                    if file_properties.split(".")[-1] != "properties":
                        continue

                    properties_name = file_properties.removesuffix(".properties")
                    the_folder = root.split("\\")[-1]

                    global_path_to_overlay_image = f"{path_to_preset_folder}\\overlay_images\\{properties_name}.png"
                    global_path_to_file = root + "\\" + file_properties
                    local_path_to_file = global_path_to_file.replace(path_button_folder, "")

                    local_path_to_save_icon = \
                        normalize_slash(f"{button.name}{local_path_to_file}"
                                        .replace(file_properties,
                                                 f"{folder_name_underscore}{the_folder}_{properties_name}.png"))

                    path_to_save_icon = f"{Costumer.save_folder_path}\\{folder_name}\\{local_path_to_save_icon}"
                    folder_before_icon = \
                        f"{Costumer.save_folder_path}\\{folder_name}\\{button.name}{local_path_to_file}"

                    if not path.exists(folder_before_icon.replace(file_properties, "")):
                        mkdir(folder_before_icon.replace(file_properties, ""))

                    create_icon(button.icon, global_path_to_overlay_image, path_to_save_icon)

                    with open(file=global_path_to_file, mode="r", encoding="utf-8") as original_file_properties:
                        original_file_properties = original_file_properties.read()

                    original_file_properties = \
                        original_file_properties.replace('PATH_TO_ICON_FOLDER', path_to_icon_folder)
                    original_file_properties = \
                        original_file_properties.replace('FOLDER_NAME', folder_name)
                    original_file_properties = \
                        original_file_properties.replace('UNICODE_DISPLAY_NAME', unicode_display_name)
                    original_file_properties = \
                        original_file_properties.replace('DISPLAY_NAME', display_name)
                    original_file_properties = \
                        original_file_properties.replace('CHANGEBLE_LEATHER_ARMOR_LAYER', leather_armor_layer)
                    original_file_properties = \
                        original_file_properties.replace('CHANGEBLE_LEATHER_ICON_LAYER', leather_icon_layer)
                    original_file_properties = \
                        original_file_properties.replace('PATH_TO_ICON_IN_ICON_FOLDER', local_path_to_save_icon)

                    with open(file=global_path_to_file, mode="w", encoding="utf-8") as new_file_properties:
                        new_file_properties.write(original_file_properties)

                    renames(global_path_to_file,
                            global_path_to_file.replace(file_properties,
                                                        f"{folder_name_underscore}{the_folder}_{file_properties}"))

            renames(path_button_folder,
                    f"{Costumer.save_folder_path}\\{folder_name_underscore}\\{folder_name}_icons_{button.name}")

    def closeEvent(self, event):
        Costumer.kill_threads = True
        self.created_folder_check_thread.join()
        self.preset_folder_check_thread.join()

        settings = read_json(Costumer.settings_json)
        settings["last_preset"] = self.chosed_preset.currentText()
        edit_json(Costumer.settings_json, settings)
        event.accept()

    def watch_preset_folder_thread(self) -> None:
        costumator_not_active = True

        while True:
            if Costumer.kill_threads:
                break

            if not self.isActiveWindow():
                costumator_not_active = True

            if self.isActiveWindow() and costumator_not_active:
                costumator_not_active = False
                self.update_presets()

            sleep(0.1)

    def watch_created_costume_folder_thread(self) -> None:
        folders = None

        while True:
            if Costumer.kill_threads:
                break

            if [path.exists(f"{Costumer.save_folder_path}\\{self.folder_name.text()}"),
                    path.exists(f"{Costumer.save_folder_path}\\{self.folder_name.text()}_")] != folders:
                folders = [path.exists(f"{Costumer.save_folder_path}\\{self.folder_name.text()}"),
                           path.exists(f"{Costumer.save_folder_path}\\{self.folder_name.text()}_")]
                self.folder_name_changed()

            sleep(1)


def excepthook(type1, value, tb):
    try:
        costumator.close()
    except NameError:
        pass

    error_message = ''.join(traceback.format_exception(type1, value, tb))

    if not path.exists(Costumer.logs_folder):
        mkdir(Costumer.logs_folder)

    with open(file=f"{Costumer.logs_folder}\\{strftime('%Y.%m.%d %H_%M_%S ') + str(time_ns())}.txt", mode="w") as logs:
        logs.write(error_message)


sys.excepthook = excepthook


def main() -> None:
    app = QApplication(sys.argv)
    costumator = Costumer()
    costumator.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
