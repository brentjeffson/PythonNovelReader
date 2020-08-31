from kivy.app import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from wescrape.parsers.helpers import identify_parser
from wescrape.parsers.nparse import BoxNovelCom, WuxiaWorldCo
from wescrape.models.novel import Novel, Meta, Website
from novelreader.services.ndownloader import (fetch_markup, parse_markup, get_content)
from pathlib import Path
from novelreader.helpers import plog
from functools import partial
from novelreader.models import Database
import requests



Builder.load_file(str(Path('novelreader/views/info_page.kv').absolute()))

class InfoPage(Screen):
    """Page containing informations related to novel"""
    chapter_list = ObjectProperty()
    title = ObjectProperty()
    authors = ObjectProperty()
    genres = ObjectProperty()
    release_date = ObjectProperty()
    status = ObjectProperty()
    rating = ObjectProperty()

    novel = ObjectProperty(Novel(
        id=-1,
        title="",
        url="",
        thumbnail="",
        meta=Meta(
            rating="",
            release_date="",
            status=""
        )
    ))
    
    def on_start(self, db):
        self.db = db

    def add_to_library(self):
        """Add Current Instance Of Novel To Database"""
        novel = Database.select_novel(self.db.conn, self.novel.url)

        if novel is None:
            Database.insert_novel(self.db.conn, self.novel.url, self.novel.title)
            Database.insert_meta(self.db.conn, self.novel.url, self.novel.meta)
            self.db.commit()
            
            plog(["add to library"], self.title.text)
        else:
            plog(["in library"], self.title.text)


    def prep_content(self, url):
        # todo fetch novel from database
        # if None; fetch from web
        with requests.Session() as session:
            Clock.schedule_once(partial(self.fetch_content, session, url), 0)

    def fetch_content(self, session, url, _):
        parser = identify_parser(url)

        reader_page = self.manager.get_screen("reader_page")
        markup, status_code = fetch_markup(session, url)
        soup = parse_markup(markup)
        content = get_content(soup, parser)
        if content is not None:
            reader_page.update_content(content)
            self.manager.current = "reader_page"
    
    def update_widgets(self, novel):
        self.novel = novel
        self.title.text = novel.title
        self.authors.value = ', '.join(novel.meta.authors)
        self.genres.value = ', '.join(novel.meta.genres)
        self.status.value = novel.meta.status.name
        self.release_date.value = novel.meta.release_date
        dict_chapters = [{"text": chapter.title, "url": chapter.url} for chapter in novel.chapters]
        self.chapter_list.data = dict_chapters

class ChapterItem(Button):
    """Chapter list item"""
    url = StringProperty()

    def read(self):
        plog(["reading"], self.text)
        self.parent.parent.parent.parent.prep_content(self.url)

class InfoItem(GridLayout):
    """Contain a name and value"""
    name = StringProperty()
    value = StringProperty()
