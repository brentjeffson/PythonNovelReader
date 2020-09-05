import requests
import sqlite3 as sql
from novelreader.services import Services
from novelreader.models import Database
from novelreader.helpers import plog
from wescrape.models.novel import Novel, Chapter, Meta



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
        elif target_type == Chapter:
            item = self.__service.fetch_chapters(target)
        elif target_type == Meta:
            item = self.__service.fetch_meta(target)
        return item
    
    def __get_offline_item(self, target, target_type):
        item = None
        if target_type == Novel:
            item = self.__database.select_novel(target)
        elif target_type == Chapter:
            item = self.__database.select_chapter(target)
        elif target_type == Meta:
            item = self.__database.select_meta(target)
        return item

    def __get_item(self, target, target_type, offline=False):
        item = None
        if offline:
            item = self.__get_offline_item(target, target_type)
        else:
            try: 
                item = self.__get_online_item(target, target_type)
            except Exception as ex:
                item = self.__get_offline_item(target, target_type)
                plog(["exception", "get_item"], ex)
        return item

    def get_novels(self) -> [Novel]:
        """Get All Novels From Database"""
        return self.__database.select_novels()
    
    def get_novel(self, novel_url: str, offline: bool = False) -> Novel:
        return self.__get_item(novel_url, Novel, offline)

    def get_chapter(self, chapter_url: str, offline = False) -> Chapter:
        """Get a single chapter from database or web"""
        chapters = self.__get_item(chapter_url, Chapter, offline)
        chapter = None
        if chapters:
            for chapter in chapters:
                if chapter.url == chapter_url:
                    return chapter
        return chapter

    def get_chapters(self, novel_url: str, offline: bool = False):
        chapters = []
        if offline:
            chapters = self.__database.select_chapters(novel_url)
        try:
            chapters = self.__service.fetch_chapters()
        except Exception as ex:
            chapters = self.__database.select_chapters(novel_url)
        return 

    def get_meta(self, novel_url, offline: bool = False):
        return self.__get_item(novel_url, Meta, offline)

    def get_chapter_content(self, chapter_url: str) -> str:
        content = self.__service.fetch_content(chapter_url)
        return content

    def update_chapter(self, chapter: Chapter):
        """Update chapter in database whose `url` is equal to `chapter.url`"""
        self.__database.update_chapter(chapter)

    def update_chapters(self, novel_url: str):
        """Fetch chapters of Novel `novel_url` from web, save new chapters to database."""
        new_chapters = self.__service.fetch_chapters(novel_url)
        saved_chapters = self.__database.select_chapters(novel_url)
        # remove content on saved chapters
        for chapter in saved_chapters:
            saved_chapters.content = ""

        num_new_chapters = 0
        if saved_chapters:
            # save chapters not in old chapters
            for new_chapter in new_chapters:
                if new_chapter not in saved_chapters:
                    # saved new chapter
                    self.__database.insert_chapter(novel_url, new_chapter)
                    num_new_chapters += 1
                    
        plog(["number of new chapters"], len(num_new_chapters))
        return new_chapters, num_new_chapters
    
    def insert_novel(self, novel: Novel):
        self.__database.insert_novel(novel)

    def insert_chapters(self, novel_url: str, chapters: Chapter):
        for chapter in chapters:
            self.__database.insert_chapter(novel_url, chapter)

    def insert_meta(self, novel_url: str, meta: Meta):
        self.__database.insert_meta(novel_url, meta)

