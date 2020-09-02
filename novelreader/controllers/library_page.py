from kivy.app import Builder
from kivy.clock import Clock
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
from wescrape.models.novel import Novel
from novelreader.repository import Repository
from novelreader.services import download_thumbnail
from novelreader.models import Database
from novelreader.helpers import plog, thumbnail_path
import requests
import threading


Builder.load_file(str(Path('novelreader/views/library_page.kv').absolute()))

class LibraryPage(Screen):
    novellist = ObjectProperty(None)
    bottom_controls = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LibraryPage, self).__init__(**kwargs)
        # self.__selected_novel = None
    
    def on_start(self, repository: Repository):
        plog(["on start"], "library_page")
        self.repo = repository
        Clock.schedule_interval(lambda dt: self.update_library(), 1*60)

        # load saved novels in database
        novels = self.repo.get_novels()
        if novels:
            for novel in novels:
                threading.Thread(target=self.download_thumbnail, args=(novel.thumbnail,)).start()
            self.update_library()

    def goto_info_page(self, novel):
        novel = self.repo.get_novel(url, offline=True)
        self.manager.get_screen('info_page').open(novel)
        self.manager.current = 'info_page'

    def download_thumbnail(self, url):
        with requests.Session() as session:
            download_thumbnail(session, url)
        
    def update_library(self):
        """Update Novels Library From `novels`"""
        self.novellist.data = []
        novels = self.repo.get_novels()
        for novel in novels:
            self.novellist.data.append({
                "url": novel.url,
                "title": novel.title,
                "thumbnail": str(thumbnail_path(novel.thumbnail))
            })
        plog(["loaded", str(len(novels))], 'novels')
        
    def get_selected_novel(self):
        return self.selected_novel

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


