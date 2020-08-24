from . import Builder, Screen
from . import ObjectProperty, StringProperty
from . import GridLayout
from . import Path

Builder.load_file(str(Path('novelreader/views/info_page.kv').absolute()))

class InfoPage(Screen):
    """Page containing informations related to novel"""
    novel = ObjectProperty({
        'title': '',
        'thumbnail': ''
    })
    
    def __init__(self, **kwargs):
        super(InfoPage, self).__init__(**kwargs)

class ChapterItem(GridLayout):
    """Chapter list item"""

class InfoItem(GridLayout):
    """Contain a name and value"""
    name = StringProperty()
    value = StringProperty()
