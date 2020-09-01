import requests
import sqlite3 as sql
from novelreader.services import Service
from novelreader.database import Database
from wescrape.models.novel import Novel, Chapter, Meta



# Handles getting data from database and web
# Get data from web if nothing 
# Get data from database

class Repository:
    INSTANCE = None

    @classmethod
    def build(cls, 
        db: sql.Connection, 
        session: requests.Session, 
        service: Service, 
        database: Database
    ) -> Repository:

        if cls.INSTANCE is None:
            cls.INSTANCE = Repository(db, session, service, database)
        return cls.INSTANCE

    @classmethod
    def instance(cls):
        return cls.INSTANCE

    def __init__(self, 
        db: sql.Connection, 
        session: requests.Session, 
        service: Service, 
        database: Database
    ):

        self.__db = db
        self.__session = session
        self.__service = service
        self.__database = database
    
    def get_novel(self, url: str) -> Novel:
        """Get Novel From Web, If Nothing """
        # get from web
        novel = None
        try: 
            novel = self.__service.fetch_novel(self.__session, url)
            if novel is not None:
                return novel
        except Exception as ex:
            plog(["exception", "get_novel"], ex)
        finally:
            # get from database
            novel = self.__database.select_novel(self.__db, url)
        return novel

    def get_chapters(self, url: str):
        # get from web
        chapters = []
        try: 
            chapters = self.__service.fetch_chapters(self.__session, url)
            if chapters is not None:
                return chapters
        except Exception as ex:
            plog(["exception", "get_chapters"], ex)
        finally:
            # get from database
            chapters = self.__database.select_chapters(self.__db, url)
        return chapters

    def get_meta():
        # get from web
        meta = []
        try: 
            meta = self.__service.fetch_meta(self.__session, url)
            if meta is not None:
                return meta
        except Exception as ex:
            plog(["exception", "get_chapters"], ex)
        finally:
            # get from database
            meta = self.__database.select_meta(self.__db, url)
        return meta

