from . import Screen, Builder
from . import ObjectProperty, StringProperty
from . import Label, Button
from . import plog, Path

import aiohttp
import asyncio

Builder.load_file(str(Path("novelreader/views/search_page.kv").absolute()))

class SearchPage(Screen):
    search_list_recycle = ObjectProperty()
    search_input = ObjectProperty()

    def __init__(self, **kwargs):
        super(SearchPage, self).__init__(**kwargs)

    async def fetch_novels(self, session, payload):
        async with session.post("https://boxnovel.com/wp-admin/admin-ajax.php", data=payload) as resp:
            return await resp.json()
    
    async def prep_fetch(self):
        async with aiohttp.ClientSession() as session:
            payload = {
                "action": "wp-manga-search-manga",
                "title": self.search_input.text
            }
            self.search_list_recycle.data = []
            res = await self.fetch_novels(session, payload)
            print(res['data'])
            data = res["data"]
            if data:
                for item in data:
                    self.search_list_recycle.data.append({"text": item["title"], "url": item["url"]})


    def search(self):
        plog(['searching'], self.search_input.text)
        
        loop = None
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.prep_fetch())
        except Exception as ex:
            plog(["search page", 'exception'], ex.with_traceback(None))
        # 

class SearchItem(Button):
    url = StringProperty()

    def browse(self, url):
        plog(['browsing'], self.text)




