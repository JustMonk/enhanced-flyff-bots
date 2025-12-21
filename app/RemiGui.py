"""
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import json
import os
import time
from pathlib import Path
import threading
import remi.gui as gui
from remi import App
from utils.helpers import get_window_handlers
import numpy
import cv2 as cv
import base64
from components.ListMultiselectView import ListMultiselectView
from components.LabeledSlider import LabeledSlider
from components.Logo import Logo
from components.SectionCard import SectionCard
from hotkey import global_listener
from key_sender import send_to_window
from pynput.keyboard import Key
import shutil

class RemiApp(App):
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.config_file = Path("app_config.json")
        instance.config = {
            # app config
            # 'attached_window': None,
            # show_bot_vision: always False
            # bot show options
            'show_matches_text': True,
            'show_mobs_boxes': True,
            'show_mobs_markers': True,
            # threshold options
            'mob_position_match_threshold': 0.7,
            'mob_still_alive_match_threshold': 0.7,
            'mob_existence_match_threshold': 0.7,
            'inventory_perin_match_threshold': 0.7,
            'inventory_icons_match_threshold': 0.7,
            # fight options
            "mobs_kill_goal": None,
            "fight_time_limit_sec": 8,
            "delay_to_check_mob_still_alive_sec": 0.25,
            # "convert_penya_to_perins_timer_min": 30,
            "selected_mobs": [],
        }
        return instance

    def __init__(self, *args, **kwargs):
        res_path = os.path.join(os.path.dirname(__file__), 'static')
        self.show_bot_vision = False
        self.attached_window = None
        super(RemiApp, self).__init__(*args, static_file_path={'static': res_path})

    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.config.update(loaded_config)
            else:
                self.save_config()  # Create default config file
        except Exception as e:
            print(f"Error loading config: {e}")

    def update_bot_config(self, bot):
        # TODO: тут бы еще регенерацию конфига, если типы не совпадают с ожидаемым (или функцию валидации)
        all_mobs = bot.get_all_mobs()
        selected_mobs_names = self.config['selected_mobs']
        selected_mobs_names = [name for name in selected_mobs_names if name in all_mobs] # exist filter
        selected_mobs_list = [all_mobs[key] for key in all_mobs if key in selected_mobs_names]

        bot.set_config(
            # TODO: тут надо читать состяние checkbox из апп (оно не пишется в стор)
            # show_frames= ...
            show_frames=self.show_bot_vision,
            show_mobs_pos_boxes=self.config.get('show_mobs_boxes'),
            show_mobs_pos_markers=self.config.get('show_mobs_markers'),
            show_matches_text=self.config.get('show_matches_text'),
            mob_pos_match_threshold=self.config.get('mob_position_match_threshold'),
            mob_still_alive_match_threshold=self.config.get('mob_still_alive_match_threshold'),
            mob_existence_match_threshold=self.config.get('mob_existence_match_threshold'),
            inventory_perin_converter_match_threshold=self.config.get('inventory_perin_match_threshold'),
            inventory_icons_match_threshold=self.config.get('inventory_icons_match_threshold'),
            mobs_kill_goal=self.config.get('mobs_kill_goal'),
            fight_time_limit_sec=self.config.get('fight_time_limit_sec'),
            delay_to_check_mob_still_alive_sec=self.config.get('delay_to_check_mob_still_alive_sec'),
            # convert_penya_to_perins_timer_min=self.config.get('convert_penya_to_perins_timer_min'),
            selected_mobs=selected_mobs_list,
        )

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def set_config(self, **options):
        for key, value in options.items():
            self.config[key] = value
        self.save_config()
        # sync app config with bot
        self.update_bot_config(self.bot)

    def idle(self):
        #self.counter.set_text('Running Time: ' + str(self.count))
        # self.progress.set_value(self.count%100)
        pass
    
    def on_stop_hotkey(self):
        self.append_status_log("Stop hotkey triggered, bot is going to stop...")
        self.stop_bot()

    def main(self, bot):
        self.page.children['head'].add_child('additional_headdata', f'<link rel="stylesheet" href="/static:style.css&t={int(time.time())}">')

        self.bot = bot
        self.load_config()
        self.update_bot_config(self.bot)

        listener_thread = threading.Thread(target=global_listener, args=(self,), daemon=True)
        listener_thread.start()

        # the margin 0px auto centers the main container
        mainWrapperContainer = gui.Container(width=540, margin='0px auto', style={'display': 'block', 'overflow': 'hidden', 'padding': '20px', 'box-shadow': 'none', 'background': 'transparent'})
        self.mainWrapperContainer = mainWrapperContainer

        mainWrapperContainer.append(Logo())

        # <------------------ [ACTIONS BLOCK] ------------------>
        self.actionsContainer_attach_bt = gui.Button('Attach window', width='100%', margin='10px', _class='Button main-button')
        self.actionsContainer_attach_bt.onclick.do(self.open_attach_window_popup)
        
        self.actionsContainer_start_bt = gui.Button('Start', width=200, height=30, margin='10px')
        self.actionsContainer_start_bt.onclick.do(lambda w: self.start_bot())

        self.actionsContainer_stop_bt = gui.Button('Stop (alt+s)', width=200, height=30, margin='10px')
        self.actionsContainer_stop_bt.onclick.do(lambda w: self.stop_bot())

        self.start_stop_bt = gui.Button('Start', width='100%', margin='10px', _class='Button main-button disabled-button')
        self.start_stop_bt.onclick.do(self.toggle_bot_state)

        self.actionsContainer_exit_bt = gui.Button('Exit', width=200, height=30, margin='10px')
        self.actionsContainer_exit_bt.onclick.do(self.exit)

        self.actionsContainer_current_attached_label = gui.Label('', margin='0', style={'width': 'auto', 'white-space': 'pre', 'overflow': 'hidden', 'height': 'auto', 'color': '#007ec2', 'margin-top': '5px'})

        self.send_keys_bt = gui.Button('send keys', width=200, height=30, margin='10px')
        self.send_keys_bt.onclick.do(lambda w: send_to_window(self.bot.keyboard.hwnd, Key.f1))

        actionsCard = SectionCard([
            gui.Container([
                self.actionsContainer_attach_bt,
                self.start_stop_bt
                # self.actionsContainer_start_bt,
                # self.actionsContainer_stop_bt,
                # self.actionsContainer_exit_bt
            ], margin='0px auto', style={'overflow': 'hidden', 'width': '100%', 'display': 'flex', 'justify-content': 'space-around'}),
            self.actionsContainer_current_attached_label,
            # self.send_keys_bt
        ], header='Actions')
        mainWrapperContainer.append([actionsCard])
        # </------------------ [ACTIONS BLOCK] ------------------>

        # <------------------ [MOBS BLOCK] ------------------>
        self.mobsContainer_select_mobs_bt = gui.Button('Select mobs', margin='10px', _class='Button main-button')
        self.mobsContainer_select_mobs_bt.onclick.do(self.open_select_mobs_dialog)
        self.mobsContainer_add_mob_bt = gui.Button('Add mob', margin='10px', _class='Button main-button')
        self.mobsContainer_add_mob_bt.onclick.do(self.open_add_mob_dialog)
        self.mobsContainer_delete_mobs_bt = gui.Button('Delete mobs', margin='10px', _class='Button main-button')
        self.mobsContainer_delete_mobs_bt.onclick.do(self.open_delete_mob_dialog)

        mobsCard = SectionCard([
            gui.Container([
                self.mobsContainer_select_mobs_bt,
                self.mobsContainer_add_mob_bt,
                self.mobsContainer_delete_mobs_bt
            ], margin='0px auto', style={'overflow': 'hidden', 'width': '100%', 'display': 'flex'})
        ], header='Mobs')
        mainWrapperContainer.append([mobsCard])
        # </------------------ [MOBS BLOCK] ------------------>

        # <------------------ [OPTIONS BLOCK] ------------------>
        visionOptionsContainer = gui.Container(style={'display': 'flex'})
        self.show_bots_vision_bt = gui.Button("Show bot's vision", margin='10px', _class='Button main-button')
        self.show_bots_vision_bt.onclick.do(self.open_show_bots_vision_dialog)
        visionOptionsContainer.append([
            self.show_bots_vision_bt,
        ])
        
        thresholdContainer = gui.Container([
            gui.Label('Threshold options', width=200, margin='10px', style={'font-weight': 'bold'}),
            gui.Container([
                LabeledSlider(
                    label="Mob position match threshold",
                    value=self.config['mob_position_match_threshold'],
                    on_change=lambda w, v: self.set_config(mob_position_match_threshold=float(v))
                ),
                 LabeledSlider(
                    label="Mob still alive match threshold",
                    value=self.config['mob_still_alive_match_threshold'],
                    on_change=lambda w, v: self.set_config(mob_still_alive_match_threshold=float(v))
                ),
                LabeledSlider(
                    label="Mob existence match threshold",
                    value=self.config['mob_existence_match_threshold'],
                    on_change=lambda w, v: self.set_config(mob_existence_match_threshold=float(v))
                ),
                LabeledSlider(
                    label="Inventory perin converter match threshold",
                    value=self.config['inventory_perin_match_threshold'],
                    on_change=lambda w, v: self.set_config(inventory_perin_match_threshold=float(v))
                ),
                LabeledSlider(
                    label="Inventory icons match threshold",
                    value=self.config['inventory_icons_match_threshold'],
                    on_change=lambda w, v: self.set_config(inventory_icons_match_threshold=float(v))
                )
            ], style={'display': 'flex', 'flex-wrap': 'wrap'})
        ], style={'border-top': '1px solid #d7d7d7', 'border-bottom': '1px solid #d7d7d7', 'margin': '10px 0px', 'padding': '10px 0px'})

        combatSettingsContainer = gui.Container(margin='0px auto', style={'padding': '10px', 'display': 'flex', 'flex-wrap': 'wrap'})
        combatSettings_mobs_kill_goal_label = gui.Label('Mobs kill goal', width=100, style={'height': 'auto', 'margin-left': '10px', 'margin-top': '10px'})
        combatSettings_mobs_kill_goal_input = gui.TextInput(width=100, height='100%', style={'padding': '5px'})
        combatSettings_mobs_kill_goal_input.set_value(str(self.config.get('mobs_kill_goal', '')))
        def kill_goal_onchange(w, v):
            value = v
            try:
                value = int(v)
                if value == 0:
                    value = None
            except Exception:
                value = None
            self.set_config(mobs_kill_goal=value)
            w.set_value(str(self.config.get('mobs_kill_goal', '')))
        combatSettings_mobs_kill_goal_input.onchange.do(kill_goal_onchange)

        combatSettings_fight_time_label = gui.Label('Fight time limit (s)', width=100, style={'height': 'auto', 'margin-left': '10px', 'margin-top': '10px'})
        combatSettings_fight_time_input = gui.TextInput(width=100, height='100%', style={'padding': '5px'})
        combatSettings_fight_time_input.set_value(str(self.config.get('fight_time_limit_sec', '')))
        def fight_time_onchange(w, v):
            value = v
            try:
                value = int(v)
            except Exception:
                w.set_value(str(self.config.get('fight_time_limit_sec', '')))
                return
            self.set_config(fight_time_limit_sec=value)
            w.set_value(str(self.config.get('fight_time_limit_sec', '')))
        combatSettings_fight_time_input.onchange.do(fight_time_onchange)

        combatSettings_alive_check_delay_label = gui.Label('Delay to check if mob is still alive (s)', width=100, style={'height': 'auto', 'margin-left': '10px', 'margin-top': '10px'})
        combatSettings_alive_check_delay_input = gui.TextInput(width=100, height='100%', style={'padding': '5px'})
        combatSettings_alive_check_delay_input.set_value(str(self.config.get('delay_to_check_mob_still_alive_sec', '')))
        def alive_check_onchange(w, v):
            value = v
            try:
                value = float(v)
            except Exception:
                w.set_value(str(self.config.get('delay_to_check_mob_still_alive_sec', '')))
                return
            self.set_config(delay_to_check_mob_still_alive_sec=value)
            w.set_value(str(self.config.get('delay_to_check_mob_still_alive_sec', '')))
        combatSettings_alive_check_delay_input.onchange.do(alive_check_onchange)

        # combatSettings_penya_convert_timer_label = gui.Label('Timer to convert penya to perins (m)', width=100, style={'height': 'auto', 'margin-left': '10px', 'margin-top': '10px'})
        # combatSettings_penya_convert_timer_input = gui.TextInput(width=100, height='100%', style={'padding': '5px'})
        # combatSettings_penya_convert_timer_input.set_value(str(self.config.get('convert_penya_to_perins_timer_min', '')))
        # def penya_convert_timer_onchange(w, v):
        #     value = v
        #     try:
        #         value = int(v)
        #     except Exception:
        #         w.set_value(str(self.config.get('convert_penya_to_perins_timer_min', '')))
        #         return
        #     self.set_config(convert_penya_to_perins_timer_min=value)
        #     w.set_value(str(self.config.get('convert_penya_to_perins_timer_min', '')))
        # combatSettings_penya_convert_timer_input.onchange.do(penya_convert_timer_onchange)

        combatSettingsContainer.append([
            combatSettings_mobs_kill_goal_label,
            combatSettings_mobs_kill_goal_input,
            combatSettings_fight_time_label,
            combatSettings_fight_time_input,
            combatSettings_alive_check_delay_label,
            combatSettings_alive_check_delay_input,
            # combatSettings_penya_convert_timer_label,
            # combatSettings_penya_convert_timer_input
        ])

        combatSettingsBlock = gui.Container([
            gui.Label('Fight options', width=200, margin='10px', style={'font-weight': 'bold'}),
            combatSettingsContainer
        ])

        optionsCard = SectionCard([
            gui.Container([
                visionOptionsContainer,
                thresholdContainer,
                combatSettingsBlock
            ], margin='0px auto', style={'overflow': 'hidden', 'width': '100%', 'display': 'block'})
        ], header='Options')
        mainWrapperContainer.append([optionsCard])
        # </------------------ [OPTIONS BLOCK] ------------------>

        # <------------------ [STATUS BLOCK] ------------------>
        self.txt = gui.TextInput(single_line=False, height=150, margin='10px', style={'width': '90%', 'padding': '5px'})
        self.txt.set_text('UI started')
        self.txt.attributes['readonly'] = '1'

        statusCard = SectionCard([
            gui.Container([
                self.txt
            ], margin='0px auto', style={'overflow': 'hidden', 'width': '100%', 'display': 'block'})
        ], header='Status')
        mainWrapperContainer.append([statusCard])
        # </------------------ [STATUS BLOCK] ------------------>

        return mainWrapperContainer
    
    def exit(self, widget):
        self.close()

    def on_close(self):
        """ Overloading App.on_close event to stop the Timer.
        """
        self.stop_flag = True
        super(RemiApp, self).on_close()

    def open_attach_window_popup(self, widget):
        # Create a dialog window
        dialog = gui.GenericDialog(title='Attach window', width='300px', height='200px')
        
        # Add input fields to the dialog
        handlers = get_window_handlers()
        dropdown = gui.DropDown.new_from_list(list(handlers.keys()), width=200, height=20, margin='10px')
        if self.attached_window:
            dropdown.select_by_value(self.attached_window)
        dialog.add_field('select', dropdown)

        # Add confirm button
        # dialog.set_on_confirm_dialog_listener(self.on_attach_window_dialog_confirm)
        # dialog.confirm_dialog.onclick.do(self.on_dialog_confirm)
        dialog.confirm_dialog.do(self.on_attach_window_dialog_confirm)
        
        # Show the dialog
        dialog.show(self)

    def on_attach_window_dialog_confirm(self, dialog):
        # Get the dialog reference
        # Access input values
        select_value = dialog.get_field('select').get_value()

        self.attached_window = select_value
        self.actionsContainer_current_attached_label.set_text(str(select_value))

        handlers = get_window_handlers()
        game_window_name, game_window_handler = select_value, handlers[select_value]
        self.bot.setup(game_window_handler, self)
        
        # unlock start button
        self.start_stop_bt.remove_class('disabled-button')
        # Close the dialog
        dialog.hide()

    def open_select_mobs_dialog(self, widget, is_delete_form=False):
        dialog = gui.GenericDialog(title='Select mobs' if not is_delete_form else 'Delete mobs', width='400px')

        mobNameInput = gui.TextInput(width=200, height=30)
        dialog.add_field_with_label('mobNameInput', 'Find', mobNameInput)
        
        all_mobs = self.bot.get_all_mobs()
        selected_mobs_names = [mob["name"] for mob in self.bot.config["selected_mobs"] if mob["name"] in all_mobs]
        all_mobs_titles = [f"{name} - {params['element']} - {params['map_name']}" for (name, params) in dict.items(all_mobs)]
        selected_mobs_titles = [
            f"{name} - {params['element']} - {params['map_name']}" for (name, params) in dict.items(all_mobs)
            if name in selected_mobs_names
        ]

        # value должно быть >>> selected_names:  ['kingyo', 'castor', 'worun']
        listMultiView = ListMultiselectView.new_from_list(all_mobs_titles, height=250, margin='10px', style={'width': '100%', 'padding': '0'})
        if not is_delete_form:
            listMultiView.set_value(selected_mobs_titles)

        def mobNameInput_onchange(w, val, keycode):
            listMultiView.set_filter(val)
        mobNameInput.onkeyup.do(mobNameInput_onchange)

        dialog.add_field('mobListMulti', listMultiView)

        def submit(dialog):
            selected_mobs_indexes = [all_mobs_titles.index(mob) for mob in listMultiView.get_value()]
            all_names = list(dict.keys(all_mobs))
            selected_names = [all_names[i] for i in selected_mobs_indexes]

            if not is_delete_form:
                self.set_config(selected_mobs=selected_names)
            else:
                from assets.Assets import MobInfo
                MobInfo.delete_mobs
                self.set_config(selected_mobs=[name for name in self.config['selected_mobs'] if name not in selected_names])
                MobInfo.delete_mobs(selected_names)

        dialog.confirm_dialog.do(submit)
        dialog.show(self)

    def open_delete_mob_dialog(self, widget):
        self.open_select_mobs_dialog(widget, is_delete_form=True)

    def open_add_mob_dialog(self, widget):
        dialog = gui.GenericDialog(title='Add mob', width='350px')

        mobNameInput = gui.TextInput(width=200, height=30)
        dialog.add_field_with_label('mobNameInput', 'Mob name', mobNameInput)

        locNameInput = gui.TextInput(width=200, height=30)
        dialog.add_field_with_label('locNameInput', 'Location name', locNameInput)
        
        BASE_DIR = Path(__file__).parent
        folder_path = BASE_DIR / "assets" / "_temp"
        folder_path.mkdir(parents=True, exist_ok=True)

        fileInput = gui.FileUploader(folder_path, width=200, height=30, margin='10px')
        fileInput.filename = None
        def save_raw_file(widget, filename):
            widget.filename = filename
        fileInput.onsuccess.do(save_raw_file)
        dialog.add_field_with_label('fileInput', 'file', fileInput)

        heightOffsetInput = gui.TextInput(width=200, height=30)
        dialog.add_field_with_label('heightOffsetInput', 'Height offset', heightOffsetInput)

        elementDropdownInput = gui.DropDown.new_from_list(['electricity', 'wind', 'fire', 'water', 'soil', 'lvl'], width=200, height=20, margin='10px')
        dialog.add_field_with_label('elementDropdownInput', 'Element', elementDropdownInput)

        dialog.confirm_dialog.do(self.on_add_mob_dialog_confirm)
        dialog.show(self)

    def on_add_mob_dialog_confirm(self, dialog):
        BASE_DIR = Path(__file__).parent
        img_temp_folder_path = BASE_DIR / "assets" / "_temp"

        values = {
            'name': dialog.get_field('mobNameInput').get_value(),
            'map': dialog.get_field('locNameInput').get_value(),
            'image': img_temp_folder_path / dialog.get_field('fileInput').filename,
            'height': dialog.get_field('heightOffsetInput').get_value(),
            'element': dialog.get_field('elementDropdownInput').get_value(),
        }

        from assets.Assets import MobInfo
        MobInfo.add_new_mob(
            name=values["name"], map_name=values["map"], image_path=values["image"],
            height_offset=int(values["height"]), element=values["element"]
        )

        # clear temp folder
        temp_folder_path = Path(__file__).parent / "assets" / "_temp"
        if temp_folder_path.exists():
            shutil.rmtree(temp_folder_path)

        dialog.hide()

    def open_show_bots_vision_dialog(self, widget):
        dialog = gui.GenericDialog(title="Bot's vision", width='auto', height='auto')
        dialog.set_style({'margin': '20px'})

        fps_container = gui.Container(style={'display': 'flex'})
        fps_label = gui.Label('FPS:', margin='10px')
        self.fps_counter = gui.Label('-', width=200, margin='10px')
        fps_container.append([
            fps_label,
            self.fps_counter
        ])
        dialog.add_field('fps', fps_container)

        options_container_vision_params = gui.Container(style={'display': 'flex'})

        options_container_show_matches_text_checkbox = gui.CheckBoxLabel('Show matches text', self.config.get('show_matches_text'), height=30, margin='10px', style={'justify-content': 'flex-start'})
        options_container_show_matches_text_checkbox.onchange.do(lambda w, v: self.set_config(show_matches_text=v))

        options_container_show_mobs_boxes_checkbox = gui.CheckBoxLabel('Show mobs boxes', self.config.get('show_mobs_boxes'), height=30, margin='10px', style={'justify-content': 'flex-start'})
        options_container_show_mobs_boxes_checkbox.onchange.do(lambda w, v: self.set_config(show_mobs_boxes=v))

        options_container_show_mobs_markers_checkbox = gui.CheckBoxLabel('Show mobs markers', self.config.get('show_mobs_markers'), height=30, margin='10px', style={'justify-content': 'flex-start'})
        options_container_show_mobs_markers_checkbox.onchange.do(lambda w, v: self.set_config(show_mobs_markers=v))
        
        options_container_vision_params.append([
            options_container_show_matches_text_checkbox,
            options_container_show_mobs_boxes_checkbox,
            options_container_show_mobs_markers_checkbox
        ])

        dialog.add_field('vision_controls', options_container_vision_params)

        self.img = gui.Image('', style={'border': '2px dotted grey', 'width': '100%'})
        dialog.add_field('img', self.img)

        self.bot.set_config(show_frames=True)
        dialog.confirm_dialog.do(lambda w: self.bot.set_config(show_frames=False))
        dialog.cancel_dialog.do(lambda w: self.bot.set_config(show_frames=False))

        dialog.show(self)

    def render_image(self, source_img: numpy.ndarray):
        try:
            w, h = (1024, 768)
            img = cv.resize(source_img, (w, h))
            # imgbytes = cv.imencode(".png", img)[1].tobytes()
            png_params = [cv.IMWRITE_JPEG_QUALITY, 50]

            encoded_img = cv.imencode(".jpg", img, png_params)[1]
            img_bytes = encoded_img.tobytes()
            base64_encoded = base64.b64encode(img_bytes).decode('utf-8')
            img_src = f"data:image/jpg;base64,{base64_encoded}"
            self.img.set_image(img_src)
        except Exception as e:
            print('> render_image exception: ', e)

    def set_fps_value(self, value: int):
        self.fps_counter.set_text(str(value))

    def append_status_log(self, msg):
        current_value = self.txt.get_value()
        current_value += f'\n{msg}'
        self.txt.set_value(current_value)

    def start_bot(self):
        self.bot.start()
        self.start_stop_bt.set_text('Stop (alt+s)')

    def stop_bot(self):
        self.bot.stop()
        self.start_stop_bt.set_text('Start')

    def toggle_bot_state(self, widget):
        if not self.attached_window:
            return

        if not self.bot.is_running:
            self.start_bot()
        else:
            self.stop_bot()
