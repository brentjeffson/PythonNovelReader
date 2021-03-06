from kivy.app import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from wescrape.helpers import identify_parser, identify_status
from wescrape.parsers.nparse import BoxNovelCom, WuxiaWorldCo
from novelreader.services import download_thumbnail
from novelreader.repository import Repository
from novelreader.models import Database, Novel, Chapter, Meta, Website, Status
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
        self.repo = repository

    def open(self, novel):
        # set novel as property
        self.novel = novel
        # download thumbnail
        threading.Thread(target=self.download_work, args=(novel.thumbnail,)).start()
        # update widgets
        self.update_widgets(novel)

    def update_widgets(self, novel: Novel):
        """Update All Widgets"""
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
        new_chapters, num_new_chapter = self.repo.update_chapters(url)
        
        if new_chapters:
            dict_chapters = [{"text": chapter.title, "url": chapter.url} for chapter in new_chapters]
            self.ids.chapter_list.data = dict_chapters

        plog(["# Of New Chapters"], num_new_chapter)
        
    def read_chapter(self, chapter_url):
        # check first if chapter has content in database
        chapter = self.repo.get_chapter()

        if chapter:
            # chapter in database
            if not chapter.has_read:
                # chapter not yet read
                self.repo.update_chapter_has_read(chapter.url, True)

            if not chapter.content:
                # check if chapter has not content
                # get content from web
                content = self.repo.get_chapter_content(chapter_url)
                self.repo.update_chapter_content(chapter_url, content)
                chapter.content = content
            if chapter.content:
                # makes sure that chapter has content
                self.manager.get_screen("reader_page").update_content(chapter.content)
                self.manager.current = "reader_page"
            else:
                plog(["missing", "content"], chapter_url)

    def add_to_library(self):
        """Add Current Instance Of Novel To Database"""
        novel = self.repo.get_novel(self.novel.url, offline=True)
        if novel is None:
            self.repo.save_novel(self.novel)
            self.repo.save_meta(self.novel.url, self.novel.meta)
            self.repo.save_chapters(self.novel.url, self.novel.chapters)

            plog(["added to library"], self.ids.title.text)
        else:
            plog(["in library"], self.ids.title.text)

    def download_work(self, url: str):
        with requests.Session() as session:
            download_thumbnail(session, url)    

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
