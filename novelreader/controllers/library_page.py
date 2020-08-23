from . import Builder, Screen
from . import ObjectProperty, StringProperty
from . import GridLayout, BoxLayout, RecycleView

Builder.load_file('../views/library_page.kv')

# todo library page
class LibraryPage(Screen):
    novellist = ObjectProperty(None)
    bottom_controls = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LibraryPage, self).__init__(**kwargs)

# recyclerview
class NovelList(RecycleView):
    novellist = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(NovelList, self).__init__(**kwargs)
        self.data = [{} for i in range(12)]

# todo recyclerview behavior
# todo NovelItem
class NovelItem(GridLayout):
    novel = ObjectProperty({
        'thumbnail': '../public/imgs/cultivation-chat-group.jpg',
        'title': 'Cultivation Chat Group'
        })

    def __init__(self, **kwargs):
        super(NovelItem, self).__init__(**kwargs)


class BottomControlBar(BoxLayout):
    library_btn = ObjectProperty(None)
    search_btn = ObjectProperty(None)
    downloads_btn = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(BottomControlBar, self).__init__(**kwargs)
    
    def print_text(self):
        print(self.library_btn.text)


