import requests
from wescrape.models.novel import Novel, Chapter
from wescrape.parsers.nparse import NovelBaseParser
from bs4 import BeautifulSoup
from pathlib import Path


def download_thumbnail(session: requests.Session, url: str) -> bool:
    filename = url.split("/")[-1]
    img_path = Path("novelreader", "public", "imgs", filename).absolute()
    if not img_path.exists():
        resp = session.get(url)
        if resp.ok:
            img_path.write_bytes(resp.content)
            return True
    return False


def fetch_markup(session: requests.Session, url: str) -> str:
    """Fetch markup of `URL` from web."""
    resp = session.get(url)
    if resp.ok:
        return resp.text, resp.status_code
    return None, resp.status_code


def parse_markup(markup: str, parser: str = "html.parser"):
    """Parse markup using BeautifulSoup"""
    soup = BeautifulSoup(markup, features="html.parser")
    return soup


# parse novel information together with its chapters
def get_novel(url: str, soup: BeautifulSoup, parser: NovelBaseParser) -> Novel:
    """Get data on the novel from the parsed markup `soup`"""
    novel = parser.get_novel(soup)
    novel.url = url
    return novel



def get_content(soup: BeautifulSoup, parser: NovelBaseParser) -> str:
    """Get content of chapter from parsed chapter markup."""
    content = parser.get_content(soup)
    return content


def get_chapters(soup: BeautifulSoup, parser: NovelBaseParser) -> [Chapter]:
    """Get Chapters Of Novel From Parser Novel Markup"""
    chapters = parser.get_chapters(soup)
    return chapters
