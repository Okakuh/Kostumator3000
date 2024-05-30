from os import getcwd

icons_buttons = ['helmet', 'chestplate', 'leggings', 'boots']
armor_buttons = ['layer_1', 'layer_2']

main_path = getcwd()

settings_json = f"{main_path}\\program\\settings.json"
path_to_presets = f"{main_path}\\program\\presets"
make_unicode_will_skip = ""

last_preset_folder_state = None
kill_threads = False

icons_list = []
armor_texture_list = []

save_folder_path = ''

button_enabled_style = "background-color: rgb(30, 30, 30); " \
                 "border-radius: 5px; " \
                 "border: 2px solid  rgb(74, 74, 74); " \
                 "color: rgb(255, 255, 255)"

button_disabled_style = "background-color: rgb(15, 15, 15); " \
                  "border-radius: 5px; " \
                  "border: 2px solid  rgb(23, 23, 23); " \
                  "color: rgb(64, 64, 64)"
