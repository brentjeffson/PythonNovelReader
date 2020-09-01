from kivy.app import App, Builder
from kivy.core.window import Window
from novelreader.controllers.pages import PageManager
from kivy.config import Config
from pathlib import Path
from novelreader.models import Database
import sqlite3 as sql
import requests

Window.size = (840, 640)
pages_manager = Builder.load_file(str(Path("novelreader/views/pages.kv").absolute()))

class MainApp(App):

    def build(self):
        Window.bind(on_resize=self.check_resize)
        return pages_manager

    def on_start(self):
        # create services instance
        session = requests.Session()
        services = Services.build(session)

        # create database instance
        db = Database(Path("novelreader", "public", "novels.db"))
        db.conn.row_factory = sql.Row

        # create repository
        repository = Repository.build(db, services)

        # create tables
        repository.create_novels_table()
        repository.create_chapters_table()
        repository.create_metas_table()

        # initialize page
        self.root.get_screen("library_page").on_start(repository)
        self.root.get_screen("info_page").on_start(repository)
        
    def check_resize(self, instance, x, y):
        # resize X
        print(Window.size)
        if x > 840 or x < 840:
            Window.size = (840, Window.size[1])  # 840, 640
        # resize Y
        if y > 640 or y < 640:
            Window.size = (Window.size[0], 640)  # 840, 640
