from collections import OrderedDict
import requests, json, re
from flask import Response
from support import d, default_headers, logger
from tool import ToolUtil

from .setup import P


class Gugutv:

    _url = "https://lifetv365.com"

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

    @classmethod
    def ch_list(cls):
        channels = []
        url = cls._url

        html_code = requests.get(f"{url}/sites/gugutv/index.php?tg=1ch&ca=0", headers={"referer": url}).text

        sport_table_html = re.search(
            r'<div id="sports" class="tabcontent".*?<section class="sport_channel_wrap2".*?>(.*?)<\/section>\s*<\/div>',
            html_code, re.DOTALL).group(1)

        if sport_table_html:
            rows = re.findall(r'<tr class="cate_\d+".*?</tr>', sport_table_html, re.DOTALL)
            for row in rows:
                row_data = re.findall(r'<td.*?>(.*?)</td>', row, re.DOTALL)
                status = re.search(re.compile(r'<li class="channel_on .*? data-title="(.*?)">', re.IGNORECASE),
                                   str(row_data[4]))

                if status:
                    img = re.search(r'<img.*?src="./assets/images/events/(.*?).png.*?".*?>', row_data[0]).group(1)
                    channel_id = row_data[1].strip()
                    time = row_data[2].strip()
                    name = re.sub(r'<.*?>', '', row_data[3]).strip()

                    channel = {
                        "source": "GUGUTV",
                        "source_name":"구구TV",
                        "type": "SPORTS",
                        'category': cls.sport_categories.get(img, None),
                        'time': time,
                        "channel_id": channel_id,
                        'name': name,
                        "current": None,
                        "url": None,
                        "icon": f"{url}/sites/gugutv/assets/images/events/{img}.png",
                    }
                    channels.append(channel)

        


        bet365_table_html = re.search(r'<div id="bet365" class="tabcontent".*?<table.*?>.*?<\/table>', html_code,
                                     re.DOTALL).group(0)

        if bet365_table_html:
            channel_regex = r'<tr style="display: table-row;">.*?<img.*?src="(.*?)".*?<td>(.*?)<\/td>.*?data-m3u8="(.*?)".*?<\/tr>'
            matches = re.findall(channel_regex, bet365_table_html, re.DOTALL)

            for match in matches:
                icon, name, m3u8_url = match
                channel = {
                    "source": "GUGUTV",
                    "source_name": "구구TV",
                    "type": "BETFAIR",
                    'category': None,
                    'time': None,
                    "channel_id": None,
                    "name": name.strip(),
                    "current": None,
                    "url": m3u8_url,
                    "icon": icon.replace("./assets", f"{url}/sites/gugutv/assets"),
                }
                channels.append(channel)
       
    
        live_table_html = re.search(r'<div id="livetv" class="tabcontent".*?<table.*?>.*?<\/table>', html_code,
                                    re.DOTALL).group(0)

        if live_table_html:
            channel_regex = r'<li class="live_channel_list_item horizon_block">\s*<a class="ch1_select" data-stream="(\w+)" data-title="([^"]+)">\s*<img src="([^"]+)" alt="[^"]+">\s*</a>\s*</li>'
            matches = re.findall(channel_regex, live_table_html, re.DOTALL)

            for match in matches:
                channel_id, name, icon = match
                channel = {
                    "source": "GUGUTV",
                    "source_name": "구구TV",
                    "type": "LIVETV",
                    'category': None,
                    'time': None,
                    "channel_id": channel_id,
                    "name": name,
                    "current": None,
                    "url": None,
                    "icon": icon.replace("./assets", f"{url}/sites/gugutv/assets"),
                }
                channels.append(channel)

        live2_table_html = re.search(r'<div id="livetv2" class="tabcontent".*?<table.*?>.*?<\/table>', html_code,
                                     re.DOTALL).group(0)

        if live2_table_html:
            channel_regex = r'<tr style="display: table-row;">.*?<img.*?src="(.*?)".*?<td>(.*?)<\/td>.*?data-m3u8="(.*?)".*?<\/tr>'
            matches = re.findall(channel_regex, live2_table_html, re.DOTALL)

            for match in matches:
                icon, name, m3u8_url = match
                channel = {
                    "source": "GUGUTV",
                    "source_name": "구구TV",
                    "type": "LIVETV2",
                    'category': None,
                    'time': None,
                    "channel_id": None,
                    "name": name.strip(),
                    "current": None,
                    "url": m3u8_url,
                    "icon": icon.replace("./assets", f"{url}/sites/gugutv/assets"),
                }
                channels.append(channel)

        return channels
    
    @classmethod
    def get_m3u8(cls, ch_id, ch_title):
        url = f"{cls._url}/sites/gugutv/pages/pc/pc_view.php?ch={ch_id}&title={ch_title}"
        headers = {"referer": f"{cls._url}/sites/gugutv/index.php?tg=1ch&ca=0"}

        response = requests.get(url, headers=headers).content.decode('UTF-8')

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
            if item['type'] in ['SPORTS', 'LIVETV']:
                m3u += M3U_FORMAT.format(
                    id=item['channel_id'],
                    title=f"{item['name']}",
                    group=item['type'],
                    ch_no=str(idx+1),
                    url=ToolUtil.make_apikey_url(f"/{P.package_name}/api/url.m3u8?ch_id={item['channel_id']}&ch_title={item['name']}"),
                    logo=item['icon'],
                )
            elif item['type'] in ['BETFAIR', 'LIVETV2']:
                m3u += M3U_FORMAT.format(
                    id=item['name'],
                    title=f"{item['name']}",
                    group=item['type'],
                    ch_no=str(idx+1),
                    url=item['url'],
                    logo=item['icon'],
                )
        return m3u