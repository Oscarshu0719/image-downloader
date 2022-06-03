from bs4 import BeautifulSoup
import os
import re
import requests
from typing import Tuple

from downloader import Downloader


class KissGoddess(Downloader):
    def __init__(self, urls: dict, output: str, log: str) -> None:
        super().__init__(output, log)
        self.model_urls = urls['model']
        self.album_urls = urls['album']
        self.__kissgoddess()

    def __kissgoddess(self) -> None:
        for model_url in self.model_urls:
            print(f'\n[INFO]: Processing KissGoddess model URL {model_url} ...\n')
            model_name, album_ids = self.__get_albums_from_model(model_url)
            if model_name == '' or len(album_ids) == 0:
                continue
            print(f'\n[INFO]: Total {len(album_ids)} KissGoddess albums are found ...\n')

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
                    self._add_error_msg(f'[WARN]: KissGoddess album {album_path} is duplicated, skip.')
                    continue

                print(f'\n[INFO]: Downloading images from KissGoddess model {model_name} album {album_name} ...\n')
                self._download_srcs(images, album_path, 'KissGoddess')

        for album_url in self.album_urls:
            print(f'\n[INFO]: Processing KissGoddess album URL {album_url} ...\n')
            album_id = self.__get_album_id(album_url)
            if album_id == '':
                continue

            images, album_name = self.__get_images_from_album(album_id)
            if len(images) == 0 or album_name == '':
                continue

            album_path = os.path.join(self.output, album_name)
            if not os.path.exists(album_path):
                os.makedirs(album_path)

            if self._is_duplicated(album_path, len(images)):
                self._add_error_msg(f'[WARN]: KissGoddess album {album_path} is duplicated, skip.')
                continue

            print(f'\n[INFO]: Downloading images from KissGoddess album {album_name} ...\n')
            self._download_srcs(images, album_path, 'KissGoddess ')

        self._write_log()

    def __get_albums_from_model(self, url: str) -> Tuple[str, list]:
        html = requests.get(url)
        if html.status_code != requests.codes.ok:
            self._add_error_msg(f'[ERR]: Failed to get KissGoddess model URL {url} (status code: {html.status_code}).')
            return '', []
        soup = BeautifulSoup(html.text, 'lxml')
        model_name = soup.select('.person-name')[0].text.strip()

        albums = soup.select('.td-module-thumb > a')
        first_album = soup.select('.td-module-thumb > a > img')[0]['data-original'].strip()
        if len(albums) >= 10:
            more_albums, model_id = self.__get_more_albums(url, first_album)
            if len(more_albums) == 0 or model_id == '':
                return '', []

            albums.extend(more_albums)

        album_ids = list()
        for album in albums:
            album_id = self.__get_album_id(album['href'])
            if album_id != '':
                album_ids.append(album_id)
        return model_name, album_ids

    def __get_more_albums(self, url: str, first_album_url: str) -> Tuple[list, str]:
        P_IMAGE = r'^https://pic.kissgoddess.com/gallery/(.*)/(.*)/cover/0.jpg$'
        AJAX_MORE_ALBUMS = 'https://tw.kissgoddess.com/ajax/person_album_handle.ashx?id={}'

        match = re.match(P_IMAGE, first_album_url, re.M|re.I)
        if match:
            model_id = match.group(1)
        else:
            return [], ''

        url = AJAX_MORE_ALBUMS.format(model_id)
        html = requests.get(url)
        if html.status_code != requests.codes.ok:
            self._add_error_msg(f'[ERR]: Failed to get KissGoddess more album from URL {url} (status code: {html.status_code}).')
            return [], ''
        soup = BeautifulSoup(html.text, 'lxml')
        albums = soup.select('.td-module-thumb > a')

        return albums, model_id

    def __get_album_id(self, url: str) -> str:
        P_ALBUM = r'.*/album/(\d+).html$'
        match = re.match(P_ALBUM, url, re.M|re.I)
        if match:
            return match.group(1)
        else:
            self._add_error_msg(f'[ERR]: Failed to parse KissGoddess album URL {url}.')
            return ''

    def __get_images_from_album(self, album_id: str) -> Tuple[list, str]:
        URL_ALBUM = 'http://tw.kissgoddess.com/album/{}.html'
        URL_FIRST_IMAGE = 'https://pic.kissgoddess.com/gallery/{}/{}/s/0.jpg'
        URL_IMAGE = 'https://pic.kissgoddess.com/gallery/{}/{}/s/{:0>3d}.jpg'
        P_LAST_IMAGE = r'^https://pic.kissgoddess.com/gallery/(\d+)/{}/s/(.*).jpg$'

        url = URL_ALBUM.format(album_id)
        html = requests.get(url)
        if html.status_code != requests.codes.ok:
            self._add_error_msg(f'[ERR]: Failed to get KissGoddess album URL {url} (status code: {html.status_code}).')
            return [], ''
        soup = BeautifulSoup(html.text, 'lxml')
        album_name = soup.select('.entry-title')[0].text.strip()
        page_num = int(soup.select('#pages > span')[1].text[-1])

        last_page_url = URL_ALBUM.format(f'{album_id}_{page_num}')
        html = requests.get(last_page_url)
        if html.status_code != requests.codes.ok:
            self._add_error_msg(f'[ERR]: Failed to get KissGoddess last page of album URL {url} (status code: {html.status_code}).')
            return [], ''
        soup = BeautifulSoup(html.text, 'lxml')
        last_image = soup.select('.td-gallery-content > img')[-1]
        try:
            last_image_url = last_image['src'].strip()
        except:
            last_image_url = last_image['data-original'].strip()

        match = re.match(P_LAST_IMAGE.format(album_id), last_image_url, re.M|re.I)
        model_id = -1
        last_page_num = -1
        if match:
            model_id = match.group(1)
            if match.group(2).isdigit():
                last_page_num = int(match.group(2))
        else:
            self._add_error_msg(f'[ERR]: Failed to parse KissGoddess last image of album URL {last_image} (status code: {html.status_code}).')
            return [], ''

        images = [[URL_IMAGE.format(model_id, album_id, i), f'{i}.jpg'] for i in range(1, last_page_num + 1)]
        images.insert(0, [URL_FIRST_IMAGE.format(model_id, album_id), '0.jpg'])
        return images, self._get_valid_name(album_name)
