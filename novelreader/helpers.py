from pathlib import Path
from enum import Enum

class DefaultButtonColor(Enum):
    PRIMARY_DEFAULT =  0.1725, 0.2431, 0.3137, 1
    PRIMARY_ACTIVE = 0.8274, 0.3294, 0.0, 1
    PRIMARY_HOVER = (1, 1, 1, 1)
    PRIMARY_CLICKED = (1, 1, 1, 1)
    SECONDARY_DEFAULT = 0.7411, 0.7647, 0.7803, 1

def show(funct):
    def inner(*args, **kwargs):
        res = funct(*args, **kwargs)
        print("="*len(str(res)))
        plog(["args"], args)
        plog(["kwargs"], args)
        print(res)
        print("="*len(str(res)))
        return res
    return inner

def plog(title, msg=''):
    title = ''.join([f"[{i.upper()}]" for i in title])
    print(f'{title} {str(msg)}')


def thumbnail_path(url: str):
    """Create a path to thumbnail using URL"""
    thumbnail_path = Path(
        "novelreader", 
        "public", 
        "imgs", 
        url.split("/")[-1]
    ).absolute()
    return thumbnail_path