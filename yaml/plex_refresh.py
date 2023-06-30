import requests
import yaml
import time
import os

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

            # 이전 데이터와 새 데이터를 비교합니다.
            if previous_data is not None and previous_data != new_data:
                # 데이터가 변경된 경우, 로컬에 저장합니다.
                with open(local_path, 'w', encoding='utf-8') as file:
                    yaml.dump(new_data, file, allow_unicode=True, sort_keys=False, encoding='utf-8')
                    print('데이터가 변경되어 로컬에 저장되었습니다.')

                # Plex 메타 데이터를 새로고침합니다.
                plex_refresh_by_item(meta_item)
            else:
                print('데이터가 동일합니다.')

            # 이전 데이터를 업데이트합니다.
            previous_data = new_data

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

        if ret.status_code != 200:
            print('Plex 메타 데이터 오류가 발생했습니다.')
        else:
            print('Plex 메타 데이터 새로고침이 성공적으로 시작되었습니다.')

    except Exception as e:
        print('오류가 발생했습니다:', str(e))


if __name__ == '__main__':
    main()