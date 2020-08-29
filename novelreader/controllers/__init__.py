from kivy.app import Builder
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

from pathlib import Path
import aiohttp
import asyncio

SESSION = None
IO_LOOP = None

def get_session():
    global SESSION
    if SESSION is None:
        SESSION = aiohttp.ClientSession()
    return SESSION

async def close_session():
    global SESSION
    await SESSION.close()

def get_loop():
    global IO_LOOP
    if IO_LOOP is None:
        IO_LOOP = asyncio.get_event_loop()
    return IO_LOOP


def plog(title, msg=''):
    title = ''.join([f"[{i.upper()}]" for i in title])
    print(f'{title} {str(msg)}')



# load all design files
# for path in Path('../views').glob('*.kv'):
#     plog(['KV'], path)
#     Builder.load_file(str(path))

