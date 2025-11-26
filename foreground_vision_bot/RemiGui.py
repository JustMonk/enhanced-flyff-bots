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

import remi.gui as gui
from remi import start, App
from threading import Timer
import webview
from utils.helpers import get_window_handlers
import numpy
import cv2 as cv
import base64

class MyApp(App):
    def __init__(self, *args, **kwargs):
        super(MyApp, self).__init__(*args)
        self.config = {
            # app config
            'attached_window': None
        }

    def idle(self):
        #self.counter.set_text('Running Time: ' + str(self.count))
        # self.progress.set_value(self.count%100)
        pass

    def main(self, bot):
        # userdata это данные, которые сервер передает приложению
        print('userdata arg:', bot)
        self.bot = bot

        # attach window
        # self.new_page_container = gui.VBox(width=300, height=200)
        # self.new_page_container.style['justify-content'] = 'center'
        # self.new_page_container.style['align-items'] = 'center'
        # new_lbl = gui.Label("This is the New Page!")
        # self.new_page_container.append(new_lbl)
        # self.add_url("/attach_window", self.new_page_container)
        self.new_window = None

        # the margin 0px auto centers the main container
        mainWrapperContainer = gui.Container(width=540, margin='0px auto', style={'display': 'block', 'overflow': 'hidden', 'padding': '20px'})
        self.mainWrapperContainer = mainWrapperContainer

        # <------------------ [ACTIONS BLOCK] ------------------>
        actionsContainer = gui.Container(margin='0px auto', style={'display': 'block', 'overflow': 'hidden', 'box-shadow': '0px 0px 9px 1px #00000040', 'width': '100%', 'box-shadow': '0px 0px 9px 1px #00000040'})

        actionsButtonContainer = gui.Container(margin='0px auto', style={'display': 'block', 'overflow': 'hidden', 'width': '100%', 'display': 'flex'})
        self.label = gui.Label('Actions', width=200, height=30, margin='10px')
        self.actionsContainer_attach_bt = gui.Button('Attach window', width=200, height=30, margin='10px')
        self.actionsContainer_attach_bt.onclick.do(self.open_attach_window_popup)
        self.actionsContainer_start_bt = gui.Button('Start', width=200, height=30, margin='10px')
        self.actionsContainer_stop_bt = gui.Button('Stop (alt+s)', width=200, height=30, margin='10px')
        self.actionsContainer_exit_bt = gui.Button('Exit', width=200, height=30, margin='10px')
        self.actionsContainer_exit_bt.onclick.do(self.exit)
        actionsButtonContainer.append([
            self.label,
            self.actionsContainer_attach_bt,
            self.actionsContainer_start_bt,
            self.actionsContainer_stop_bt,
            self.actionsContainer_exit_bt
        ])

        actionsContainer.append([actionsButtonContainer])


        self.actionsContainer_current_attached_label = gui.Label('',  style={'display': 'inline-block', 'width': '90%', 'height': '12px', 'padding': '5px', 'overflow': 'hidden', 'color': '#993f3f'})
        actionsContainer.append([self.actionsContainer_current_attached_label])

        mainWrapperContainer.append([actionsContainer])
        # </------------------ [ACTIONS BLOCK] ------------------>

        # <------------------ [MOBS BLOCK] ------------------>
        mobsContainer = gui.Container(margin='0px auto', style={'display': 'block', 'overflow': 'hidden', 'box-shadow': '0px 0px 9px 1px #00000040', 'width': '100%', 'box-shadow': '0px 0px 9px 1px #00000040', 'margin-top': '20px'})
        mobsButtonContainer = gui.Container(margin='0px auto', style={'display': 'block', 'overflow': 'hidden', 'width': '100%', 'display': 'flex'})
        mobsLabel = gui.Label('Mobs', width=200, height=30, margin='10px')

        self.mobsContainer_select_mobs_bt = gui.Button('Select mobs', width=200, height=30, margin='10px')
        self.mobsContainer_select_mobs_bt.onclick.do(self.open_select_mobs_dialog)
        self.mobsContainer_add_mob_bt = gui.Button('Add mob', width=200, height=30, margin='10px')
        self.mobsContainer_add_mob_bt.onclick.do(self.open_add_mob_dialog)
        self.mobsContainer_delete_mobs_bt = gui.Button('Delete mobs', width=200, height=30, margin='10px')
        self.mobsContainer_delete_mobs_bt.onclick.do(self.open_delete_mob_dialog)
        mobsButtonContainer.append([
            mobsLabel,
            self.mobsContainer_select_mobs_bt,
            self.mobsContainer_add_mob_bt,
            self.mobsContainer_delete_mobs_bt
        ])
        mobsContainer.append([mobsButtonContainer])


        mainWrapperContainer.append([mobsContainer])
        # </------------------ [MOBS BLOCK] ------------------>

        # <------------------ [OPTIONS BLOCK] ------------------>
        optionsContainer = gui.Container(margin='0px auto', style={'display': 'block', 'overflow': 'hidden', 'box-shadow': '0px 0px 9px 1px #00000040', 'width': '100%', 'box-shadow': '0px 0px 9px 1px #00000040', 'margin-top': '20px'})
        optionsContainerLabel = gui.Label('Options', width=200, height=30, margin='10px')

        checkOptionsContainer = gui.Container()
        self.options_container_show_bot_vision_checkbox = gui.CheckBoxLabel('Show bot\'s vision', True, width=200, height=30, margin='10px', style={'justify-content': 'flex-start'})
        self.options_container_show_matches_text_checkbox = gui.CheckBoxLabel('Show matches text', True, width=200, height=30, margin='10px', style={'justify-content': 'flex-start'})
        self.options_container_show_mobs_boxes_checkbox = gui.CheckBoxLabel('Show mobs boxes', True, width=200, height=30, margin='10px', style={'justify-content': 'flex-start'})
        self.options_container_show_mobs_markers_checkbox = gui.CheckBoxLabel('Show mobs markers', True, width=200, height=30, margin='10px', style={'justify-content': 'flex-start'})
        checkOptionsContainer.append([
            self.options_container_show_bot_vision_checkbox,
            self.options_container_show_matches_text_checkbox,
            self.options_container_show_mobs_boxes_checkbox,
            self.options_container_show_mobs_markers_checkbox
        ])
        
        thresholdContainer = gui.Container(style={'border': '1px solid grey'})
        thresholdContainerLabel = gui.Label('threshold option', width=200, height=30, margin='10px')
        threshold_mob_position_label = gui.Label('Mob potision match threshold', width=200, style={'height': 'auto', 'margin-left': '10px', 'margin-top': '10px'})
        threshold_mob_position_slider = gui.Slider(10, 0, 100, 5, width=200, height=20, margin='10px')
        
        threshold_mob_still_alive_label = gui.Label('Mob still alive threshold', width=200, style={'height': 'auto', 'margin-left': '10px', 'margin-top': '10px'})
        threshold_mob_still_alive_slider = gui.Slider(10, 0, 100, 5, width=200, height=20, margin='10px')

        threshold_mob_existence_label = gui.Label('Mob existence match threshold', width=200, style={'height': 'auto', 'margin-left': '10px', 'margin-top': '10px'})
        threshold_mob_existence_slider = gui.Slider(10, 0, 100, 5, width=200, height=20, margin='10px')

        threshold_inventory_perin_label = gui.Label('Inventory perin converter match threshold', width=200, style={'height': 'auto', 'margin-left': '10px', 'margin-top': '10px'})
        threshold_inventory_perin_slider = gui.Slider(10, 0, 100, 5, width=200, height=20, margin='10px')

        threshold_inventory_icons_label = gui.Label('Inventory icons match threshold', width=200, style={'height': 'auto', 'margin-left': '10px', 'margin-top': '10px'})
        threshold_inventory_icons_slider = gui.Slider(10, 0, 100, 5, width=200, height=20, margin='10px')

        thresholdContainer.append([
            thresholdContainerLabel,
            threshold_mob_position_label,
            threshold_mob_position_slider,
            threshold_mob_still_alive_label,
            threshold_mob_still_alive_slider,
            threshold_mob_existence_label,
            threshold_mob_existence_slider,
            threshold_inventory_perin_label,
            threshold_inventory_perin_slider,
            threshold_inventory_icons_label,
            threshold_inventory_icons_slider
        ])

        optionsContainer.append([
            optionsContainerLabel,
            checkOptionsContainer,
            thresholdContainer
        ])

        mainWrapperContainer.append([optionsContainer])
        # </------------------ [OPTIONS BLOCK] ------------------>

        # <------------------ [STATUS BLOCK] ------------------>
        statusContainer = gui.Container(margin='0px auto', style={'display': 'block', 'overflow': 'hidden', 'box-shadow': '0px 0px 9px 1px #00000040', 'width': '100%', 'box-shadow': '0px 0px 9px 1px #00000040', 'margin-top': '20px'})
        statusContainerLabel = gui.Label('Status', width=200, height=30, margin='10px')

        self.txt = gui.TextInput(single_line=False, height=150, margin='10px', style={'width': '90%'})
        self.txt.set_text('This is a TEXTAREA')
        
        fps_container = gui.Container(margin='0px auto', style={'display': 'flex'})
        fps_label = gui.Label('Fps:', height=30, margin='10px')
        self.fps_counter = gui.Label('-', width=200, height=30, margin='10px')
        fps_container.append([
            fps_label,
            self.fps_counter
        ])

        self.img = gui.Image('/res:logo.png', margin='10px', style={'border': '2px dotted grey'})

        statusContainer.append([
            statusContainerLabel,
            self.txt,
            fps_container,
            self.img
        ])


        mainWrapperContainer.append([statusContainer])
        # </------------------ [STATUS BLOCK] ------------------>

        
        return mainWrapperContainer
    
    def exit(self, widget):
        self.close()

    def on_close(self):
        """ Overloading App.on_close event to stop the Timer.
        """
        self.stop_flag = True
        super(MyApp, self).on_close()

    def open_attach_window_popup(self, widget):
        # Create a dialog window
        dialog = gui.GenericDialog(title='Attach window', width='300px', height='200px')
        
        # Add input fields to the dialog
        handlers = get_window_handlers()
        dropdown = gui.DropDown.new_from_list(list(handlers.keys()), width=200, height=20, margin='10px')
        if self.config.get('attached_window'):
            dropdown.select_by_value(self.config['attached_window'])
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

        self.config['attached_window'] = select_value
        self.actionsContainer_current_attached_label.set_text(select_value)

        # game_window_name, game_window_handler = self.__attach_window_popup()
        handlers = get_window_handlers()
        game_window_name, game_window_handler = select_value, handlers[select_value]
        # print('>>> ', game_window_name, game_window_handler)
        # game_window_handler, self
        self.bot.config['show_frames'] = True
        self.bot.setup(game_window_handler, self)

        # Close the dialog
        dialog.hide()

    def open_select_mobs_dialog(self, widget):
        dialog = gui.GenericDialog(title='Select mobs', width='300px', height='200px')

        dialog.show(self)

    def open_add_mob_dialog(self, widget):
        dialog = gui.GenericDialog(title='Add mob', width='350px', height='450px')

        mobNameInput = gui.TextInput(width=200, height=30)
        dialog.add_field_with_label('mobNameInput', 'Mob name', mobNameInput)

        locNameInput = gui.TextInput(width=200, height=30)
        dialog.add_field_with_label('locNameInput', 'Location name', locNameInput)
        
        # создавать папку /assets/_temp/ если она не создана
        fileInput = gui.FileUploader('./assets/_temp/', width=200, height=30, margin='10px')
        fileInput.filename = None
        def save_raw_file(widget, filename):
            widget.filename = filename
        fileInput.onsuccess.do(save_raw_file)
        dialog.add_field_with_label('fileInput', 'file', fileInput)

        heightOffsetInput = gui.TextInput(width=200, height=30)
        dialog.add_field_with_label('heightOffsetInput', 'Height offset', heightOffsetInput)

        elementDropdownInput = gui.DropDown.new_from_list(['electricity', 'wind', 'fire', 'water', 'soil'], width=200, height=20, margin='10px')
        dialog.add_field_with_label('elementDropdownInput', 'Element', elementDropdownInput)

        dialog.confirm_dialog.do(self.on_add_mob_dialog_confirm)
        dialog.show(self)

    def on_add_mob_dialog_confirm(self, dialog):
        values = {
            'name': dialog.get_field('mobNameInput').get_value(),
            'map': dialog.get_field('locNameInput').get_value(),
            'image': './assets/_temp/' + dialog.get_field('fileInput').filename,
            'height': dialog.get_field('heightOffsetInput').get_value(),
            'element': dialog.get_field('elementDropdownInput').get_value(),
        }

        from assets.Assets import MobInfo
        MobInfo.add_new_mob(
            name=values["name"], map_name=values["map"], image_path=values["image"],
            height_offset=int(values["height"]), element=values["element"]
        )

        dialog.hide()

    def open_delete_mob_dialog(self, widget):
        dialog = gui.GenericDialog(title='Delete mobs', width='300px', height='200px')

        dialog.show(self)


    def loop(self):
        # start(self, debug=True, standalone=True)
        start(self, debug=True, address='0.0.0.0', port=8081, start_browser=True, multiple_instance=True)

    def render_image(self, source_img: numpy.ndarray):
        # print('got image: ', type(img), img)
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
            # print('> b64 encoded image: ', base64_encoded)
        except Exception as e:
            print('> render_image exception: ', e)

    def set_fps_value(self, value: int):
        self.fps_counter.set_text(str(value))

if __name__ == "__main__":
    # starts the webserver
    # optional parameters
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    # start(MyApp, debug=True, address='0.0.0.0', port=8081, start_browser=True, multiple_instance=True)
    start(MyApp, debug=True, standalone=True)