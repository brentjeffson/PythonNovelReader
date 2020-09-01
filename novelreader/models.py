import sqlite3 as sql
from novelreader.helpers import plog
from wescrape.models.novel import Meta, Chapter, Meta, Novel

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

    def commit(self):
        self.__conn.commit()

    @classmethod
    def instance(cls):
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
    def create_novels_table(self):
        statement = """CREATE TABLE IF NOT EXISTS NOVELS(
            URL TEXT PRIMARY KEY,
            TITLE TEXT NOT NULL,
            THUMBNAIL TEXT NOT NULL);
        """
        self.__conn.execute(statement)

    def create_chapters_table(self):
        statement = """CREATE TABLE IF NOT EXISTS CHAPTERS(
            URL TEXT PRIMARY KEY,
            CHAPTER_ID TEXT NOT NULL,
            TITLE TEXT NOT NULL,
            CONTENT TEXT,
            NOVEL_URL TEXT NOT NULL,
            FOREIGN KEY (NOVEL_URL)
                REFERENCES NOVELS (URL));
        """
        self.__conn.execute(statement)

    def create_metas_table(self):
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
        self.__conn.execute(statement)

    # insert functions
    def insert_novel(self, url: str, title: str, thumbnail: str):
        statement = """INSERT INTO NOVELS (URL, TITLE, THUMBNAIL) VALUES (?, ?, ?);"""
        self.__conn.execute(statement, (url, title, thumbnail))

    def insert_meta(self, novel_url: str, meta: Meta):
        statement = """INSERT INTO 
        METAS (
            AUTHORS, GENRES, RATING, STATUS, RELEASE_DATE, DESCRIPTION, NOVEL_URL
        )
        VALUES (?, ?, ?, ?, ?, ?, ?);"""
        if type(meta) == Meta:
            meta = meta.__dict__
            
        values = (
            ", ".join(meta["authors"]),
            ", ".join(meta["genres"]),
            meta["rating"],
            meta["status"].name,
            meta["release_date"],
            meta["description"],
            novel_url
        )
        self.__conn.execute(statement, values)

    def insert_chapter(self, novel_url: str, chapter: Chapter):
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
        self.__conn.execute(statement, values)


    def update_chapter(self, url: str, chapter: Chapter):
        """Update cols of selected chapter whose col URL is `url`"""
        statement = """UPDATE CHAPTERS 
        SET CHAPTER_ID = ?,
            TITLE = ?,
            CONTENT = ?
        WHERE URL = ?;"""

        if type(chapter) == Chapter:
            chapter = chapter.__dict__

        values = (
            chapter["id"],
            chapter["title"],
            chapter["content"],
            chapter["url"]
        )

        self.__conn.execute(statement, values)

    def __select(self, cols: list, table: str, where: list = None, where_val: tuple = ()):
        if len(cols) == 0:
            cols = ["*"]

        statement = f"SELECT {' '.join(cols)} FROM {table};"

        if where is not None and type(where) == list and len(where_val) > 0 and type(where_val) == tuple:
            statement = f"SELECT {' '.join(cols)} FROM {table} WHERE {' '.join( i + ' == ?' for i in where )};".upper()
            print(statement)
            
        return self.__conn.execute(statement, where_val)

    def __convert_row(row: dict, obj_type):
        converted_row = None
        if row:
            try:
                if obj_type == Novel:
                    converted_row = Novel(
                        url=row["url"],
                        title=row["title"],
                        thumbnail=row["thumbnail"]
                    )
                elif obj_type == Chapter:
                    converted_row = Chapter(
                        id=row["chapter_id"],
                        url=row["url"],
                        title=row["title"],
                        content=row["content"],
                    )
                elif obj_type == Meta:
                    converted_row = Meta(
                        authors=[row["authors"].split(", ")],
                        genres=[row["genres"].split(", ")],
                        rating=row["rating"],
                        release_date=row["release_date"],
                        status=row["status"],
                        description=row["description"],
                    )
            except Exception as ex:
                raise ex
        return converted_row

    def __convert_rows(rows: [dict], convert_type):
        converted_rows = []
        if rows:
            for row in rows:
                converted_row = self.__convert_row(row, convert_type)
                if converted_row:
                    converted_rows.append(converted_row)
        return converted_rows

    def select_novels(self) -> [Novel]:
        cur = Database.__select(self.__conn, [], "novels")
        novel_rows = cur.fetchall()
        novels = self.__convert_rows(novel_rows, Novel)
        return novels


    def select_novel(self, novel_url) -> Novel:
        cur = Database.__select(self.__conn, [], "novels", ["url"], (novel_url,))
        novel_row = cur.fetchone()
        novel = self.__convert_row(novel_row, Novel)
        return novel

    def select_chapters(self) -> [Chapter]:
        cur = Database.__select(self.__conn, [], "chapters")
        chapter_rows = cur.fetchall()
        chapters = self.__convert_rows(chapter_rows, Chapter)
        return chapters

    def select_chapter(self, novel_url) -> Chapter:
        cur = Database.__select(self.__conn, [], "chapters", ["novel_url"], (novel_url,))
        chapter_row = cur.fetchone()
        chapter = self.__convert_row(chapter_row, Chapter)
        return chapter

    def select_metas(self) -> Metas:
        cur = Database.__select(self.__conn, [], "metas")
        meta_rows = cur.fetchall()
        metas = self.__convert_rows(meta_rows, Meta)
        return metas

    def select_meta(self, novel_url) -> Meta:
        cur = Database.__select(self.__conn, [], "metas", ["novel_url"], (novel_url,))
        meta_row = cur.fetchone()
        meta = self.__convert_row(meta_row, Meta)
        return meta
