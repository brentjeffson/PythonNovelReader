import sqlite3

class Database:
    INSTANCE = None

    @classmethod
    def build(cls, db_file):
        if cls.INSTANCE None:
            instance = Database(db_file)
            cls.INSTANCE = instance
            return instance
        else:
            return cls.INSTANCE
    
    def __init__(self, db_file):
        self.__conn = sqlite3.connect(db_file)
    
    @property
    def conn(self):
        return self.__conn

CREATE_NOVEL_TABLE_STATEMENT = """CREATE TABLE IF NOT EXISTS novel(
	novel_id INTEGER PRIMARY KEY AUTOINCREMENT,
	title TEXT NOT NULL,
	novel_url TEXT NOT NULL UNIQUE
);
"""

CREATE_CHAPTER_TABLE_STATEMENT = """CREATE TABLE IF NOT EXISTS chapter(
    chapter_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    chapter_url TEXT NOT NULL UNIQUE,
    content TEXT,
    FOREIGN KEY (novel_url)
        REFERENCES novel (novel_url)
);
"""

CREATE_META_TABLE_STATEMENT = """CREATE TABLE IF NOT EXISTS meta(
    meta_id INTEGER PRIMARY KEY AUTOINCREMENT,
    authors TEXT,
    genres TEXT,
    rating REAL,
    status TEXT,
    release_data TEXT,
    FOREIGN KEY (novel_url)
        REFERENCES novel (novel_url)
);
"""
    
def create_table(conn, create_statement):
    c = conn.cursor()
    c.execute(create_statement)

# INSERT STATEMENTS
INSERT_NOVEL_STATEMENT = """INSERT INTO novel(title, url)
VALUES(?, ?);
"""

INSERT_CHAPTER_STATEMENT = """INSERT INTO chapter(title, chapter_url, content) VALUES(?, ?, ?)"""

def insert_value(conn, statement, values):
    c = conn.cursor()
    c.execute(statement, values)

