import requests
from wescrape.models.novel import Novel
from wescrape.parsers.nparse import NovelBaseParser
from bs4 import BeautifulSoup

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

# todo parse_content, parse content of a chapter
def get_content(soup: BeautifulSoup, parser: NovelBaseParser) -> str:
    """Get content of chapter from parsed chapter markup."""
    content = parser.get_content(soup)
    return content

