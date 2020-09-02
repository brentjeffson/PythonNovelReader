import requests
from pathlib import Path
from wescrape.helpers import identify_parser, parse_markup
from wescrape.models.novel import Novel, Chapter, Meta

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

    def __fetch(self, item_type, url: str):
        parser = identify_parser(url)
        markup = Services.fetch_markup(self.__session, url)
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

    def fetch_meta(self, novel_url: str) -> Meta:
        meta = self.__fetch(Meta, novel_url)
        return meta

    def fetch_content(self, chapter_url: str) -> str:
        markup = Services.fetch_markup(self.__session, chapter_url)
        soup = parse_markup(markup)
        parser = identify_parser(url)
        content = parser.get_content(soup)
        return content
        
    @staticmethod
    def fetch_markup(session: requests.Session, markup_url: str) -> str:
        resp = session.get(markup_url)
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
