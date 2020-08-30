from novelreader.controllers.mainapp import MainApp
import sqlite3 as sql
from pathlib import Path

if __name__ == "__main__":
    # create tables
    db = None
    try:
        db = sql.connect(Path("novelreader", "public", "novel.db").absolute())
        dbc = db.cursor()
        dbc.execute("""CREATE TABLE IF NOT EXISTS NOVELS(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            URL TEXT UNIQUE NOT NULL,
            TITLE TEXT NOT NULL
        );
        """)
        dbc.execute("""CREATE TABLE IF NOT EXISTS METAS(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            AUTHORS TEXT,
            GENRES TEXT,
            RATING REAL,
            RELEASE_DATE TEXT,
            STATUS TEXT,
            DESCRIPTION TEXT,
            NOVEL_URL TEXT UNIQUE NOT NULL,
            FOREIGN KEY (NOVEL_URL)
                REFERENCES NOVELS (URL)
        );
        """)
        dbc.execute("""CREATE TABLE IF NOT EXISTS CHAPTERS(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CHAPTER_ID REAL NOT NULL,
            URL TEXT UNIQUE NOT NULL,
            TITLE TEXT NOT NULL,
            CONTENT TEXT,
            NOVEL_URL TEXT UNIQUE NOT NULL,
            FOREIGN KEY (NOVEL_URL)
                REFERENCES NOVELS (URL)
        );
        """)
        db.commit()
    except Exception as ex:
        print(ex)
    finally:
        db.close()

    app = MainApp()
    app.title = 'Novel Reader'
    app.run()