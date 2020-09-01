from pathlib import Path

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