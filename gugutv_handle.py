from collections import OrderedDict
import requests, json, re
from flask import Response
from support import d, default_headers, logger
from tool import ToolUtil

from .setup import P


class Gugutv:

    _url = "https://lifetv365.com"

    @classmethod
    def ch_list(cls):
        response = requests.post(
            f"{cls._url}/new/ajax/get_media_list_ajax.php",
            data={'ca': 0},
            headers={"referer":f"{cls._url}"}
        ).json()
       
        channels = []
        sport_categories = {
            '1': 'soccer',
            '2': 'basketball',
            '3': 'volleyball',
            '4': 'baseball',
            '5': 'hockey',
            '6': 'football',
            '7': 'lol',
            '8': 'egame',
            '9': 'hd',
            '10': 'ufc',
            '11': 'tennis'
        }

        filterlist = list(filter(lambda x: x['onoff'] == 'on', response))

        for x in filterlist:
            item = {
                "type": "sports",
                "id": x["ch"],
                "name": x["title"],
                "time": x["time"],
                "category": sport_categories.get(x["ca"], None),
                "logo": f"{cls._url}/sites/gugutv/assets/images/events/{x['ca']}.png"
            }
            channels.append(item)

        return channels
        
    
    @classmethod
    def get_m3u8(cls, ch_id, ch_title):
        response = requests.get(
            f"{cls._url}/sites/gugutv/pages/pc/pc_view.php?ch={ch_id}&title={ch_title}",
            headers={"referer":f"{cls._url}/sites/gugutv/index.php?tg=1ch&ca=0"}
        ).content.decode('UTF-8')
        
        url_match = re.search(r'file:\s+"(https?://.*?)"', response)
        if url_match:
            return 'redirect', url_match.group(1)
        else:
            return None, None
    

    @classmethod
    def make_m3u(cls):
        M3U_FORMAT = '#EXTINF:-1 tvg-id=\"{id}\" tvg-name=\"{title}\" tvg-logo=\"{logo}\" group-title=\"{group}\" tvg-chno=\"{ch_no}\" tvh-chnum=\"{ch_no}\",{title}\n{url}\n' 
        m3u = '#EXTM3U\n'
        for idx, item in enumerate(cls.ch_list()):
            m3u += M3U_FORMAT.format(
                id=item['id'],
                title=f"{item['name']}",
                group=item['type'],
                ch_no=str(idx+1),
                url=ToolUtil.make_apikey_url(f"/{P.package_name}/api/url.m3u8?ch_id={item['id']}&ch_title={item['name']}"),
                logo= item['logo'],
            )
        return m3u