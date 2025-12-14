from remi.gui import Container, Label

class SectionCard(Container):
    def __init__(self, children=None, *args, header='', **kwargs):
        """
        Args:
            kwargs: See Container.__init__()
        """
        # super().__init__(*args, **kwargs)
        super().__init__(**kwargs)

        self.set_layout_orientation(kwargs.get('layout_orientation', Container.LAYOUT_VERTICAL))

        self.set_style({'padding': '20px', 'margin-bottom': '10px', 'display': 'block', 'overflow': 'hidden', 'box-shadow': '0px 0px 9px 1px #00000040', 'width': 'auto', 'box-shadow': '0px 0px 9px 1px #00000040'})

        self.card_wrapper = Container(
            margin='0px auto',
            # style={}
        )

        self.header = Label(str(header), style={'margin': '0', 'margin-bottom': '10px', 'text-align': 'left', 'font-size': '30px'})
        self.header.type = 'h1'
        
        self.card_wrapper.append([
            self.header
        ])

        self.append([self.card_wrapper])

        if children:
            self.append(children)
