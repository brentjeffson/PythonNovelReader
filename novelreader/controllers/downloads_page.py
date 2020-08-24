from . import Builder, Screen
from . import ObjectProperty, StringProperty, NumericProperty
from . import BoxLayout
from . import RecycleView
from . import Path

Builder.load_file(str(Path('novelreader/views/downloads_page.kv').absolute()))

class DownloadsPage(Screen):
    """Page containing downloads in progress"""
    downloads_list = ObjectProperty()

class DownloadItem(BoxLayout):
    """RecycleView Item"""
    novel = ObjectProperty()
    downloaded = NumericProperty()
    download = ObjectProperty()

    def __init__(self, **kwargs):
        super(DownloadItem, self).__init__(**kwargs)
        pass
        self.download = Downloader(self.novel.url)

    def resume(self):
        pass
        if not self.download.is_running:
            self.download.start()

    def pause(self):
        pass
        if self.download.is_running:
            self.download.pause()
