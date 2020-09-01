from kivy.app import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from wescrape.helpers import identify_parser, identify_status
from wescrape.parsers.nparse import BoxNovelCom, WuxiaWorldCo
from wescrape.models.novel import Novel, Meta, Website, Status, Chapter
from novelreader.services import download_thumbnail
from novelreader.repository import Repository
from novelreader.models import Database
from novelreader.helpers import plog, thumbnail_path
from pathlib import Path
from functools import partial
import requests



Builder.load_file(str(Path('novelreader/views/info_page.kv').absolute()))

class InfoPage(Screen):
    """Page containing informations related to novel"""

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
    
    def on_start(self, repository: Repository):
        """Initialize Required Variables"""
        self.repository = repository

    def open(self, url):
        """Opens Novel"""
        # get required data to update variables
        novel = self.repository.get_novel(url)
        chapters = self.repository.get_chapters(url)
        meta = self.repository.get_meta(url)
        # update widgets
        if novel and chapter and meta:
            self.novel = Novel(
                url=novel.url
                title=novel.title,
                thumbnail=novel.thumbnail,
                meta=meta,
                chapters=chapters
            )
            self.update_widgets(self.novel)

    def update_widgets(self, novel: Novel):
        """Update All Widgets"""
        if novel:
            self.ids.title.text = novel.title
            self.ids.authors.value = ', '.join(novel.meta.authors)
            self.ids.genres.value = ', '.join(novel.meta.genres)
            self.ids.status.value = novel.meta.status.name
            self.ids.release_date.value = novel.meta.release_date
            self.ids.rating.value = str(novel.meta.rating)
            dict_chapters = [{"text": chapter.title, "url": chapter.url} for chapter in novel.chapters]
            self.ids.chapter_list.data = dict_chapters

            # download thumbnail
            with requests.Session() as session
                download_thumbnail(session, novel.thumbnail)

            if thumbnail_path(novel.thumbnail).exists():
                self.ids.thumbnail.source = str(thumbnail_path(novel.thumbnail))

    def add_to_library(self):
        """Add Current Instance Of Novel To Database"""
        novel = Database.select_novel(self.db.conn, self.novel.url)

        if novel is None:
            Database.insert_novel(self.db.conn, self.novel.url, self.novel.title, self.novel.thumbnail)
            Database.insert_meta(self.db.conn, self.novel.url, self.novel.meta)
            for chapter in self.novel.chapters:
                Database.insert_chapter(self.db.conn, self.novel.url, chapter)
            self.db.commit()

            # download thumbnail
            session = requests.Session()
            if download_thumbnail(session, self.ids.novel.thumbnail):
                plog(["downloaded"], 'thumnbail')
            session.close()
            
            plog(["added to library"], self.ids.title.text)
        else:
            plog(["in library"], self.ids.title.text)
    
    def update_chapters(self, url: str):
        """Update Chapters Of Novel"""
        new_chapters, num_new_chapter, self.repository.update_chapters(url)
        
        if new_chapters:
            dict_chapters = [{"text": chapter.title, "url": chapter.url} for chapter in new_chapters]
            self.ids.chapter_list.data = dict_chapters

        plog(["# Of New Chapters"], num_new_chapter)
        

    def fetch_chapters(self, session, url) -> [Chapter]:
        """Fetch Chapters From Novel"""
        markup, status_code = fetch_markup(session, url)
        if markup is not None:
            soup = parse_markup(markup)
            chapters = get_chapters(soup)    
            return chapters
        return []
        

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
