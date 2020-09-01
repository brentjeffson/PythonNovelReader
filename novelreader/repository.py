import requests
import sqlite3 as sql
from novelreader.services import Services
from novelreader.models import Database
from wescrape.models.novel import Novel, Chapter, Meta



# Handles getting data from database and web
# Get data from web if nothing 
# Get data from database

class Repository:
    INSTANCE = None

    @classmethod
    def build(cls, service: Services, database: Database) -> Repository:
        if cls.INSTANCE is None:
            cls.INSTANCE = Repository(service, database)
        return cls.INSTANCE

    @classmethod
    def instance(cls):
        return cls.INSTANCE

    def __init__(self, service: Services, database: Database):
        self.__db = db
        self.__service = service
        self.__database = database
    
    def get_novel(self, url: str) -> Novel:
        """Get Novel From Web, If Nothing """
        # get from web
        novel = None
        try: 
            novel = self.__service.fetch_novel(url)
            if novel is not None:
                return novel
        except Exception as ex:
            plog(["exception", "get_novel"], ex)
        finally:
            # get from database
            novel = self.__database.select_novel(url)
        return novel

    def get_chapters(self, url: str):
        # get from web
        chapters = []
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

    def get_meta(self, url):
        # get from web
        meta = []
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

