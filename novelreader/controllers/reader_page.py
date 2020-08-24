from . import Builder, Screen
from . import Path

Builder.load_file(str(Path('novelreader/views/reader_page.kv').absolute()))

class ReaderPage(Screen):
    """Show chapter content of novel"""