from remi.gui import Container, Label, Slider

class LabeledSlider(Container):
    def __init__(self, *args, value=None, on_change=None, label='', **kwargs):
        """
        Args:
            kwargs: See Container.__init__()
        """
        super().__init__(*args, **kwargs)

        self.set_layout_orientation(kwargs.get('layout_orientation', Container.LAYOUT_VERTICAL))
        
        self.input_value_text = Label(str(value), width=200, style={'height': 'auto', 'margin-left': '10px', 'margin-top': '10px', 'text-align': 'center'})
        # TODO: slider params надо принимать отдельным аргументом 
        self.slider = Slider(0.25, 0.10, 0.90, 0.05, width=200, height=20, margin='10px')
        self.slider.attr_value = value
        def slider_onchange(w, v):
            self.input_value_text.set_text(str(v))
            on_change(w, v)
        self.slider.onchange.do(slider_onchange)

        self.append([
            Label(label, width=200, style={'height': 'auto', 'margin-left': '10px', 'margin-top': '10px'}),
            self.input_value_text,
            self.slider
        ])
