from bs4 import BeautifulSoup
import os
import re
import requests
from typing import Tuple

from downloader import Downloader


class Xsnvshen(Downloader):
    def __init__(self, urls: dict, output: str, log: str) -> None:
        super().__init__(output, log)
        self.model_urls = urls['model']
        self.album_urls = urls['album']
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36', 
            'Referer': 'https://www.xsnvshen.com/album/{}'
        }
        self.__xsnvshen()

    def __xsnvshen(self) -> None:
        for model_url in self.model_urls:
            print(f'\n[INFO]: Processing Xsnvshen model URL {model_url} ...\n')
            model_name, album_ids = self.__get_albums_from_model(model_url)
            if model_name == '' or len(album_ids) == 0:
                continue
            print(f'\n[INFO]: Total {len(album_ids)} Xsnvshen albums are found ...\n')

            dir_name = self._get_valid_name(model_name)
            dir_path = os.path.join(self.output, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            for i in range(len(album_ids)):
                images, album_name, _ = self.__get_images_from_album(album_ids[i])
                if len(images) == 0 or album_name == '':
                    continue

                album_path = os.path.join(dir_path, album_name)
                if not os.path.exists(album_path):
                    os.makedirs(album_path)

                if self._is_duplicated(album_path, len(images)):
                    self._add_error_msg(f'[WARN]: Xsnvshen album {album_path} is duplicated, skip.')
                    continue

                print(f'\n\n[INFO]: Downloading images from Xsnvshen model {model_name} album {album_name} ...\n')
                self.headers['Referer'] = self.headers['Referer'].format(album_ids[i])
                self._download_srcs(images, album_path, 'Xsnvshen ', self.headers)

        for album_url in self.album_urls:
            print(f'\n[INFO]: Processing Xsnvshen album URL {album_url} ...\n')
            album_id = self.__get_album_id(album_url)
            if album_id == '':
                continue

            images, album_name, model_id = self.__get_images_from_album(album_id)
            if len(images) == 0 or album_name == '':
                continue

            model_name = self.__get_model_name_from_id(model_id)
            if model_name == '':
                continue
            
            dir_name = self._get_valid_name(model_name)
            album_path = os.path.join(self.output, dir_name, album_name)
            if not os.path.exists(album_path):
                os.makedirs(album_path)

            if self._is_duplicated(album_path, len(images)):
                self._add_error_msg(f'[WARN]: Xsnvshen album {album_path} is duplicated, skip.')
                continue

            print(f'\n\n[INFO]: Downloading images from Xsnvshen album {album_name} ...\n')
            self.headers['Referer'] = self.headers['Referer'].format(album_id)
            self._download_srcs(images, album_path, 'Xsnvshen', self.headers)

        self._write_log()

    def __get_albums_from_model(self, url: str) -> Tuple[str, list]:
        html = requests.get(url)
        if html.status_code != requests.codes.ok:
            self._add_error_msg(f'[ERR]: Failed to get Xsnvshen model URL {url} (status code: {html.status_code}).')
            return '', []
        soup = BeautifulSoup(html.text, 'lxml')
        model_name_1 = soup.select('.entry-baseInfo-bd > ul > li:nth-child(1) > span')[1].text.strip()
        model_name_2 = soup.select('.entry-baseInfo-bd > ul > li:nth-child(2) > span')[1].text.strip()
        model_name = f'{model_name_1} ({model_name_2})'

        albums = soup.select('.star-mod-bd > ul > li > a')
        album_ids = list()
        for album in albums:
            album_id = self.__get_album_id(album['href'])
            if album_id != '':
                album_ids.append(album_id)
        return model_name, album_ids

    def __get_album_id(self, url: str) -> str:
        P_ALBUM = r'.*/album/(.*)$'
        match = re.match(P_ALBUM, url, re.M|re.I)
        if match:
            return match.group(1)
        else:
            self._add_error_msg(f'[ERR]: Failed to parse Xsnvshen album URL {url}.')
            return ''
        
    def __get_images_from_album(self, album_id: str) -> Tuple[list, str, str]:
        URL_ALBUM = 'https://www.xsnvshen.com/album/{}'
        URL_IMAGE = 'https://img.xsnvshen.com/album/{}/{}/{:0>3d}.jpg'

        url = URL_ALBUM.format(album_id)
        html = requests.get(url)
        if html.status_code != requests.codes.ok:
            self._add_error_msg(f'[ERR]: Failed to get Xsnvshen album URL {url} (status code: {html.status_code}).')
            return [], ''
        soup = BeautifulSoup(html.text, 'lxml')
        album_name = soup.select('.swp-tit.layout > h1 > a')[0].text.strip()
        span_image_num = soup.select('#time > span')[0].text
        image_num = int(''.join([c for c in span_image_num if c.isdigit()]))
        first_image = soup.select('.workShow > ul > li > img')[0]['src'].strip()

        model_id = self.__get_model_id_from_image(first_image)
        if model_id == '':
            return [], ''

        return [[URL_IMAGE.format(model_id, album_id, i), f'{i}.jpg'] for i in range(image_num)], album_name, model_id

    def __get_model_id_from_image(self, url: str) -> str:
        P_IMAGE = r'//img.xsnvshen.com/album/(.*)/(.*)/(.*).jpg'

        match = re.match(P_IMAGE, url, re.M|re.I)
        if match:
            return match.group(1)
        else:
            return ''

    def __get_model_name_from_id(self, model_id: str) -> str:
        URL_MODEL = 'https://www.xsnvshen.com/girl/{}'

        url = URL_MODEL.format(model_id)
        html = requests.get(url)
        if html.status_code != requests.codes.ok:
            self._add_error_msg(f'[ERR]: Failed to get Xsnvshen model URL {url} (status code: {html.status_code}).')
            return ''
        soup = BeautifulSoup(html.text, 'lxml')
        model_name_1 = soup.select('.entry-baseInfo-bd > ul > li:nth-child(1) > span')[1].text.strip()
        model_name_2 = soup.select('.entry-baseInfo-bd > ul > li:nth-child(2) > span')[1].text.strip()
        return f'{model_name_1} ({model_name_2})'
