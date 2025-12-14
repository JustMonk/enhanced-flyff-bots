import remi.gui as gui
from remi.gui import ListView, Container, ListItem, decorate_set_on_listener, decorate_event

class ListMultiselectView(Container):
    def __init__(self, *args, **kwargs):
        """
        Args:
            kwargs: See Container.__init__()
        """
        super().__init__(*args, **kwargs)
        self.type = 'ul'
        # NEW
        # TODO: добавить в конструктор коллбэк on_change(val: list[items]) и для set_value вызывать = on_change(...)
        self._value: set = set() # TODO: переименовать в selected_items
        self._selected_items: list = []
        self._selected_keys: set = set()

    @classmethod
    def new_from_list(cls, items, **kwargs):
        """Populates the ListView with a string list.

        Args:
            items (list): list of strings to fill the widget with.
        """
        obj = cls(**kwargs)
        for item in items:
            obj.append(ListItem(item))
        return obj
    
    def append(self, value, key=''):
        """Appends child items to the ListView. The items are accessible by list.children[key].

        Args:
            value (ListItem, or iterable of ListItems): The child to be appended. In case of a dictionary,
                each item's key is used as 'key' param for the single append.
            key (str): The unique string identifier for the child. Ignored in case of iterable 'value'
                param.
        """
        if isinstance(value, type('')) or isinstance(value, type(u'')):
            value = ListItem(value)

        keys = super().append(value, key=key)
        if type(value) in (list, tuple, dict):
            for k in keys:
                if self.EVENT_ONCLICK not in self.children[k].attributes:
                    self.children[k].onclick.connect(self.onselection)
                self.children[k].attributes['selected'] = False
        else:
            # if an event listener is already set for the added item, it will not generate a selection event
            if self.EVENT_ONCLICK not in value.attributes:
                value.onclick.connect(self.onselection)
            value.attributes['selected'] = False
        return keys
    
    def empty(self):
        """Removes all children from the list"""
        self._selected_items = []
        self._selected_keys = set()
        super().empty()

    @decorate_set_on_listener("(self,emitter,selectedKey)")
    @decorate_event
    def onselection(self, widget):
        """Called when a new item gets selected in the list."""
        for k in self.children:
            if self.children[k] == widget:  # widget is the selected ListItem
                item_value = widget.get_value()
                if widget.attributes['selected'] == False:
                    widget.attributes['selected'] = True
                    self._value.add(item_value)
                    self._selected_keys.add(k)
                    self._selected_items.append(widget)
                else:
                    widget.attributes['selected'] = False
                    self._value.remove(item_value)
                    self._selected_keys.remove(k)
                    self._selected_items = [item for item in self._selected_items if item != widget]
        return (self._selected_keys,)
    
    # alias for set_value
    def select_by_value(self, value: set):
        """Selects an item by the text content of the child.

        Args:
            value (set): Text content of the item that have to be selected.
        """
        self._value = value
        self._selected_keys = set()
        self._selected_items = []

        for k in self.children:
            item = self.children[k]
            item.attributes['selected'] = False
            if item.get_value() in self._value:
                item.attributes['selected'] = True
                self._selected_keys.add(k)
                self._selected_items.append(item)

    def get_items(self) -> list[ListItem]:
        # completed
        """
        Returns:
            list[ListItem]: The selected item or None
        """
        return self._selected_items
    
    def get_value(self) -> set:
        # completed // TODO: можно итерироваться по _selected_items и вернуть set из item.get_value()
        """
        Returns:
            set: The value of the selected items or empty set
        """
        return self._value

    def get_keys(self) -> set:
        # completed
        """
        Returns:
            set: Keys of the selected items or empty set if no item is selected.
        """
        return self._selected_keys
    
    def set_value(self, value: set | list):
        new_value = value
        if not isinstance(value, set):
            new_value = set(value)
        self.select_by_value(new_value)

    def set_filter(self, filter_value: str) -> None:
        # TODO: можно возвращать сколько записей нашлось (количество)
        if not filter_value:
            for k in self.children:
                self.children[k].css_display = 'block'
            return

        for k in self.children:
            item = self.children[k]
            item_value = item.get_value()

            if filter_value.lower() in item_value.lower():
                item.css_display = 'block'
            else:
                item.css_display = 'none'
            