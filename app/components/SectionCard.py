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

        self.set_style({'padding': '20px', 'margin-bottom': '10px', 'display': 'block', 'overflow': 'hidden', 'box-shadow': '0px 3px 1px -2px rgba(0,0,0,0.2),0px 2px 2px 0px rgba(0,0,0,0.14),0px 1px 5px 0px rgba(0,0,0,0.12)', 'width': 'auto', 'border-radius': '4px'})

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
