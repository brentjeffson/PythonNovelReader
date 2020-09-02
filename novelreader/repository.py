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
            item = self.__database.select_chapters(target)
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
    
    def get_novel(self, url: str, offline: bool = False) -> Novel:
        """Get Novel From Web, If Nothing """
        # get from web
        novel = self.__get_item(url, Novel, offline)
        return novel

    def get_chapters(self, url: str, offline: bool = False):
        # get from web
        chapters = []
        if offline:
            return self.__database.select_chapters(url)
        
        try: 
            chapters = self.__service.fetch_chapters(url)
            if chapters is not None:
                return chapters
        except Exception as ex:
            plog(["exception", "get_chapters"], ex)
        finally:
            # get from database
            chapters = self.__database.select_chapters(url)
        return chapters

    def get_meta(self, url, offline: bool = False):
        # get from web
        meta = []
        if offline:
            return self.__database.select_meta(url)

        try: 
            meta = self.__service.fetch_meta(url)
            if meta is not None:
                return meta
        except Exception as ex:
            plog(["exception", "get_chapters"], ex)
        finally:
            # get from database
            meta = self.__database.select_meta(url)
        return meta

    def get_chapter_content(self, url: str) -> str:
        # get content
        content = self.__service.fetch_content(url)
        # update content of chapter in the database
        chapter = self.__database.select_chapter(url)
        updated_chapter = Chapter(
            id=chapter.id,
            url=chapter.url,
            title=chapter.title,
            content=content
        )
        self.__database.update_chapter(url, updated_chapter)
        return content

    def update_chapters(self, url: str):
        """Fetch chapters of novel from web, return updated chapters"""
        new_chapters = self.__service.fetch_chapters(url)
        num_new_chapters = 0
        if new_chapters: 
            saved_chapters = self.__database.select_chapters(url)
            for new_chapter in new_chapters:
                for saved_chapter in saved_chapters:
                    if new_chapter.url != saved_chapter.url:
                        self.__database.insert_chapter(url, new_chapter)
                        num_new_chapters += 1
        return new_chapters, num_new_chapters
    
    def insert_novel(self, novel: Novel):
        self.__database.insert_novel(novel)

    def insert_chapters(self, novel_url: str, chapters: Chapter):
        for chapter in chapters:
            self.__database.insert_chapter(novel_url, chapter)

    def insert_meta(self, novel_url: str, meta: Meta):
        self.__database.insert_meta(novel_url, meta)

