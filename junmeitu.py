from bs4 import BeautifulSoup
import json
import os
import re
import requests
from tqdm.auto import tqdm
from typing import Tuple

from downloader import Downloader


class Junmeitu(Downloader):
    def __init__(self, urls: dict, output: str, log: str) -> None:
        super().__init__(output, log)
        self.model_urls = urls['model']
        self.album_urls = urls['album']
        self.__junmeitu()

    def __junmeitu(self) -> None:
        for model_url in self.model_urls:
            print(f'\n[INFO]: Processing Junmeitu model URL {model_url} ...\n')
            model_name, album_ids = self.__get_albums_from_model(model_url)
            if model_name == '' or len(album_ids) == 0:
                continue
            print(f'\n[INFO]: Total {len(album_ids)} Junmeitu albums are found ...\n')

            dir_name = self._get_valid_name(model_name)
            dir_path = os.path.join(self.output, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            for i in range(len(album_ids)):
                images, album_name = self.__get_images_from_album(album_ids[i])
                if len(images) == 0 or album_name == '':
                    continue

                album_path = os.path.join(dir_path, album_name)
                if not os.path.exists(album_path):
                    os.makedirs(album_path)

                if self._is_duplicated(album_path, len(images)):
                    self._add_error_msg(f'[WARN]: Junmeitu album {album_path} is duplicated, skip.')
                    continue

                print(f'\n[INFO]: Downloading images from Junmeitu model {model_name} album {album_name} ...\n')
                self._download_srcs(images, album_path, 'Junmeitu')

        for album_url in self.album_urls:
            print(f'\n[INFO]: Processing Junmeitu album URL {album_url} ...\n')
            album_id = self.__get_album_id(album_url)
            if album_id == '':
                continue

            images, album_name = self.__get_images_from_album(album_id)
            if len(images) == 0 or album_name == '':
                continue

            model_name = self.__get_model_name(album_url)
            if model_name == '':
                continue

            dir_name = self._get_valid_name(model_name)
            album_path = os.path.join(self.output, dir_name, album_name)
            if not os.path.exists(album_path):
                os.makedirs(album_path)

            if self._is_duplicated(album_path, len(images)):
                self._add_error_msg(f'[WARN]: Junmeitu album {album_path} is duplicated, skip.')
                continue

            print(f'\n[INFO]: Downloading images from Junmeitu album {album_name} ...\n')
            self._download_srcs(images, album_path, 'Junmeitu')

        self._write_log()

    def __get_albums_from_model(self, url: str) -> Tuple[str, list]:
        URL_MODEL = 'https://www.junmeitu.com/model/{}.html'

        html = requests.get(url)
        if html.status_code != requests.codes.ok:
            self._add_error_msg(f'[ERR]: Failed to get Junmeitu model URL {url} (status code: {html.status_code}).')
            return '', []
        soup = BeautifulSoup(html.text, 'lxml')
        model_name = soup.select('.album_info > h1')[0].text.strip()
        albums = soup.select('.pic-list > ul > li > a')
        
        model_id = self.__get_model_id(url)
        if model_id == '':
            return '', []

        album_pages = soup.select('.pages > a')
        album_page_num = 1
        if album_pages and len(album_pages) >= 3: 
            album_page_num = int(album_pages[-2].text.strip())
        for i in range(2, album_page_num + 1):
            albums.extend(self.__get_albums_from_model_page(URL_MODEL.format(f'{model_id}-{i}')))

        album_ids = list()
        for album in albums:
            album_id = self.__get_album_id(album['href'])
            if album_id != '':
                album_ids.append(album_id)
        return model_name, album_ids

    def __get_albums_from_model_page(self, url: str) -> list:
        html = requests.get(url)
        if html.status_code != requests.codes.ok:
            self._add_error_msg(f'[ERR]: Failed to get Junmeitu model URL {url} (status code: {html.status_code}).')
            return []
        soup = BeautifulSoup(html.text, 'lxml')
        
        return soup.select('.pic-list > ul > li > a')

    def __get_album_id(self, url: str) -> str:
        P_ALBUM = r'.*/beauty/(.*).html$'
        match = re.match(P_ALBUM, url, re.M|re.I)
        if match:
            return match.group(1)
        else:
            self._add_error_msg(f'[ERR]: Failed to parse Junmeitu album URL {url}.')
            return ''

    def __get_model_id(self, url: str) -> str:
        P_MODEL_ID = r'.*/model/(.*).html$'
        
        match = re.match(P_MODEL_ID, url, re.M|re.I)
        if match:
            return match.group(1)
        else:
            return ''

    def __get_images_from_album(self, album_id: str) -> Tuple[list, str]:
        URL_ALBUM = 'https://www.junmeitu.com/beauty/{}.html'
        URL_AJAX_IMAGE = 'https://www.junmeitu.com/ajax_beauty/{}-{}.html?ajax=1&catid=6&conid={}'
        P_PC_ID = r'.*pc_id.*?(\d+).*'

        url = URL_ALBUM.format(album_id)
        html = requests.get(url)
        if html.status_code != requests.codes.ok:
            self._add_error_msg(f'[ERR]: Failed to get Junmeitu album URL {url} (status code: {html.status_code}).')
            return [], ''
        soup = BeautifulSoup(html.text, 'lxml')
        album_name = soup.select('.title')[0].text.strip()
        image_num = int(soup.select('.pages > a')[-2].text.strip())
        first_image = soup.select('.pictures > img')[0]['src'].strip()
        html_lines = html.text.split('\n')
        pc_id = -1
        for line in html_lines:
            match = re.match(P_PC_ID, line, re.M|re.I)
            if match:
                pc_id = int(match.group(1))
                break

        if pc_id == -1:
            self._add_error_msg(f'[ERR]: Failed to get Junmeitu album PC_ID from album {url}.')
            return [], ''

        print(f'\n[INFO]: Retrieving images URL from Junmeitu album {album_name} ...\n')
        pbar = tqdm(total=image_num, position=0, leave=True)
        pbar.set_description('Image')
        images = [[first_image, '1.jpg']]
        pbar.update(1)
        for i in range(2, image_num + 1):
            image_ajax = URL_AJAX_IMAGE.format(album_id, i, pc_id)
            ajax = requests.get(image_ajax)
            if ajax.status_code != requests.codes.ok:
                self._add_error_msg(f'[WARN]: Failed to get Junmeitu album URL {url} {i}-th image (status code: {html.status_code}).')
                continue
            json_image = json.loads(ajax.text)
            soup = BeautifulSoup(json_image['pic'], 'lxml')
            image_url = soup.select('img')[0]['src'].strip()
            images.append([image_url, f'{i}.jpg'])

            pbar.update(1)
        pbar.close()

        return images, self._get_valid_name(album_name)

    def __get_model_name(self, url: str) -> str:
        URL_MODEL = 'https://www.junmeitu.com/model/{}.html'

        html = requests.get(url)
        if html.status_code != requests.codes.ok:
            self._add_error_msg(f'[ERR]: Failed to get Junmeitu album URL {url} (status code: {html.status_code}).')
            return ''
        soup = BeautifulSoup(html.text, 'lxml')
        model_url = soup.select('.picture-details > span > a')[0]['href'].strip()
        model_id = self.__get_model_id(model_url)

        url = URL_MODEL.format(model_id)
        html = requests.get(url)
        if html.status_code != requests.codes.ok:
            self._add_error_msg(f'[ERR]: Failed to get Junmeitu model URL {url} (status code: {html.status_code}).')
            return ''
        soup = BeautifulSoup(html.text, 'lxml')
        model_name = soup.select('.album_info > h1')[0].text.strip()

        return model_name
