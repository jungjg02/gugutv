from collections import OrderedDict
import requests, json, re
from flask import Response
from datetime import datetime
import os
import yaml
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

        if P.ModelSetting.get_bool('main_use_sports') :
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

        if P.ModelSetting.get_bool('main_use_betfair') :
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
       
        if P.ModelSetting.get_bool('main_use_livetv') :
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

        if P.ModelSetting.get_bool('main_use_livetv2') :
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
    def get_m3u8(cls, ch_id):
        url = f"{cls._url}/sites/gugutv/pages/pc/pc_view.php?ch={ch_id}"
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
                    url=ToolUtil.make_apikey_url(f"/{P.package_name}/api/url.m3u8?ch_id={item['channel_id']}"),
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
    
    @classmethod
    def make_yaml(cls):
        
        data = {
            'primary': True,
            'code': "gugutv",
            'title': "[GUGUTV]",
            'year': 2023,
            'genres': "Live",
            'posters': 'https://cdn.discordapp.com/attachments/877784202651787316/1124610187181953094/gugutv.png',
            'summary': "",
            'extras':[]
        }
        for idx, item in enumerate(cls.ch_list()):
            if item['type'] in ['SPORTS', 'LIVETV']:
                data['extras'].append({
                'mode': "m3u8",
                'type': 'featurette',
                'param': ToolUtil.make_apikey_url(f"/{P.package_name}/api/url.m3u8?ch_id={item['channel_id']}"),
                'title': item['name'],
                'thumb': item['icon']
                })
            elif item['type'] in ['BETFAIR', 'LIVETV2']:
                data['extras'].append({
                'mode': 'm3u8',
                'type': 'featurette',
                'param': item['url'],
                'title': item['name'],
                'thumb': item['icon']
                })
            

        yaml_data = yaml.dump(data, allow_unicode=True, sort_keys=False, encoding='utf-8')
        return yaml_data
    
    @classmethod
    def plex_refresh_by_item(cls, item_id):
        try:
            plex_server_url = P.ModelSetting.get('main_plex_server_url')
            plex_token = P.ModelSetting.get('main_plex_token')

            url = f"{plex_server_url}/library/metadata/{item_id}/refresh?X-Plex-Token={plex_token}"
            ret = requests.put(url)
            ret.raise_for_status()

            P.logger.debug('Plex 메타 데이터 새로고침이 성공적으로 시작되었습니다.')
        except requests.exceptions.RequestException as e:
            P.logger.error(f'requests.exceptions.RequestException:{str(e)}')
        except Exception as e:
            P.logger.error(f'Exception:{str(e)}')

    
    @classmethod
    def sync_yaml_data(cls):
        try:
            yaml_url = ToolUtil.make_apikey_url(f"/{P.package_name}/api/yaml")
            local_path = P.ModelSetting.get('main_yaml_path')
            meta_item = P.ModelSetting.get('main_plex_meta_item')

            # YAML 파일을 가져와 이전 데이터를 로드합니다.
            response = requests.get(yaml_url)
            new_data = yaml.safe_load(response.content)
            previous_data = yaml.safe_load(open(local_path, encoding='utf-8')) if os.path.exists(local_path) else None

            # extras 만 가져와서 비교합니다.
            new_data_extras_data = new_data['extras']
            previous_extras_data = previous_data['extras']

            # 이전 데이터와 새 데이터를 비교합니다.
            if previous_extras_data is not None and previous_extras_data != new_data_extras_data:
                # 데이터가 변경된 경우, 로컬에 저장합니다.
                updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_data['summary'] = f"마지막 업데이트 시간 : {updated_at}"

                with open(local_path, 'w', encoding='utf-8') as file:
                    yaml.dump(new_data, file, allow_unicode=True, sort_keys=False, encoding='utf-8')
                    P.logger.debug('데이터가 변경되어 로컬에 저장되었습니다.')

                # Plex 메타 데이터를 새로고침합니다.
                cls.plex_refresh_by_item(meta_item)

        except requests.exceptions.RequestException as e:
            P.logger.error(f'requests.exceptions.RequestException:{str(e)}')
        except yaml.YAMLError as e:
            P.logger.error(f'yaml.YAMLError:{str(e)}')
        except Exception as e:
            P.logger.error(f'Exception:{str(e)}')


    
