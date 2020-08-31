import sqlite3 as sql
from novelreader.helpers import plog
from wescrape.models.novel import Meta, Chapter

class Database:
    INSTANCE = None

    @classmethod
    def build(cls, db_file):
        """Build An Instance Of Database"""
        if cls.INSTANCE is None:
            cls.INSTANCE = Database(db_file)
            plog(["created"], "database instance")
            return cls.INSTANCE
        else:
            plog(["exists"], "database instance")
            return cls.INSTANCE
            
    
    def __init__(self, db_file):
        self.__conn = sql.connect(db_file)

    @classmethod
    def get_instance(cls):
        if cls.INSTANCE is not None:
            return cls.INSTANCE
        else:
            plog(["missing"], "database instance")
    
    @classmethod
    def close(cls):
        """Close Database Connection, Clear Instance"""
        if cls.INSTANCE is not None:
            cls.INSTANCE.conn.close()
            cls.INSTANCE = None
            plog(["removed"], "database instance")
        else:
            plog(["missing"], "database instance")

    @property
    def conn(self):
        return self.__conn
        
    # create functions
    @staticmethod
    def create_novels_table(conn):
        statement = """CREATE TABLE IF NOT EXISTS NOVELS(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            URL TEXT UNIQUE NOT NULL,
            TITLE TEXT NOT NULL);
        """
        conn.execute(statement)

    @staticmethod
    def create_chapters_table(conn):
        statement = """CREATE TABLE IF NOT EXISTS CHAPTERS(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CHAPTER_ID REAL NOT NULL,
            URL TEXT UNIQUE NOT NULL,
            TITLE TEXT NOT NULL,
            CONTENT TEXT,
            NOVEL_URL TEXT UNIQUE NOT NULL,
            FOREIGN KEY (NOVEL_URL)
                REFERENCES NOVELS (URL));
        """
        conn.execute(statement)

    @staticmethod
    def create_metas_table(conn):
        statement = """CREATE TABLE IF NOT EXISTS METAS(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            AUTHORS TEXT,
            GENRES TEXT,
            RATING REAL,
            RELEASE_DATE TEXT,
            STATUS TEXT,
            DESCRIPTION TEXT,
            NOVEL_URL TEXT UNIQUE NOT NULL,
            FOREIGN KEY (NOVEL_URL)
                REFERENCES NOVELS (URL));
        """
        conn.execute(statement)

    # insert functions
    @staticmethod
    def insert_novel(conn, url: str, title: str):
        statement = """INSERT INTO NOVELS (URL, TITLE) VALUES (?, ?);"""
        conn.execute(statement, (url, title))

    @staticmethod
    def insert_meta(conn, novel_url: str, meta: Meta):
        statement = """INSERT INTO METAS (AUTHORS, GENRES, RATING, STATUS, RELEASE_DATE, DESCRIPTION, NOVEL_URL) VALUES (?, ?, ?, ?, ?, ?, ?);"""
        if type(meta) == Meta:
            meta = meta.__dict__
            
        values = (
            ", ".join(meta["authors"]),
            ", ".join(meta["genres"]),
            meta["rating"],
            meta["status"],
            meta["release_date"],
            meta["description"],
            novel_url
        )
        conn.execute(statement, values)

    @staticmethod
    def insert_chapter(conn, novel_url: str, chapter: Chapter):
        statement = """INSERT INTO CHAPTERS (CHAPTER_ID, URL, TITLE, CONTENT, NOVEL_URL) VALUES(?, ?, ?, ?, ?);"""
        if type(chapter) == Chapter:
            chapter = chapter.__dict__

        values = (
            chapter["id"],
            chapter["url"],
            chapter["title"],
            chapter["content"],
            novel_url
        )
        conn.execute(statement, values)

    @staticmethod
    def update_chapter(conn, novel_url: str, chapter: Chapter):
        statement = """UPDATE CHAPTERS 
        SET CHAPTER_ID = ?,
            URL = ?,
            TITLE = ?,
            CONTENT = ?
        WHERE NOVEL_URL = ?;"""

        if type(chapter) == Chapter:
            chapter = chapter.__dict__

        values = (
            chapter["id"],
            chapter["url"],
            chapter["title"],
            chapter["content"],
            novel_url
        )

        conn.execute(statement, values)

    @staticmethod
    def __select(conn, cols: list, table: str, where: list = None, where_val: tuple = ()):
        if len(cols) == 0:
            cols = ["*"]

        statement = f"SELECT {' '.join(cols)} FROM {table};"

        if where is not None and type(where) == list and len(where_val) > 0 and type(where_val) == tuple:
            statement = f"SELECT {' '.join(cols)} FROM {table} WHERE {' '.join( i + ' == ?' for i in where )};".upper()
            print(statement)
            
        return conn.execute(statement, where_val)

    @staticmethod
    def select_novels(conn):
        cur = Database.__select(conn, [], "novels")
        return cur.fetchall()

    @staticmethod
    def select_novel(conn, novel_url):
        cur = Database.__select(conn, [], "novels", ["url"], (novel_url,))
        return cur.fetchone()

    @staticmethod
    def select_chapters(conn):
        cur = Database.__select(conn, [], "chapters")
        return cur.fetchall() 

    @staticmethod
    def select_chapter(conn, novel_url):
        cur = Database.__select(conn, [], "chapters", ["novel_url"], (novel_url,))
        return cur.fetchone()

    @staticmethod
    def select_metas(conn):
        cur = Database.__select(conn, [], "metas")
        return cur.fetchall()

    @staticmethod
    def select_meta(conn, novel_url):
        cur = Database.__select(conn, [], "metas", ["novel_url"], (novel_url,))
        return cur.fetchone()
