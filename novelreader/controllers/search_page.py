from kivy.app import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from novelreader.models import Website, Novel
from novelreader.helpers import plog
from pathlib import Path
from functools import partial
import requests
import threading

Builder.load_file(str(Path("novelreader/views/search_page.kv").absolute()))

class SearchPage(Screen):
    search_list_recycle = ObjectProperty()
    search_input = ObjectProperty()

    def __init__(self, **kwargs):
        super(SearchPage, self).__init__(**kwargs)
        self.__searching = False
    
    def on_start(self, repository):
        self.repo = repository

    def goto_info_page(self, url):
        # get novel data from web
        novel = self.repo.get_novel(url)
        chapters = self.repo.get_chapters(url)
        meta = self.repo.get_meta(url)

        # open info page then send novel data
        self.manager.get_screen("info_page").open(Novel(
            url=novel.url,
            title=novel.title,
            thumbnail=novel.thumbnail,
            meta=meta,
            chapters=chapters
        ))
        self.manager.current = "info_page"

    def update_search_list(self, novels: {}):
        self.search_list_recycle.data = []
        novel_data = []
        for novel in novels:
            novel_data.append({"text": novel.title, "url": novel.url})
        if novel_data:
            self.search_list_recycle.data = novel_data
    
    def start_search(self):
        if not self.__searching:
            self.__searching = True
            plog(['searching'], self.search_input.text)
            self.search_list_recycle.data.clear()

            with requests.Session() as session:
                thread = threading.Thread(target=self.search_work, args=(self.search_input.text, Website.BOXNOVELCOM))
                thread.start()
        else:
            plog(["already searching"], self.search_input.text)
        self.search_input.text = ""

    def search_work(self, keyword: str, website: Website):
        novels = self.repo.search(keyword, website)
        if novels:
            plog(["# Of Searched"], len(novels))
            self.update_search_list(novels)
        self.__searching = False
        
class SearchItem(Button):
    url = StringProperty()

    def browse(self):
        plog(['browsing'], self.text)
        self.parent.parent.parent.parent.goto_info_page(self.url)
        # Clock.schedule_once(partial(), 0)




