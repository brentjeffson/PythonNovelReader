from kivy.app import App, Builder
from kivy.core.window import Window
from novelreader.controllers.pages import PageManager
from kivy.config import Config

Window.size = (840, 640)
pages_manager = Builder.load_file("../views/pages.kv")

class MainApp(App):

    def build(self):
        Window.bind(on_resize=self.check_resize)
        return pages_manager
        
    def check_resize(self, instance, x, y):
        # resize X
        print(Window.size)
        if x > 840 or x < 840:
            Window.size = (840, Window.size[1])  # 840, 640
        # resize Y
        if y > 640 or y < 640:
            Window.size = (Window.size[0], 640)  # 840, 640


if __name__ == "__main__":
    app = MainApp()
    app.title = 'Novel Reader'
    app.run()
    
