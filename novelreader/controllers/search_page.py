from kivy.app import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from wescrape.models.novel import Website
from wescrape.parsers.helpers import identify_parser
from wescrape.parsers.nparse import BoxNovelCom, WuxiaWorldCo
from novelreader.services.ndownloader import (fetch_markup, parse_markup, get_novel)
from . import plog
from pathlib import Path
from functools import partial
import requests

Builder.load_file(str(Path("novelreader/views/search_page.kv").absolute()))

class SearchPage(Screen):
    search_list_recycle = ObjectProperty()
    search_input = ObjectProperty()

    def __init__(self, **kwargs):
        super(SearchPage, self).__init__(**kwargs)

    def goto_info_page(self, url, _):        
        info_page = self.manager.get_screen("info_page")
        info_page.ids.chapter_list.data.clear()

        with requests.Session() as session:
            parser = identify_parser(url)
            if parser is not None:
                markup, status_code = fetch_markup(session, url)
                soup = parse_markup(markup)
                novel = get_novel(url, soup, parser)
                info_page.update_widgets(novel)
                self.manager.current = "info_page"

    def fetch_novels(self, session, _):
        payload = {
            "action": "wp-manga-search-manga",
            "title": self.search_input.text
        }
        resp = session.post("https://boxnovel.com/wp-admin/admin-ajax.php", data=payload)
        print(resp.json())
        self.update_search_list(resp.json()["data"])

    def update_search_list(self, novels: {}):
        for item in novels:
            self.search_list_recycle.data.append({"text": item["title"], "url": item["url"]})
    
    def search(self):
        plog(['searching'], self.search_input.text)
        self.search_list_recycle.data = []
        with requests.Session() as session:
            Clock.schedule_once(partial(self.fetch_novels, session), 0)

class SearchItem(Button):
    url = StringProperty()

    def browse(self):
        plog(['browsing'], self.text)
        Clock.schedule_once(partial(self.parent.parent.parent.parent.goto_info_page, self.url), 0)




