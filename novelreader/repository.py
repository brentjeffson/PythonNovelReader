import requests
import sqlite3 as sql
from novelreader.services import Services
from novelreader.models import Database
from novelreader.helpers import plog
from wescrape.models.novel import Novel, Chapter, Meta, Status, Website



# Handles getting data from database and web
# Get data from web if nothing 
# Get data from database

class Repository:
    INSTANCE = None

    @classmethod
    def build(cls, service: Services, database: Database):
        if cls.INSTANCE is None:
            cls.INSTANCE = Repository(service, database)
        return cls.INSTANCE

    @classmethod
    def instance(cls):
        return cls.INSTANCE

    def __init__(self, service: Services, database: Database):
        self.__service = service
        self.__database = database
    
    def save(self):
        self.__database.commit()

    def create_tables(self):
        self.create_novels_table()
        self.create_chapters_table()
        self.create_metas_table()

    def create_novels_table(self):
        self.__database.create_novels_table()
    
    def create_chapters_table(self):
        self.__database.create_chapters_table()

    def create_metas_table(self):
        self.__database.create_metas_table()

    def __get_online_item(self, target, target_type):
        item = None
        if target_type == Novel:
            item = self.__service.fetch_novel(target)
        elif target_type == Meta:
            item = self.__service.fetch_meta(target)
        return item
    
    def __get_offline_item(self, target, target_type):
        item = None
        if target_type == Novel:
            item = self.__database.select_novel(target)
        elif target_type == Meta:
            item = self.__database.select_meta(target)
        return item

    def __get_item(self, target, target_type, offline=False):
        item = None
        if offline:
            item = self.__get_offline_item(target, target_type)
        else:
            item = self.__get_online_item(target, target_type)
        return item

    
    def get_novel(self, novel_url: str, offline: bool = False) -> Novel:
        return self.__get_item(novel_url, Novel, offline)
    
    def get_novels(self) -> [Novel]:
        """Get All Novels From Database"""
        return self.__database.select_novels()
    
    def get_chapter(self, chapter_url: str) -> Chapter:
        """Returns `Chapter` object from database whose `url` is `chapter_url`, 
        otherwise `None`"""
        chapter = None
        try:
            chapter = self.__database.select_chapter(chapter_url)
        except sql.OperationalError as ex:
            plog(["No Chapter"], chapter_url)
        return chapter

    def get_chapters(self, novel_url: str, offline: bool = False):
        chapters = []
        if offline:
            chapters = self.__database.select_chapters(novel_url)
        else:
            chapters = self.__service.fetch_chapters(novel_url)
        return chapters

    def get_chapter_content(self, chapter_url: str, offline: bool = False) -> str:
        content = None
        if offline:
            chapter = self.__database.select_chapter(chapter_url)
            if chapter:
                content = chapter.content
        else:
            try:
                content = self.__service.fetch_content(chapter_url)
            except Exception as ex:
                chapter = self.__database.select_chapter(chapter_url)
                if chapter:
                    content = chapter.content
        return content

    def get_meta(self, novel_url, offline: bool = False):
        return self.__get_item(novel_url, Meta, offline)

    def update_chapter_content(self, chapter_url: str, content: str):
        chapter = self.__database.select_chapter(chapter_url)
        if chapter:
            chapter.content = content
            self.__database.update_chapter(chapter)
            self.save()
            return True

        return False

    def update_chapter_has_read(self, chapter_url: str, has_read: bool):
        chapter = self.__database.select_chapter(chapter_url)
        if chapter:
            chapter.has_read = has_read
            self.__database.update_chapter(chapter)
            self.save()
            return True
        return False

    def update_meta_status(self, novel_url: str, status: Status):
        meta = self.__database.select_meta(novel_url)
        if meta:
            meta.status = status
            self.__database.update_meta(meta)
            self.save()
            return True
        return False
    
    def save_novel(self, novel: Novel):
        self.__database.insert_novel(novel)
        self.save()

    def save_chapters(self, novel_url: str, chapters: [Chapter]):
        for chapter in chapters:
            self.__database.insert_chapter(novel_url, chapter)
        self.save()

    def save_meta(self, novel_url: str, meta: Meta):
        self.__database.insert_meta(novel_url, meta)

    def search(self, keyword: str, website: Website) -> [Novel]:
        novels = []
        if website == Website.BOXNOVELCOM:
            payload = {
                "action": "wp-manga-search-manga",
                "title": keyword
            }
            resp = self.__service.session.post("https://boxnovel.com/wp-admin/admin-ajax.php", data=payload)
            if resp.ok:
                for novel in resp.json()["data"]:
                    novels.append(Novel(
                        title=novel["title"],
                        url=novel["url"],
                        thumbnail=""
                    ))
        elif website == Website.WUXIAWORLDCO:
            search_selector = "ul.result-list > li.list-item > a.list-img"
            keyword = keyword.replace(" ", "%20")
            endpoint = '/'.join(["https://m.wuxiaworld.co/search", keyword, "1"])
            resp = self.__service.session.get(endpoint)
            if resp.ok:
                markup = resp.text
                soup = parse_markup(markup)
                novel_tags = soup.select(search_selector)
                for tag in novel_tags:
                    img_tag = tag.find("img")
                    url = ''.join(["https://m.wuxiaworld.co", tag["href"]])
                    title = img_tag["alt"]

                    novels.append(Novel(
                        id=url,
                        title=title,
                        url=url,
                        thumbnail=""
                    ))
        return novels

