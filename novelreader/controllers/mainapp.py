from kivy.app import App, Builder
from kivy.core.window import Window
from kivy.config import Config
from novelreader.repository import Repository
from novelreader.services import Services
from novelreader.models import Database
from novelreader.controllers.pages import PageManager
from pathlib import Path
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
        database = Database.build(str(Path("novelreader", "public", "novels.db")))

        # create repository
        repository = Repository.build(services, database)

        # create tables
        repository.create_novels_table()
        repository.create_chapters_table()
        repository.create_metas_table()

        # initialize page
        self.root.get_screen("library_page").on_start(repository)
        self.root.get_screen("info_page").on_start(repository)
        self.root.get_screen("search_page").on_start(repository)

    def check_resize(self, instance, x, y):
        # resize X
        print(Window.size)
        if x > 840 or x < 840:
            Window.size = (840, Window.size[1])  # 840, 640
        # resize Y
        if y > 640 or y < 640:
            Window.size = (Window.size[0], 640)  # 840, 640
