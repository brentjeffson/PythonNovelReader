import requests
from pathlib import Path
from wescrape.helpers import identify_parser, parse_markup
from wescrape.models.novel import Novel, Chapter, Meta

class Services:

    INTANCE = None

    @classmethod
    def build(cls, session: requests.Session):
        if cls.INTANCE is None:
            cls.INTANCE = Services(session)
        return cls.INTANCE

    def __init__(self, session: requests.Session):
        self.__session = session

    def __fetch(self, item_type, url: str):
        parser = identify_parser(url)
        markup = Services.fetch_markup(self.__session, url)
        item = None
        if markup is not None and parser is not None:
            soup = parse_markup(markup)
            if item_type == Novel:
                item = parser.get_novel(soup)
            if item_type == Chapter:
                item = parser.get_chapters(soup)
            if item_type == Meta:
                item = parser.get_meta(soup)
        return item

    def fetch_novel(self, url: str) -> Novel:
        novel = self.__fetch(Novel, url)
        return novel

    def fetch_chapters(self, url: str) -> [Chapter]:
        chapters = self.__fetch(Chapter, url)
        return chapters if chapters is not None else []

    def fetch_meta(self, url: str) -> Meta:
        meta = self.__fetch(Meta, url)
        return meta

    def fetch_content(self, url: str) -> str:
        markup = Services.fetch_markup(url)
        soup = parse_markup(markup)
        parser = identify_parser(url)
        content = parser.get_content(soup)
        return content
        
    @staticmethod
    def fetch_markup(session: requests.Session, url: str) -> str:
        resp = session.get(url)
        markup = None
        if resp.ok:
            markup = resp.text
        return markup


def download_thumbnail(session: requests.Session, url: str) -> bool:
    filename = url.split("/")[-1]
    img_path = Path("novelreader", "public", "imgs", filename).absolute()
    if not img_path.exists():
        resp = session.get(url)
        if resp.ok:
            img_path.write_bytes(resp.content)
            return True
    return False
