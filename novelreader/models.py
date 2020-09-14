import sqlite3 as sql
from dataclasses import dataclass
from novelreader.helpers import plog, show
from wescrape.helpers import identify_status
from wescrape.models.novel import Novel, Chapter, Meta, Website, Status

@dataclass
class Chapter(Chapter):
    has_read: bool = False

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
        self.__conn.row_factory = sql.Row

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

    # @show
    def __conditions_builder(conditions: [(str, any)]):  
        if type(conditions) == list:
            values = tuple([c[1] for c in conditions]) 
            part = " AND ".join([f"{c[0].upper()} = ?" for c in conditions])
            conditions = " ".join(["WHERE", part]) if len(conditions) > 0 else ""
        else: 
            values = (conditions[1],)
            conditions = f"WHERE {conditions[0].upper()} = ?"
        return conditions, values

    def __set_builder(sets: [(str, any)]):
        values = tuple( [ s[1] for s in sets ] )
        cols = ", ".join( f"{s[0].upper()} = ?" for s in sets )
        return cols, values

    # @show
    def __select(self, table: str, cols:[str] = ["*",], conditions: [(str, any)] = []):
        cols = " ".join(cols) if type(cols) == list else cols
        conditions, values = Database.__conditions_builder(conditions)
        statement = f"""SELECT {cols} FROM {table} {conditions}""".strip().upper()
        rows = self.__conn.execute(statement, values)
        return rows

    def __update(self, table: str, cols=[(str, any)], conditions=[(str, any)]):
        valid_tables = ["novels", "chapters", "metas"]
        if table.lower() not in valid_tables:
            return None
        
        values = []
        cols, vals = Database.__set_builder(cols)
        values.extend(vals)

        conditions, vals = Database.__conditions_builder(conditions)
        values.extend(vals)
        values = tuple(values)

        statement = f"UPDATE {table} SET {cols} {conditions}".strip().upper()
        self.__conn.execute(statement, values)

    def __convert_row(self, row: dict, obj_type):
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
                        has_read=bool(row["has_read"])
                    )
                elif obj_type == Meta:
                    converted_row = Meta(
                        authors=row["authors"].split(", "),
                        genres=row["genres"].split(", "),
                        rating=row["rating"],
                        release_date=row["release_date"],
                        status=identify_status(row["status"]),
                        description=row["description"],
                    )
            except Exception as ex:
                raise ex
        return converted_row

    def __convert_rows(self, rows: [dict], convert_type):
        converted_rows = []
        if rows:
            for row in rows:
                converted_row = self.__convert_row(row, convert_type)
                if converted_row:
                    converted_rows.append(converted_row)
        return converted_rows
        
    # create functions
    def create_novels_table(self):
        statement = """CREATE TABLE IF NOT EXISTS NOVELS(
            URL TEXT PRIMARY KEY UNIQUE,
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
            HAS_READ INTEGER,
            FOREIGN KEY (NOVEL_URL)
                REFERENCES NOVELS (URL));
        """
        self.__conn.execute(statement)

    def create_metas_table(self):
        statement = """CREATE TABLE IF NOT EXISTS METAS(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            AUTHORS TEXT,
            GENRES TEXT,
            RATING TEXT,
            RELEASE_DATE TEXT,
            STATUS TEXT,
            DESCRIPTION TEXT,
            NOVEL_URL TEXT UNIQUE NOT NULL,
            FOREIGN KEY (NOVEL_URL)
                REFERENCES NOVELS (URL));
        """
        self.__conn.execute(statement)

    # insert functions
    def insert_novel(self, novel: Novel):
        statement = """INSERT INTO NOVELS (URL, TITLE, THUMBNAIL) VALUES (?, ?, ?);"""
        self.__conn.execute(statement, (novel.url, novel.title, novel.thumbnail))

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

    def update_chapter(self, chapter: Chapter):
        """Update cols of selected chapter whose col URL is `url`"""
        self.__update(
            "chapters",
            [("content", chapter.content)],
            [("url", chapter.url)]
        )
    
    def update_meta(self, meta: Meta):
        self.__update(
            "metas",
            [("status", meta.status.name)],
            [("novel_url", meta.novel_url)]
        )

    def select_novels(self) -> [Novel]:
        cur = self.__select("novels")
        novel_rows = cur.fetchall()
        # novel_rows = self.__conn.execute("""SELECT * FROM NOVELS""").fetchall()
        novels = self.__convert_rows(novel_rows, Novel)
        return novels

    def select_novel(self, novel_url) -> Novel:
        cur = self.__select("novels", conditions=[("url", novel_url)])
        novel_row = cur.fetchone()
        novel = self.__convert_row(novel_row, Novel)
        return novel

    def select_chapters(self, novel_url: str) -> [Chapter]:
        cur = self.__select("chapters", conditions=("novel_url", novel_url))
        chapter_rows = cur.fetchall()
        chapters = self.__convert_rows(chapter_rows, Chapter)
        return chapters

    def select_chapter(self, chapter_url: str) -> Chapter:
        cur = self.__select("chapters", conditions=("url", chapter_url))
        chapter_row = cur.fetchone()
        chapter = self.__convert_row(chapter_row, Chapter)
        return chapter

    def select_metas(self) -> [Meta]:
        cur = self.__select("metas")
        meta_rows = cur.fetchall()
        metas = self.__convert_rows(meta_rows, Meta)
        return metas

    def select_meta(self, novel_url) -> Meta:
        cur = self.__select("metas", conditions=("novel_url", novel_url))
        meta_row = cur.fetchone()
        meta = self.__convert_row(meta_row, Meta)
        return meta
