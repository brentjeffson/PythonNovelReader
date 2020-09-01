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
import threading



Builder.load_file(str(Path('novelreader/views/info_page.kv').absolute()))

class InfoPage(Screen):
    """Page containing informations related to novel"""

    novel = ObjectProperty(Novel(
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

    def open(self, url: str):
        """Opens novel `url`"""
        # get required data to update variables
        novel = self.repository.get_novel(url)
        chapters = self.repository.get_chapters(url)
        meta = self.repository.get_meta(url)

        # download thumbnail
        threading.Thread(target=self.download_work, args(novel.thumbnail,)).start()

        # update widgets
        if novel and chapters and meta:
            self.novel = Novel(
                url=novel.url,
                title=novel.title,
                thumbnail=novel.thumbnail,
                meta=meta,
                chapters=chapters
            )
            self.update_widgets(self.novel)

    def add_to_library(self):
        """Add Current Instance Of Novel To Database"""
        novel = self.repository.get_novel(self.novel.url, offline=True)
        if novel is None:
            self.repository.insert_novel(self.novel)
            self.repository.insert_meta(self.novel.meta)
            self.repository.insert_chapters(self.novel.chapters)
            self.repository.save()
            
            plog(["added to library"], self.ids.title.text)
        else:
            plog(["in library"], self.ids.title.text)
    
    def download_work(self, url: str):
        with requests.Session() as session:
            download_thumbnail(session, url)

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

            if thumbnail_path(novel.thumbnail).exists():
                self.ids.thumbnail.source = str(thumbnail_path(novel.thumbnail))

    def update_chapters(self, url: str):
        """Update Chapters Of Novel"""
        new_chapters, num_new_chapter = self.repository.update_chapters(url)
        
        if new_chapters:
            dict_chapters = [{"text": chapter.title, "url": chapter.url} for chapter in new_chapters]
            self.ids.chapter_list.data = dict_chapters

        plog(["# Of New Chapters"], num_new_chapter)
        
    def read_chapter(self, url):
        content = self.repository.get_chapter_content(url)
        self.manager.get_screen("reader_page").update_content(content)
        self.manager.current = "reader_page"
    
class ChapterItem(Button):
    """Chapter list item"""
    url = StringProperty()

    def read(self):
        plog(["reading"], self.text)
        self.parent.parent.parent.parent.read_chapter(self.url)

class InfoItem(GridLayout):
    """Contain a name and value"""
    name = StringProperty()
    value = StringProperty()
