from kivy.app import Builder
from kivy.uix.screenmanager import Screen
from pathlib import Path

Builder.load_file(str(Path('novelreader/views/reader_page.kv')))

class ReaderPage(Screen):
    """Show chapter content of novel"""

    def update_content(self, content):
        self.ids.content.text = content