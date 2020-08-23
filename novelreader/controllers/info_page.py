from . import Builder, Screen
from . import ObjectProperty, StringProperty
from . import GridLayout

Builder.load_file('../views/info_page.kv')

class InfoPage(Screen):
    """Page containing informations related to novel"""
    novel = ObjectProperty()
    # todo accept novel object from library page or search page
    def __init__(self, **kwargs):
        super(InfoPage, self).__init__(**kwargs)

class ChapterItem(GridLayout):
    """Chapter list item"""

class InfoItem(GridLayout):
    """Contain a name and value"""
    name = StringProperty()
    value = StringProperty()
