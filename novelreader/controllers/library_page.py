from kivy.app import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from pathlib import Path
from novelreader.helpers import plog
from novelreader.models import Database


Builder.load_file(str(Path('novelreader/views/library_page.kv').absolute()))

class LibraryPage(Screen):
    novellist = ObjectProperty(None)
    bottom_controls = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LibraryPage, self).__init__(**kwargs)
        # self.__selected_novel = None
    
    def on_start(self, db):
        plog(["on start"], "library_page")
        self.db = db

        # load saved novels in database
        novels = Database.select_novels(db.conn)
        if len(novels) > 0:
            for novel in novels:
                self.novellist.data.append({
                    "url": novel["url"],
                    "title": novel["title"],
                    "thumbnail": novel["thumbnail"]
                })
            plog(["loaded"], 'novels')

    def get_selected_novel(self):
        return self.selected_novel
    
    def goto_info_page(self, novel):
        print(dir(self.manager.get_screen('info_page')))
        self.manager.get_screen('info_page').update_content(novel["url"])
        self.manager.current = 'info_page'

# recyclerview
class NovelList(RecycleView):
    novellist = ObjectProperty(None)

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                     RecycleGridLayout):
        ''' Adds selection and focus behaviour to the view. '''

class NovelItem(RecycleDataViewBehavior, GridLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    title = StringProperty('')
    thumbnail = StringProperty('')

    def __init__(self, **kwargs):
        super(NovelItem, self).__init__(**kwargs)

    ''' Add selection support to the Label '''
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(NovelItem, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(NovelItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.parent.parent.goto_info_page(rv.data[index])

class BottomControlBar(BoxLayout):
    library_btn = ObjectProperty(None)
    search_btn = ObjectProperty(None)
    downloads_btn = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(BottomControlBar, self).__init__(**kwargs)
    
    def print_text(self):
        print(self.library_btn.text)


