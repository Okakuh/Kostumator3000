from os import getcwd

name: str = "Kostumator3000"
version: str = "1.1"

title: str = f"{name} {version}"

# Main costume folder suffix
folder_suffix = "_"

# Folder names
name_in_preset_3d: str = "3d"
name_in_preset_armor_files_properties: str = "armor_file_properties"
name_in_preset_overlay_images: str = "overlay_images"
name_in_preset_ways_to_icons: str = "icons"


# Pathes and files
the_fldr: str = f"{getcwd()}/{name} {version}"
p_fldr_program: str = f"{the_fldr}/Program"

p_fldr_presets: str = f"{the_fldr}/Presets"

p_file_ui: str = f"{p_fldr_program}/costumator.ui"
p_program_settings_json: str = f"{p_fldr_program}/settings.json"


# Pathes to default TextureButtons images
p_fldr_empty_texture_buttons: str = f"{p_fldr_program}/Icons/Empty TextureButton"

p_icon_button_disabled: str = f"{p_fldr_program}/Icons/no_folder.png"

p_empty_texture_button_helmet: str = f"{p_fldr_empty_texture_buttons}/helmet.png"
p_empty_texture_button_boots: str = f"{p_fldr_empty_texture_buttons}/boots.png"
p_empty_texture_button_chestplate: str = f"{p_fldr_empty_texture_buttons}/chestplate.png"
p_empty_texture_button_leggings: str = f"{p_fldr_empty_texture_buttons}/leggings.png"

p_empty_texture_button_layer_1: str = f"{p_fldr_empty_texture_buttons}/layer_1.png"
p_empty_texture_button_layer_2: str = f"{p_fldr_empty_texture_buttons}/layer_2.png"


# Button styles
button_enabled_style: str = "background-color: rgb(31, 30, 30); " \
                            "border-radius: 5px; " \
                            "border: 2px solid  rgb(74, 74, 74); " \
                            "color: rgb(255, 255, 255)"

button_disabled_style: str = "background-color: rgb(15, 15, 15); " \
                             "border-radius: 5px; " \
                             "border: 2px solid  rgb(23, 23, 23); " \
                             "color: rgb(64, 64, 64)"

# Error messages
folder_name_errors = {1: "Required field!",
                      2: "Delete or move existing folders!"}
save_path_errors = {1: "Required field!",
                    2: "Invalid path!"}
