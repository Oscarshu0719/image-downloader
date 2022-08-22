from bs4 import BeautifulSoup
import os
import re
import requests
from tqdm.auto import tqdm

from .downloader import Downloader


class Fapello(Downloader):
    def __init__(self, urls: list, output: str, log: str) -> None:
        super().__init__(output, log)
        self.urls = urls
        self.__fapello()

    def __fapello(self) -> None:
        URL = 'https://fapello.com/{}/{}/'


        urls_num = len(self.urls)
        for i, url in enumerate(self.urls):
            print(f'\n[INFO]: ({i + 1}/{urls_num}) Processing Fapello album URL {url} ...\n')

            model_id = self.__get_model_id(url)
            if model_id == '':
                self._add_error_msg(f'[ERR]: Failed to get Fapello model ID from URL {url}.')
                continue

            html = requests.get(url)
            if html.status_code != requests.codes.ok:
                self._add_error_msg(f'[ERR]: Failed to get Fapello URL {url} (status code: {html.status_code}).')
                continue
            soup = BeautifulSoup(html.text, 'lxml')
            try:
                last_img_url = soup.select('#content > div > a')[0]['href']
            except:
                self._add_error_msg(f'[ERR]: Failed to get Fapello last image url from URL {url}.')
                continue

            last_image_id = self.__get_image_id(last_img_url, model_id)
            if last_image_id == '':
                self._add_error_msg(f'[ERR]: Failed to get Fapello last image ID from URL {last_img_url}.')
                continue

            dir_name = self._get_valid_name(model_id)
            album_path = os.path.join(self.output, dir_name)
            if not os.path.exists(album_path):
                os.makedirs(album_path)
            
            srcs = []
            print(f'\n[INFO]: Retrieving images/videos URL from Fapello model {url} ...\n')
            pbar = tqdm(total=last_image_id, position=0, leave=True)
            pbar.set_description('Fapello')
            for page in range(1, last_image_id + 1):
                page_url = URL.format(model_id, page)
                response = requests.get(page_url)
                if response.status_code != requests.codes.ok:
                    self._add_error_msg(f'[ERR]: Failed to get Fapello image URL {page_url} (status code: {html.status_code}).')
                    continue
                soup = BeautifulSoup(response.text, 'lxml')

                try: 
                    # Some image IDs are found missing.
                    video_div = soup.select('.container > div > div > div')[1]
                    video_src_div = video_div.select('video > source')
                    if len(video_src_div) != 0:
                        srcs.append([video_src_div[0]['src'], f'{page}.m4v'])
                    else: 
                        img_div = soup.select('.container > div > div > div')[1]
                        srcs.append([img_div.select('a')[0]['href'], f'{page}.png'])
                except:
                    self._add_error_msg(f'[ERR]: Failed to get Fapello image URL {page_url}.')
                    pbar.update(1)
                    continue
                
                pbar.update(1)
            pbar.close()
            
            print(f'\n[INFO]: Downloading images/videos from Fapello model {url} ...\n')
            self._download_srcs(srcs, album_path, 'Fapello')

    def __get_model_id(self, url: str) -> str:
        P_MODEL = r'https://fapello.com/(.*)/$'
        match = re.match(P_MODEL, url, re.M|re.I)
        if match:
            return match.group(1)
        else:
            return ''

    def __get_image_id(self, url: str, model_id: str) -> str:
        P_IMAGE = r'https://fapello.com/{}/(\d+)/$'.format(model_id)
        match = re.match(P_IMAGE, url, re.M|re.I)
        if match:
            return int(match.group(1))
        else:
            return ''
