import aiohttp
from wescrape.models.novel import Novel
from wescrape.parsers.nparse import NovelBaseParser
from bs4 import BeautifulSoup

async def fetch_markup(session: aiohttp.ClientSession, url: str) -> str:
    """Fetch markup of `URL` from web."""
    async with session.get(url) as resp:
        if resp.reason.lower() != 'ok':
            return None, resp.status
        
        return await resp.text(), resp.status

async def parse_markup(markup: str, parser: str = "html.parser"):
    """Parse markup using BeautifulSoup"""
    soup = BeautifulSoup(markup, features="html.parser")
    return soup

# parse novel information together with its chapters
async def get_novel(url: str, soup: BeautifulSoup, parser: NovelBaseParser) -> Novel:
    """Get data on the novel from the parsed markup `soup`"""
    novel = parser.get_novel(soup)
    novel.url = url
    return novel

# todo parse_content, parse content of a chapter
async def get_content(soup: BeautifulSoup, parser: NovelBaseParser) -> str:
    """Get content of chapter from parsed chapter markup."""
    content = parser.get_content(soup)
    return content

