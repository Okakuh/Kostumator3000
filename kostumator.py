from time import sleep
from os import listdir, path, mkdir, renames, walk
from shutil import copy, copytree
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QComboBox
from threading import Thread
from pyperclip import copy as copy_to_clipboard
import sys
from pathlib import Path

from functions import *
from cclass import *
import settings


class Costumator(QWidget):
    def __init__(self):
        super().__init__()

        # Load ui -----------------------------------------------------------------------------------------------------

        self.ui = uic.loadUi(settings.p_file_ui, self)

        # Set types for ui widgets -----------------------------------------------------------------------------------

        # ComboBox for presets
        self.presets: QComboBox = self.presets

        # Preset buttons
        self.button_set_preset_settings: QPushButton = self.button_set_preset_settings
        self.button_set_current_settings_to_preset: QPushButton = self.button_set_current_settings_to_preset
        self.button_open_in_explorer_preset: QPushButton = self.button_open_in_explorer_preset

        # Display name buttons
        self.button_copy_unicode_display_name: QPushButton = self.button_copy_unicode_display_name
        self.button_open_unicode_convertor_settings: QPushButton = self.button_open_unicode_convertor_settings

        # Folder names button
        self.button_delete_created_folders: QPushButton = self.button_delete_created_folders
        self.button_open_in_explorer_save_folder: QPushButton = self.button_open_in_explorer_save_folder

        # LineEdit's and maket for save folder LineEdit
        self.display_name: QLineEdit = self.display_name
        self.folder_name: QLineEdit = self.folder_name
        self.maket_save_folder: QLineEdit = self.maket_save_folder
        self.path_to_icon_folder: QLineEdit = self.path_to_icon_folder
        self.leather_armor_layer: QLineEdit = self.leather_armor_layer
        self.leather_icon_layer: QLineEdit = self.leather_icon_layer

        # Makets  for IconButton's
        self.maket_helmet: QPushButton = self.maket_helmet
        self.maket_chestplate: QPushButton = self.maket_chestplate
        self.maket_leggings: QPushButton = self.maket_leggings
        self.maket_boots: QPushButton = self.maket_boots

        # Makets  for ArmorButton's
        self.maket_layer_1: QPushButton = self.maket_layer_1
        self.maket_layer_2: QPushButton = self.maket_layer_2

        # Main buttons
        self.button_3d: QPushButton = self.button_3d
        self.button_clear: QPushButton = self.button_clear
        self.button_create: QPushButton = self.button_create

        # Create my widgets -------------------------------------------------------------------------------------------

        self.save_folder = MyLineEdit(self, maket_text_edit=self.maket_save_folder)

        self.button_helmet = IconButton(self, 'helmet', self.maket_helmet, settings.p_empty_texture_button_helmet)
        self.button_chestplate = IconButton(self, 'chestplate', self.maket_chestplate,
                                            settings.p_empty_texture_button_chestplate)
        self.button_leggings = IconButton(self, 'leggings', self.maket_leggings,
                                          settings.p_empty_texture_button_leggings)
        self.button_boots = IconButton(self, 'boots', self.maket_boots, settings.p_empty_texture_button_boots)

        self.button_layer_1 = ArmorButton(self, self.maket_layer_1, settings.p_empty_texture_button_layer_1)
        self.button_layer_2 = ArmorButton(self, self.maket_layer_2, settings.p_empty_texture_button_layer_2)

        # Costumator parameters ---------------------------------------------------------------------------------------

        self.symbols_unicode_convertor_skips: str = ""
        self.p_save_folder: str = ""

        self.kill_threads: bool = False

        self.save_folder_is_ok: bool = False
        self.presets_is_ok: bool = False
        self.folder_name_is_ok: bool = False

        # Widgets id for settings.json in preset
        self.widgets_id_for_preset_settings_json = {"Display name": self.display_name,
                                                    "Folder name": self.folder_name,
                                                    "Save costume to": self.save_folder,
                                                    "Path to icon folder": self.path_to_icon_folder,
                                                    "Path to leather armor changeble layer": self.leather_armor_layer,
                                                    "Path to leather armor icon changeble layer": self.leather_icon_layer}

        # Created icon/armor buttons
        self.icon_buttons: list[IconButton] = [self.button_helmet, self.button_chestplate, self.button_leggings, self.button_boots]
        self.armor_buttons: list[ArmorButton] = [self.button_layer_1, self.button_layer_2]

        # On start code------------------------------------------------------------------------------------------------

        self.set_window_settings()
        self.wingets_connect_events()

        # Set last used preset to preset list
        last_used_preset = read_json(settings.p_program_settings_json)["last_preset"]
        self.presets.addItem(last_used_preset)
        self.presets.setCurrentText(last_used_preset)

        # Threads
        self.created_folder_check_thread = Thread(target=self.thread_watch_created_costume_folders)
        self.created_folder_check_thread.start()

        self.preset_folder_check_thread = Thread(target=self.thread_watch_presets_folder)
        self.preset_folder_check_thread.start()

        self.slide_show_thread = Thread(target=self.thread_slide_show_icons)
        self.slide_show_thread.start()

    def set_window_settings(self) -> None:
        self.setWindowTitle(settings.title)

        self.setMinimumSize(self.ui.geometry().width(), self.ui.geometry().height())
        self.setMaximumSize(self.ui.geometry().width(), self.ui.geometry().height())

    def wingets_connect_events(self) -> None:
        # Main buttons create, create 3d, clear------------------------------------------------------------------------
        self.button_create.clicked.connect(self.click_create)
        self.button_3d.clicked.connect(self.click_3d)
        self.button_clear.clicked.connect(self.all_clear)

        # Display name buttons-----------------------------------------------------------------------------------------
        self.button_copy_unicode_display_name.clicked.connect(lambda: copy_to_clipboard(make_unicode(self.display_name.text(),
                                                                    self.symbols_unicode_convertor_skips)))
        self.button_open_unicode_convertor_settings.clicked.connect(self.click_uni_settings)

        # Save folder buttons------------------------------------------------------------------------------------------
        self.button_open_in_explorer_save_folder.clicked.connect(lambda: open_in_explorer(self.p_save_folder))
        self.button_delete_created_folders.clicked.connect(self.delete_existing_folders)

        # Preset buttons-----------------------------------------------------------------------------------------------
        self.button_set_preset_settings.clicked.connect(self.set_preset_settings)
        self.button_set_current_settings_to_preset.clicked.connect(self.set_current_settings_as_preset_default)
        self.button_open_in_explorer_preset.clicked.connect(lambda: open_in_explorer(settings.p_fldr_presets))

        # LineEdit.textEdited.connect-------------------------------------------------------------------------------
        self.save_folder.textEdited.connect(self.save_path_changed)
        self.display_name.textEdited.connect(self.display_name_changed)
        self.folder_name.textEdited.connect(self.folder_name_changed)

        self.presets.currentTextChanged.connect(self.set_preset_settings)

    def set_current_settings_as_preset_default(self) -> None:
        dlg = AskSureDialog("Sure?", "Set current settings as preset default?")

        if dlg.exec():
            settings_json = f"{settings.p_fldr_presets}\\{self.presets.currentText()}\\settings.json"

            program_settings = read_json(settings_json)

            for json_widget_id, program_widget in self.widgets_id_for_preset_settings_json.items():
                program_settings["input_fields_text"][json_widget_id] = program_widget.text()

            write_json(settings_json, program_settings)

    def delete_existing_folders(self) -> None:
        ask = AskSureDialog("Sure?", "Delete folders with this name?")
        if ask.exec():
            delete_folders([f"{self.p_save_folder}/{self.folder_name.text()}",
                            f"{self.p_save_folder}/{self.folder_name.text()}_"])

            self.folder_name_changed()

    def update_presets(self) -> None:
        last_chosed_preset: str = self.presets.currentText()

        preset_list = [preset for preset in listdir(settings.p_fldr_presets) if path.isdir(f"{settings.p_fldr_presets}/{preset}")]

        self.presets.clear()

        for preset_folder in preset_list:
            self.presets.addItem(preset_folder)

        if last_chosed_preset != "" and last_chosed_preset in preset_list:
            self.presets.setCurrentText(last_chosed_preset)
        else:
            if preset_list:
                self.presets.setCurrentText(preset_list[0])

        if self.presets.currentText() != "":
            hide_warning(self.warn_preset)
            self.presets_is_ok = True

            self.set_preset_settings()

            enable_button(self.button_set_current_settings_to_preset)
            enable_button(self.button_set_preset_settings)
        else:
            self.presets_is_ok = False

            show_warning(self.warn_preset, "No presets found!")

            disable_button(self.button_set_current_settings_to_preset)
            disable_button(self.button_set_preset_settings)

            self.save_path_changed()

    def set_preset_settings(self) -> None:
        self.all_clear()
        preset_folder = self.presets.currentText()

        if not preset_folder:
            return

        path_to_preset_settings_json = f"{settings.p_fldr_presets}\\{preset_folder}\\settings.json"
        preset_settings = read_json(path_to_preset_settings_json)

        for json_widget_name, text in preset_settings["input_fields_text"].items():
            self.widgets_id_for_preset_settings_json[json_widget_name].setText(text)

        self.symbols_unicode_convertor_skips = preset_settings["symbols_unicode_convertor_will_skip"]

        preset_icon_folders = listdir(f"{settings.p_fldr_presets}/{preset_folder}/{settings.name_in_preset_ways_to_icons}")
        for icon_button in self.icon_buttons:
            if icon_button.folder_in_preset in preset_icon_folders:
                icon_button.enable()
            else:
                icon_button.disable()

        if not self.button_helmet.isEnabled() and not self.button_chestplate.isEnabled() and not self.button_boots.isEnabled():
            self.button_layer_1.setEnabled(False)
        else:
            self.button_layer_1.setEnabled(True)

        if not self.button_leggings.isEnabled():
            self.button_layer_2.setEnabled(False)
        else:
            self.button_layer_2.setEnabled(True)

        self.display_name_changed()
        self.save_path_changed()

    def display_name_changed(self) -> None:
        text = self.display_name.text()

        text = text.replace("\\", "").replace("№", "").replace("?", "").replace("§", "")
        if len(text) > 50:
            text = text[0:50]
            self.display_name_max_len.setStyleSheet("color: rgb(255, 75, 68)")
        else:
            self.display_name_max_len.setStyleSheet("color: rgb(255, 255, 255)")

        if text != '':
            enable_button(self.button_copy_unicode_display_name)
        else:
            disable_button(self.button_copy_unicode_display_name)

        self.display_name.setText(text)
        self.display_name_max_len.setText(f"{len(text)}/50")

    def folder_name_changed(self) -> None:
        hide_warning(self.warn_folder)
        error = ErrorID()
        text = self.folder_name.text()

        text = text.replace(" ", "_")
        text = text.lower()
        text = "".join([char for char in text if char in "qwertyuiopasdfghjklzxcvbnm1234567890_"])

        if not text:
            error.set_id(1)
            disable_button(self.button_delete_created_folders)
        elif text:
            enable_button(self.button_delete_created_folders)

            if path.exists(f"{self.p_save_folder}\\{text}_") or path.exists(f"{self.p_save_folder}\\{text}"):
                error.set_id(2)
                enable_button(self.button_delete_created_folders)
            else:
                disable_button(self.button_delete_created_folders)

        error_id = error.get_id()
        if error_id:
            self.folder_name_is_ok = False
            show_warning(self.warn_folder, settings.folder_name_errors[error_id])
        else:
            self.folder_name_is_ok = True

        self.folder_name.setText(text)
        self.update_create_and_3d()

    def update_create_and_3d(self) -> None:
        if not self.presets_is_ok or not self.folder_name_is_ok or not self.save_folder_is_ok:
            disable_button(self.button_create)
            disable_button(self.button_3d)
        else:
            enable_button(self.button_create)
            enable_button(self.button_3d)

    def save_path_changed(self) -> None:
        text = self.save_folder.text()
        error = ErrorID()

        if not text:
            error.set_id(1)

        if not error.get_id():
            if not path.exists(text):
                error.set_id(2)

        if error.get_id():
            disable_button(self.button_open_in_explorer_save_folder)
            show_warning(self.warn_save_path, settings.save_path_errors[error.get_id()])
            self.save_folder_is_ok = False
        else:
            hide_warning(self.warn_save_path)
            enable_button(self.button_open_in_explorer_save_folder)
            self.p_save_folder = normalize_path(text)
            self.save_folder_is_ok = True
            self.folder_name_changed()

        self.update_create_and_3d()

    def click_uni_settings(self) -> None:
        title = "Unicode convertor settings"
        message = "Symbols unicode convertor will skip:"

        unicode_settings = UnicodeConvertorSettings(title, message, self.symbols_unicode_convertor_skips)

        if unicode_settings.exec():
            self.symbols_unicode_convertor_skips = unicode_settings.symbols.toPlainText()
            
            current_preset = self.presets.currentText()
            path_to_current_preset_settings = f"{settings.p_fldr_presets}/{current_preset}/settings.json"

            program_settings = read_json(path_to_current_preset_settings)
            program_settings["symbols_unicode_convertor_will_skip"] = self.symbols_unicode_convertor_skips
            write_json(path_to_current_preset_settings, program_settings)

    def all_clear(self) -> None:
        for button in self.icon_buttons:
            button.clear()

        for button in self.armor_buttons:
            button.clear()

        self.display_name.setText("")
        self.folder_name.setText("")

        self.folder_name_changed()
        self.display_name_changed()

    def click_3d(self) -> None:
        disable_button(self.button_create)
        disable_button(self.button_3d)

        display_name = self.display_name.text()
        unicode_display_name = make_unicode(display_name, self.symbols_unicode_convertor_skips)

        path_to_icon_folder = normalize_path(self.path_to_icon_folder.text())
        leather_armor_layer = normalize_path(self.leather_armor_layer.text())
        leather_icon_layer = normalize_path(self.leather_icon_layer.text())

        path_to_current_preset_folder = f"{settings.p_fldr_presets}\\{self.presets.currentText()}"

        folder_name = self.folder_name.text()
        folder_name_underscore = folder_name + settings.folder_suffix

        copytree(f"{path_to_current_preset_folder}/{settings.name_in_preset_3d}", f"{self.p_save_folder}/{folder_name_underscore}")

        all_files_properties = []

        for root, _, files in walk(f"{self.p_save_folder}\\{folder_name_underscore}"):
            for file_properties in files:
                if Path(file_properties).suffix == ".properties":
                    all_files_properties.append({"path": root + "\\", "name": file_properties})

        for file_properties in all_files_properties:
            path_to_file_properties = file_properties["path"] + file_properties["name"]
            parameters_to_replace = {
                "FOLDER_NAME": folder_name,
                "UNICODE_DISPLAY_NAME": unicode_display_name,
                "DISPLAY_NAME": display_name,
                "CHANGEBLE_LEATHER_ARMOR_LAYER": leather_armor_layer,
                "PATH_TO_ICON_FOLDER": path_to_icon_folder,
                "CHANGEBLE_LEATHER_ICON_LAYER": leather_icon_layer
            }

            edit_file_properties(file=path_to_file_properties, data_to_replase=parameters_to_replace)

            renames(path_to_file_properties, file_properties["path"] + folder_name_underscore + file_properties["name"])

    def click_create(self) -> None:
        disable_button(self.button_create)
        disable_button(self.button_3d)

        self.create_main_folder()

        if self.valid_icons():
            self.create_icon_folder()

    def valid_icons(self) -> list[IconButton]:
        return [icon_button for icon_button in self.icon_buttons if icon_button.valid()]

    def valid_armors(self) -> list[ArmorButton]:
        return [armor_button for armor_button in self.armor_buttons if armor_button.valid()]

    def create_main_folder(self) -> None:
        # Созадет оригинальную папку
        # Копирует нужные папки с файлами пропертис для иконок и текстур моделек брони
        # Копирует выбранные текстуры для моделек брони
        # Редактирует наполнение всех файлов пропертис

        display_name = self.display_name.text()
        unicode_display_name = make_unicode(display_name, self.symbols_unicode_convertor_skips)

        path_to_icon_folder = normalize_path(self.path_to_icon_folder.text())
        leather_armor_layer = normalize_path(self.leather_armor_layer.text())
        leather_icon_layer = normalize_path(self.leather_icon_layer.text())

        path_to_preset_folder = f"{settings.p_fldr_presets}\\{self.presets.currentText()}"

        folder_name = self.folder_name.text()
        folder_name_underscore = folder_name + settings.folder_suffix

        valid_icon_buttons = self.valid_icons()
        valid_armor_buttons = self.valid_armors()
        
        mkdir(f"{self.p_save_folder}\\{folder_name_underscore}")

        # Копирование и переименование текстур для брони
        if valid_armor_buttons:
            if self.button_layer_1 in valid_armor_buttons:
                layer_old_name = Path(self.button_layer_1.get_icon()).stem

                copy(self.button_layer_1.get_icon(), f"{self.p_save_folder}\\{folder_name_underscore}")

                renames(f"{self.p_save_folder}\\{folder_name_underscore}\\{layer_old_name}.png",
                        f"{self.p_save_folder}\\{folder_name_underscore}\\{folder_name}_layer_1.png")

            if self.button_layer_2 in valid_armor_buttons:
                layer_old_name = Path(self.button_layer_2.get_icon()).stem

                copy(self.button_layer_2.get_icon(), f"{self.p_save_folder}\\{folder_name_underscore}")

                renames(f"{self.p_save_folder}\\{folder_name_underscore}\\{layer_old_name}.png",
                        f"{self.p_save_folder}\\{folder_name_underscore}\\{folder_name}_layer_2.png")

        # Копирование файлов пропертис для брони
        if valid_icon_buttons:
            for button in valid_icon_buttons:
                button_folder_in_preset = button.folder_in_preset
                copy(
                    f"{path_to_preset_folder}\\{settings.name_in_preset_armor_files_properties}\\{button_folder_in_preset}.properties",
                    f"{self.p_save_folder}\\{folder_name_underscore}\\{button_folder_in_preset}.properties")

        all_files_properties = []

        for root, _, file in walk(f"{self.p_save_folder}\\{folder_name_underscore}"):
            for file_properties in file:
                if ".properties" in file_properties:
                    all_files_properties.append({"path": root + "\\", "name": file_properties})

        # Редактирование наполнения файлов пропертис для иконок и переименование этих файлов
        for file_properties in all_files_properties:
            path_to_file_properties = file_properties["path"] + file_properties["name"]
            parameters_to_replace = {
                "FOLDER_NAME": folder_name,
                "UNICODE_DISPLAY_NAME": unicode_display_name,
                "DISPLAY_NAME": display_name,
                "CHANGEBLE_LEATHER_ARMOR_LAYER": leather_armor_layer,
                "PATH_TO_ICON_FOLDER": path_to_icon_folder,
                "CHANGEBLE_LEATHER_ICON_LAYER": leather_icon_layer
            }

            edit_file_properties(file=path_to_file_properties, data_to_replase=parameters_to_replace)

            renames(path_to_file_properties,
                    file_properties["path"] + folder_name_underscore + file_properties["name"])

    def create_icon_folder(self) -> None:
        # Создает папку для иконок
        # Накладывает "орбы ресурсов" на иконки костюма перед этим изменив размеры иконки костюма до 16х16

        display_name = self.display_name.text()
        unicode_display_name = make_unicode(display_name, self.symbols_unicode_convertor_skips)

        path_to_icon_folder = normalize_path(self.path_to_icon_folder.text())

        preset_folder = self.presets.currentText()
        path_to_current_preset_folder = f"{settings.p_fldr_presets}\\{preset_folder}"
        path_to_ways_to_icons_in_current_preset = f"{path_to_current_preset_folder}\\{settings.name_in_preset_ways_to_icons}"

        leather_armor_layer = normalize_path(self.leather_armor_layer.text())
        leather_icon_layer = normalize_path(self.leather_icon_layer.text())

        folder_name = self.folder_name.text()
        folder_name_underscore = folder_name + settings.folder_suffix

        valid_icon_buttons = self.valid_icons()

        mkdir(f"{self.p_save_folder}\\{folder_name}")

        for button in valid_icon_buttons:
            button_folder_in_preset = button.folder_in_preset
            path_to_button_folder_in_save_folder = f"{self.p_save_folder}/{folder_name_underscore}/{button_folder_in_preset}"

            copytree(f"{path_to_ways_to_icons_in_current_preset}/{button_folder_in_preset}", path_to_button_folder_in_save_folder)

            for root, _, files in walk(path_to_button_folder_in_save_folder):
                for file_properties in files:
                    if Path(file_properties).suffix != ".properties":
                        continue

                    properties_name = Path(file_properties).stem

                    global_path_to_overlay_image = f"{path_to_current_preset_folder}\\{settings.name_in_preset_overlay_images}\\{properties_name}.png"
                    global_path_to_file_properties = f"{root}\\{file_properties}"
                    local_path_to_file_properties = global_path_to_file_properties.replace(f"{path_to_button_folder_in_save_folder}\\", "")

                    overlay_image_name = f"{folder_name_underscore}{button_folder_in_preset}_{properties_name}.png"
                    local_path_to_save_icon = f"{button_folder_in_preset}\\{local_path_to_file_properties}".replace(file_properties, overlay_image_name)

                    global_path_to_save_icon = f"{self.p_save_folder}\\{folder_name}\\{local_path_to_save_icon}"
                    folder_before_icon = Path(global_path_to_save_icon).parent

                    if not path.exists(folder_before_icon):
                        mkdir(folder_before_icon)

                    new_icon = merge_images(button.user_icon, global_path_to_overlay_image)
                    new_icon.save(global_path_to_save_icon, quality=100)

                    parameters_to_replace = {
                        "FOLDER_NAME": folder_name,
                        "UNICODE_DISPLAY_NAME": unicode_display_name,
                        "DISPLAY_NAME": display_name,
                        "CHANGEBLE_LEATHER_ARMOR_LAYER": leather_armor_layer,
                        "PATH_TO_ICON_FOLDER": normalize_path(path_to_icon_folder),
                        "CHANGEBLE_LEATHER_ICON_LAYER": leather_icon_layer,
                        "PATH_TO_ICON_IN_ICON_FOLDER": normalize_path(local_path_to_save_icon)
                    }

                    edit_file_properties(file=global_path_to_file_properties, data_to_replase=parameters_to_replace)

                    new_file_name = f"{folder_name_underscore}{button_folder_in_preset}_{file_properties}"
                    new_path = global_path_to_file_properties.replace(file_properties, new_file_name)
                    renames(global_path_to_file_properties, new_path)

            renames(path_to_button_folder_in_save_folder,
                    f"{self.p_save_folder}\\{folder_name_underscore}\\{folder_name}_icons_{button_folder_in_preset}")

    def closeEvent(self, event) -> None:
        self.kill_threads = True

        program_settings = read_json(settings.p_program_settings_json)
        program_settings["last_preset"] = self.presets.currentText()
        write_json(settings.p_program_settings_json, program_settings)
        event.accept()

    def thread_watch_presets_folder(self) -> None:
        costumator_not_in_focus = True
        last_preset_folder_state = None

        while not self.kill_threads:
            if not self.isActiveWindow():
                costumator_not_in_focus = True

            if self.isActiveWindow() and costumator_not_in_focus:
                costumator_not_in_focus = False
                
                current_state_of_presets_folder = listdir(settings.p_fldr_presets)

                if last_preset_folder_state != current_state_of_presets_folder:
                    last_preset_folder_state = current_state_of_presets_folder
                    self.update_presets()

            sleep(0.1)

    def thread_watch_created_costume_folders(self) -> None:
        folders = None

        while not self.kill_threads:
            folder_name = self.folder_name.text()
            if [path.exists(f"{self.p_save_folder}\\{folder_name}"), path.exists(
                    f"{self.p_save_folder}\\{folder_name}_")] != folders:
                folders = [path.exists(f"{self.p_save_folder}\\{folder_name}"),
                           path.exists(f"{self.p_save_folder}\\{folder_name}_")]
                self.folder_name_changed()

            sleep(1)

    def thread_slide_show_icons(self) -> None:
        while not self.kill_threads:
            current_preset = self.presets.currentText()
            self.button_helmet.slide_show(current_preset)
            self.button_chestplate.slide_show(current_preset)
            self.button_leggings.slide_show(current_preset)
            self.button_boots.slide_show(current_preset)
            sleep(1)


def main() -> None:
    app = QApplication(sys.argv)
    costumator = Costumator()
    costumator.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
