from . import Screen, Builder
from . import ObjectProperty, StringProperty
from . import Label, Button
from . import plog

Builder.load_file("../views/search_page.kv")

class SearchPage(Screen):
    search_list_recycle = ObjectProperty()
    search_keyword = StringProperty()

    def __init__(self, **kwargs):
        super(SearchPage, self).__init__(**kwargs)

    def search(self, keyword):
        plog(['searching'], keyword)

class SearchItem(Button):
    url = StringProperty()

    def browse(self, url):
        plog(['browsing'], self.text)




