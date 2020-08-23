from kivy.app import Builder
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView


def plog(title, msg=''):
    title = ''.join([f"[{i.upper()}]" for i in title])
    print(f'{title} {msg}')