from kivy.app import App, Builder
from kivy.core.window import Window
from novelreader.controllers.pages import PageManager
from kivy.config import Config
from pathlib import Path
from novelreader.models import Database

Window.size = (840, 640)
pages_manager = Builder.load_file(str(Path("novelreader/views/pages.kv").absolute()))

class MainApp(App):

    def build(self):
        Window.bind(on_resize=self.check_resize)
        return pages_manager

    def on_start(self):
        # create database instance
        db = Database(Path("novelreader", "public", "novels.db"))

        # create tables
        Database.create_novels_table(db.conn)
        Database.create_chapters_table(db.conn)
        Database.create_metas_table(db.conn)

        # initialize page content
        self.root.get_screen("library_page").on_start(db)
        self.root.get_screen("info_page").on_start(db)
        
    def check_resize(self, instance, x, y):
        # resize X
        print(Window.size)
        if x > 840 or x < 840:
            Window.size = (840, Window.size[1])  # 840, 640
        # resize Y
        if y > 640 or y < 640:
            Window.size = (Window.size[0], 640)  # 840, 640
