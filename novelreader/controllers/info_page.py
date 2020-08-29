from . import Builder, Screen
from . import ObjectProperty, StringProperty
from . import GridLayout, Button
from . import Path
from . import get_session, get_loop
from . import plog
from wescrape.parsers.helpers import identify_parser
from wescrape.parsers.nparse import BoxNovelCom, WuxiaWorldCo
from wescrape.models.novel import Novel, Meta, Website
from novelreader.services.ndownloader import (fetch_markup, parse_markup, get_novel)

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
    
    def __init__(self, **kwargs):
        super(InfoPage, self).__init__(**kwargs)

    # get novel from database or web
    def fetch_novel(self, url):
        # todo fetch novel from database
        # if None; fetch from web
        loop = get_loop()
        session = get_session()
        loop.run_until_complete(self.process_web_fetch(session, url))
        print(self.ids.keys())

    # fetch novel from web
    async def process_web_fetch(self, session, url):
        parser_type = identify_parser(url)
        parser = None
        if Website.BOXNOVELCOM == parser_type:
            parser = BoxNovelCom()
        elif Website.WUXIAWORLDCO == parser_type:
            parser = WuxiaWorldCo()

        markup, status = await fetch_markup(session, url)
        soup = await parse_markup(markup)
        novel = await get_novel(url, soup, parser)    
        dict_chapters = [{"text": chapter.title, "url": chapter.url}for chapter in novel.chapters]
        self.chapter_list.data = dict_chapters
        self.update_widgets(novel)
        plog(["FETCHED"], url)
    
    def update_widgets(self, novel):
        self.title.text = novel.title
        self.authors.value = ', '.join(novel.meta.authors)
        self.genres.value = ', '.join(novel.meta.genres)
        self.status.value = novel.meta.status.name
        self.release_date.value = novel.meta.release_date

class ChapterItem(Button):
    """Chapter list item"""
    url = StringProperty()

    def read(self):
        plog(["READING"], self.text)

class InfoItem(GridLayout):
    """Contain a name and value"""
    name = StringProperty()
    value = StringProperty()
