from kivy.app import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from wescrape.helpers import identify_parser, identify_status
from wescrape.parsers.nparse import BoxNovelCom, WuxiaWorldCo
from wescrape.models.novel import Novel, Meta, Website, Status, Chapter
from novelreader.repository import Repository
from novelreader.models import Database
from novelreader.helpers import plog
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
        if novel:
            self.update_widgets()


    def update_widgets(self, url):
        """Update All Widgets"""
        # fetch from database
        dbnovel = Database.select_novel(self.db.conn, url)
        dbmetas = Database.select_meta(self.db.conn, url)
        dbchapters = Database.select_chapter(self.db.conn, url)

        novel = None
        if dbnovel is not None and dbmetas is not None:      
            chapter_list = []
            for chapter in dbchapters:
                chapter_list.append(
                    Chapter(
                        id=chapter["chapter_id"],
                        title=chapter["title"],
                        url=chapter["url"],
                        content=chapter["content"],
                    )
                )

            novel = Novel(
                id=dbnovel["id"],
                title=dbnovel["title"],
                url=dbnovel["url"],
                thumbnail=dbnovel["thumbnail"],
                meta=Meta(
                    authors=[i.strip() for i in dbmetas["authors"].split(",")],
                    genres=[i.strip() for i in dbmetas["genres"].split(",")],
                    rating=float(dbmetas["rating"]),
                    release_date=dbmetas["release_date"],
                    status=identify_status(dbmetas["status"]),
                    description=dbmetas["description"]
                ),
                chapters=chapter_list
            )
        else:
        # fetch from web
            with requests.Session() as session:
                parser = identify_parser(url)
                if parser is not None:
                    markup, status_code = fetch_markup(session, url)
                    soup = parse_markup(markup)
                    novel = get_novel(url, soup, parser)
                    
        if novel is not None:
            self.novel = novel
            self.ids.title.text = novel.title
            self.ids.authors.value = ', '.join(novel.meta.authors)
            self.ids.genres.value = ', '.join(novel.meta.genres)
            self.ids.status.value = novel.meta.status.name
            self.ids.release_date.value = novel.meta.release_date
            self.ids.rating.value = str(novel.meta.rating)
            dict_chapters = [{"text": chapter.title, "url": chapter.url} for chapter in novel.chapters]
            self.ids.chapter_list.data = dict_chapters

            thumbnail_path = Path(
                "novelreader", 
                "public", 
                "imgs", 
                novel.thumbnail.split("/")[-1]
            ).absolute()
            # download thumbnail
            session = requests.Session()
            if download_thumbnail(session, self.novel.thumbnail):
                plog(["downloaded"], 'thumnbail')
            session.close()
            if thumbnail_path.exists():
                self.ids.thumbnail.source = str(thumbnail_path)

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
        # get saved chapters from database
        saved_chapters = Database.select_novel_chapters(self.db.conn, url)
        converted_saved_chapters = []
        # convert to Chapter object
        if len(saved_chapters) > 0:
            for saved_chapter in saved_chapters:
                converted_saved_chapters.append(Chapter(
                    id=saved_chapter["chapter_id"],
                    title=saved_chapter["title"],
                    url=saved_chapter["url"],
                    content=saved_chapter["content"]
                ))
            saved_chapters = converted_saved_chapters
        # fetched chapters from web
        new_chapters = []
        with requests.Session() as session:
            new_chapters = self.fetch_chapters(session, url)
        # compare new chapters and saved chapters
        if len(new_chapters) > 0 and len(saved_chapters) > 0:
            num_new_chapter = 0
            for new_chapter in new_chapters:
                for saved_chapter in saved_chapters:
                    # if new chapter is not in saved chapters
                    if new_chapter.url != saved_chapter.url:
                        # save new chapter to database
                        with self.db.conn:
                            Database.insert_chapter(self.db.conn, url, new_chapter)
                            num_new_chapter += 1
        elif len(new_chapters):
            # no saved chapter for novel, save all new chapters
            for new_chapter in new_chapters:
                with self.db.conn:
                    Database.insert_chapter(self.db.conn, url, new_chapter)
                    num_new_chapter += 1
                        
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
