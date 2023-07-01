import requests
import yaml
import time
from datetime import datetime
import os

import requests
import yaml

# Plex 서버의 주소와 토큰을 설정합니다.
plex_server_url = 'http://localhost:32400'
plex_token = ''

# YAML 파일의 URL과 로컬에 저장할 경로를 설정합니다.
yaml_url = ''
local_path = ''

# PLEX 메타아이템
meta_item = '563908'

def main():
    while True:
        try:
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
                    print('데이터가 변경되어 로컬에 저장되었습니다.')

                # Plex 메타 데이터를 새로고침합니다.
                plex_refresh_by_item(meta_item)
            else:
                print('데이터가 동일합니다.')

            # 5분간 대기합니다.
            time.sleep(300)

        except requests.exceptions.RequestException as e:
            print('YAML 파일을 가져오는 도중 오류가 발생했습니다:', str(e))

        except yaml.YAMLError as e:
            print('YAML 파일을 처리하는 도중 오류가 발생했습니다:', str(e))

        except Exception as e:
            print('오류가 발생했습니다:', str(e))

def plex_refresh_by_item(item_id):
    try:
        url = f"{plex_server_url}/library/metadata/{item_id}/refresh?X-Plex-Token={plex_token}"
        ret = requests.put(url)
        ret.raise_for_status()

        print('Plex 메타 데이터 새로고침이 성공적으로 시작되었습니다.')
    except requests.exceptions.RequestException as e:
        print('Plex 메타 데이터 요청 중 오류가 발생했습니다:', str(e))
    except Exception as e:
        print('Plex 메타 데이터 새로고침 중 오류가 발생했습니다:', str(e))


if __name__ == '__main__':
    main()