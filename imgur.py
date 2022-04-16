from bs4 import BeautifulSoup
import requests

from downloader import Downloader


class Imgur(Downloader):
    def __init__(self, urls: list, output: str, log: str) -> None:
        super().__init__(output, log)
        self.urls = urls
        self.__imgur()

    def __imgur(self) -> None:
        srcs = list()
        for url in self.urls:
            html = requests.get(url)
            if html.status_code != requests.codes.ok:
                self._add_error_msg(f'[ERR]: Failed to get Imgur URL {url} (status code: {html.status_code}).')
                continue
            soup = BeautifulSoup(html.text, 'lxml')
            image = soup.find("meta", property="og:image")
            video = soup.find("meta", property="og:video")

            if video:
                srcs.append(video['content'].strip())
            else:
                srcs.append(image['content'].strip())

        src_tuples = list()
        for src in srcs:
            filename = src
            rindex = src.rfind('?')
            if rindex != -1:
                filename = filename[: filename.rfind('?')]
            real_url = filename
            filename = filename[filename.rfind('/') + 1: ]
            
            src_tuples.append([real_url, filename])

        if len(src_tuples) != 0:
            self._download_srcs(src_tuples, self.output, 'Imgur')
