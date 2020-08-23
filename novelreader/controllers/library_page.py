from . import Builder, Screen
from . import ObjectProperty, StringProperty, BooleanProperty
from . import RecycleView, RecycleGridLayout
from . import RecycleDataViewBehavior, FocusBehavior, LayoutSelectionBehavior
from . import GridLayout, BoxLayout

Builder.load_file('../views/library_page.kv')

# todo library page
class LibraryPage(Screen):
    novellist = ObjectProperty(None)
    bottom_controls = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LibraryPage, self).__init__(**kwargs)

# recyclerview
class NovelList(RecycleView):
    novellist = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(NovelList, self).__init__(**kwargs)
        # self.data = [{} for i in range(12)]
        self.data = [{
            'title': 'Cultivation 1',
            'thumbnail': '../public/imgs/cultivation-chat-group.jpg',
            'is_selected': False
        }]
        # self.data.append({'novel': {'title': 'New Novel', 'thumbnail': '../public/imgs/cultivation-chat-group.jpg'}})

# todo recyclerview behavior
# todo NovelItem
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                     RecycleGridLayout):
        ''' Adds selection and focus behaviour to the view. '''

class NovelItem(RecycleDataViewBehavior, GridLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    novel = ObjectProperty(None)
    title = StringProperty('')
    thumbnail = StringProperty('../public/imgs/cultivation-chat-group.jpg')
    is_selected = BooleanProperty(False)

    # def __init__(self, **kwargs):
    #     super(NovelItem, self).__init__(**kwargs)

    ''' Add selection support to the Label '''
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(NovelItem, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(NovelItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class BottomControlBar(BoxLayout):
    library_btn = ObjectProperty(None)
    search_btn = ObjectProperty(None)
    downloads_btn = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(BottomControlBar, self).__init__(**kwargs)
    
    def print_text(self):
        print(self.library_btn.text)


