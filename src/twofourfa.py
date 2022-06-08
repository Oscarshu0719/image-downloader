from bs4 import BeautifulSoup
import os
import re
import requests
from tqdm.auto import tqdm

from downloader import Downloader


class TwoFourFA(Downloader):
    def __init__(self, urls: list, output: str, log: str) -> None:
        super().__init__(output, log)
        self.urls = urls
        self.__twofourfa()

    def __twofourfa(self) -> None:
        URL = 'https://www.24fa.com/{}.aspx'
        URL_ROOT = 'https://www.24fa.com/'

        urls_num = len(self.urls)
        for i, url in enumerate(self.urls):
            print(f'\n[INFO]: ({i + 1}/{urls_num}) Processing 24FA album URL {url} ...\n')

            album_id = self.__get_album_id(url)
            if album_id == '':
                self._add_error_msg(f'[ERR]: Failed to get 24FA album ID from URL {url}.')
                continue

            html = requests.get(url)
            if html.status_code != requests.codes.ok:
                self._add_error_msg(f'[ERR]: Failed to get 24FA URL {url} (status code: {html.status_code}).')
                continue
            soup = BeautifulSoup(html.text, 'lxml')
            imgs = soup.select('#content > div > div > img')
            if len(imgs) == 0:
                imgs = soup.select('#content > div > p > img')
            img_srcs = [img['src'] for img in imgs]
            title = soup.select('.title2')[0].text
            page_num = int(soup.select('.pager > ul > li:nth-last-child(3)')[0].text)

            dir_name = self._get_valid_name(title)
            album_path = os.path.join(self.output, dir_name)
            if not os.path.exists(album_path):
                os.makedirs(album_path)

            print(f'\n[INFO]: Retrieving images URL from 24FA album {url} ...\n')
            for page in range(2, page_num + 1):
                page_url = URL.format(album_id + f'p{page}')
                response = requests.get(page_url)
                soup = BeautifulSoup(response.text, 'lxml')
                imgs = soup.select('#content > div > div > img')
                if len(imgs) == 0:
                    imgs = soup.select('#content > div > p > img')
                img_srcs.extend([img['src'] for img in imgs])

            
            images = [[URL_ROOT + img_src, f'{i + 1}.png'] for i, img_src in enumerate(img_srcs)]
            print(f'\n[INFO]: Downloading images from 24FA album {url} ...\n')
            self._download_srcs(images, album_path, '24FA ')

    def __get_album_id(self, url: str) -> str:
        P_ALBUM = r'https://www.24fa.com/(.*).aspx'
        match = re.match(P_ALBUM, url, re.M|re.I)
        if match:
            return match.group(1)
        else:
            return ''
