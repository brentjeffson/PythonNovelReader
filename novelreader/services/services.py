import requests
from pathlib import Path
from wescrape.helpers import identify_parser, parse_markup
from novelreader.models import Novel, Chapter, Meta

class Services:

    INSTANCE = None

    @classmethod
    def build(cls, session: requests.Session):
        if cls.INSTANCE is None:
            cls.INSTANCE = Services(session)
        return cls.INSTANCE

    @classmethod
    def instance(cls):
        return cls.INSTANCE

    def __init__(self, session: requests.Session):
        self.__session = session

    @property
    def session(self):
        return self.__session

    def __fetch(self, item_type, url: str):
        parser = identify_parser(url)
        markup = self.fetch_markup(url)
        item = None
        if markup is not None and parser is not None:
            soup = parse_markup(markup)
            if item_type == Novel:
                novel = parser.get_novel(url, soup)
                chapters = parser.get_chapters(soup)
                meta = parser.get_meta(soup)
                item = Novel(
                    url=novel.url,
                    title=novel.title,
                    thumbnail=novel.thumbnail,
                    meta=meta,
                    chapters=chapters
                )
            if item_type == Chapter:
                item = parser.get_chapters(soup)
                # convert to new Chapter Object
                temp_items = []
                for i in item:
                    temp_items.append(
                        Chapter(i.title, i.url, i.id, i.content)
                    )
                item = temp_items
            if item_type == Meta:
                item = parser.get_meta(soup)
        return item

    def fetch_novel(self, novel_url: str) -> Novel:
        """Fetches novel `url` from web, 
        then returns Novel containing chapters and meta
        """
        novel = self.__fetch(Novel, novel_url)
        return novel

    def fetch_chapters(self, novel_url: str) -> [Chapter]:
        chapters = self.__fetch(Chapter, novel_url)
        return chapters if chapters is not None else []

    def fetch_chapter(self, novel_url: str, chapter_url: str) -> Chapter:
        """Fetches chapter from novel `novel_url` where chapter is `chapter_url`."""
        chapter = None
        chapters = self.__fetch(Chapter, novel_url)
        if chapters:
            for c in chapters:
                if c.url == chapter_url:
                    chapter = c
                    break
        return chapter

    def fetch_meta(self, novel_url: str) -> Meta:
        meta = self.__fetch(Meta, novel_url)
        return meta

    def fetch_content(self, chapter_url: str) -> str:
        markup = self.fetch_markup(chapter_url)
        soup = parse_markup(markup)
        parser = identify_parser(chapter_url)
        content = parser.get_content(soup)
        return content
        
    def fetch_markup(self, markup_url: str) -> str:
        resp = self.__session.get(markup_url)
        markup = None
        if resp.ok:
            markup = resp.text
        return markup


def download_thumbnail(session: requests.Session, thumbnail_url: str) -> bool:
    filename = thumbnail_url.split("/")[-1]
    img_path = Path("novelreader", "public", "imgs", filename).absolute()
    if not img_path.exists():
        resp = session.get(thumbnail_url)
        if resp.ok:
            img_path.write_bytes(resp.content)
            return True
    return False
