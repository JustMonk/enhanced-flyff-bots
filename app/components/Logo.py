from remi.gui import Container, Label

class Logo(Container):
    def __init__(self, *args, **kwargs):
        """
        Args:
            kwargs: See Container.__init__()
        """
        super().__init__(*args, **kwargs)

        self.set_layout_orientation(kwargs.get('layout_orientation', Container.LAYOUT_VERTICAL))

        self.logo_wrapper = Container(
            style={'margin-bottom': '10px', 'position': 'relative'}, 
            # _class='logoWrapper'
        )
        
        self.logo_text = Label('FlyFF bot', style={'margin': '0', 'text-align': 'center'}, _class='Label LogoText')
        self.logo_text.type = 'h1'

        self.logo_label = Label('enhanced', style={'position': 'absolute', 'top': '1%', 'left': '20%', 'transform': 'rotate(-21deg)', 'background': '#ff5f5f', 'color': 'white', 'padding': '2px 10px', 'border-radius': '3px', 'font-weight': 'bold', 'box-shadow': '1px 2px 1px 1px #a50000'})

        self.logo_wrapper.append([
            self.logo_text,
            self.logo_label
        ])

        self.append([self.logo_wrapper])
