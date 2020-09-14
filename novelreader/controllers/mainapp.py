from kivy.app import App, Builder
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from novelreader.repository import Repository
from novelreader.services import Services
from novelreader.models import Database
from novelreader.controllers.library_page import LibraryPage
from novelreader.controllers.search_page import SearchPage
from novelreader.controllers.downloads_page import DownloadsPage
from novelreader.controllers.reader_page import ReaderPage
from novelreader.controllers.info_page import InfoPage

# from novelreader.controllers.pages import PageManager
from pathlib import Path
import sqlite3 as sql
import requests

Window.size = (840, 640)
Builder.load_file(str(Path("novelreader/views/pages.kv").absolute()))

DEFAULT_PAGE = "library_page"
DEFAULT_COLOR = 0.1725, 0.2431, 0.3137, 1
ON_CLICK_COLOR = 0.8274, 0.3294, 0.0, 1

class MainWindow(BoxLayout):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.page_manager = self.ids.page_manager
        # REFERENCES
        # create reference to pages
        self.library_page = self.page_manager.get_screen("library_page")
        self.info_page = self.page_manager.get_screen("info_page")
        self.search_page = self.page_manager.get_screen("search_page")
        # create reference to bottom navigation
        self.bottom_navigation = self.ids.bottom_navigation
        # END REFERENCES

        # INTIALIZERS
        self.init_bottom_navigation()
        # END INITIALIZERS


    def init_bottom_navigation(self):
         # bind bottom navigation buttons
        self.bottom_navigation.ids.library_btn.bind(on_press=lambda _: self.open_page("library_page"))
        self.bottom_navigation.ids.search_btn.bind(on_press=lambda _: self.open_page("search_page"))
        self.bottom_navigation.ids.downloads_btn.bind(on_press=lambda _: self.open_page("downloads_page"))
        # set default active bottom navigation
        self.bottom_navigation.ids.library_btn.background_color = ON_CLICK_COLOR
        # set button background color
        self.bottom_navigation.ids.library_btn.background_color = DEFAULT_COLOR
        self.bottom_navigation.ids.search_btn.background_color = DEFAULT_COLOR
        self.bottom_navigation.ids.downloads_btn.background_color = DEFAULT_COLOR

    def open_page(self, page_name):
        self.page_manager.current = page_name
        self.bottom_navigation.ids.library_btn.background_color = DEFAULT_COLOR
        self.bottom_navigation.ids.search_btn.background_color = DEFAULT_COLOR
        self.bottom_navigation.ids.downloads_btn.background_color = DEFAULT_COLOR

        if page_name == "library_page":
            self.bottom_navigation.ids.library_btn.background_color = ON_CLICK_COLOR
        elif page_name == "search_page":
            self.bottom_navigation.ids.search_btn.background_color = ON_CLICK_COLOR
        elif page_name == "downloads_page":
            self.bottom_navigation.ids.downloads_btn.background_color = ON_CLICK_COLOR

class MainApp(App):

    def build(self):
        Window.bind(on_resize=self.check_resize)
        return MainWindow()

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

        # initialize pages
        self.root.library_page.on_start(repository)
        self.root.search_page.on_start(repository)
        self.root.info_page.on_start(repository)

    def check_resize(self, instance, x, y):
        # resize X
        print(Window.size)
        if x > 840 or x < 840:
            Window.size = (840, Window.size[1])  # 840, 640
        # resize Y
        if y > 640 or y < 640:
            Window.size = (Window.size[0], 640)  # 840, 640
