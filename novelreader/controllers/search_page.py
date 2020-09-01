from kivy.app import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from wescrape.models.novel import Website
from wescrape.helpers import identify_parser, search
from wescrape.parsers.nparse import BoxNovelCom, WuxiaWorldCo
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

    def goto_info_page(self, url, _):        
        self.manager.get_screen("info_page").update_widgets(url)
        self.manager.current = "info_page"

    def fetch_novels(self, session, _):
        payload = {
            "action": "wp-manga-search-manga",
            "title": self.search_input.text
        }

        for i in range(3):
            try:
                resp = session.post("https://boxnovel.com/wp-admin/admin-ajax.php", data=payload)
                self.update_search_list(resp.json()["data"])
                break
            except requests.exceptions.ConnectionError as ex:
                plog(["retry"], i+1)

    def update_search_list(self, novels: {}):
        for novel in novels:
            self.search_list_recycle.data.append({"text": novel.title, "url": novel.url})

    def search_work(self, session: requests.Session, keyword: str, website: Website):
        novels = search(session, keyword, website)
        if novels:
            plog(["# Of Searched"], len(novels))
            self.update_search_list(novels)
        self.__searching = False

    def start_search(self):
        if not self.__searching:
            self.__searching = True
            plog(['searching'], self.search_input.text)
            self.search_list_recycle.data.clear()

            with requests.Session() as session:
                thread = threading.Thread(target=self.search_work, args=(session, self.search_input.text, Website.BOXNOVELCOM))
                thread.start()
        else:
            plog(["already searching"], self.search_input.text)
        
class SearchItem(Button):
    url = StringProperty()

    def browse(self):
        plog(['browsing'], self.text)
        self.parent.parent.parent.parent.goto_info_page(self.url)
        # Clock.schedule_once(partial(), 0)




