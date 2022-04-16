from datetime import datetime, timedelta
import os 
import requests
from tqdm.auto import tqdm


class Downloader(object):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
    }

    def __init__(self, output: str, log: str) -> None:
        self.output = output
        self.log = log
        self.error_msgs = list()

    def _get_valid_name(self, name: str) -> str:
        INVALID_CHAR = {'\\', '/', ':', '*', '?', '"', '<', '>', '|', '\n'}
        return ''.join(char for char in name if char not in INVALID_CHAR)

    # def _download_src(self, url: str, path: str) -> None: 
    #     response = requests.get(url)
    #     if response.status_code == requests.codes.ok:
    #         with open(path, 'wb') as image_file:
    #             image_file.write(response.content)
    #     else:
    #         self._add_error_msg(f'[WARN]: Failed to download URL {url} (status code: {response.status_code}).')

    """
        `src`: [url, path]
    """
    def _download_srcs(self, srcs: list, parent_dir: str, description: str, headers=HEADERS) -> None: 
        pbar = tqdm(total=len(srcs), position=0, leave=True)
        pbar.set_description(description)
        start = datetime.now()
        for src in srcs:
            response = requests.get(src[0], headers=headers)
            if response.status_code == requests.codes.ok:
                with open(os.path.join(parent_dir, src[1]), 'wb') as image_file:
                    image_file.write(response.content)
            else:
                self._add_error_msg(f'[WARN]: Failed to download URL {src[0]} (status code: {response.status_code}).')

            pbar.update(1)
        pbar.close()
        
        duration = datetime.now() - start
        print(f'\nDuration: {timedelta(seconds=duration.total_seconds())}.\n')

    def _write_log(self) -> None: 
        with open(self.log, 'a') as log:
            log.write('\n'.join(self.error_msgs))

    def _add_error_msg(self, msg: str) -> None: 
        now = datetime.now()
        self.error_msgs.append(f'{now.strftime("%Y/%m/%d %H:%M:%S")} - {msg}')

    def _is_duplicated(self, path: str, images_num: int) -> bool:
        return len(os.listdir(path)) == images_num
