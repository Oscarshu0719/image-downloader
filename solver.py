from datetime import datetime
import os
import re

from imgur import Imgur
from junmeitu import Junmeitu
from kissgoddess import KissGoddess
from xsnvshen import Xsnvshen


class Solver(object):
    def __init__(self, urls: list, config: dict) -> None:
        P_IMGUR = r'^https://imgur.com/'
        P_K_MODEL = r'^http[s]?://tw.kissgoddess.com/people/(.*).html$'
        P_K_ALBUM = r'^http[s]?://tw.kissgoddess.com/album/(\d+)[_]?([\d+]?).html$'
        P_X_MODEL = r'^https://www.xsnvshen.com/girl/(.*)$'
        P_X_ALBUM = r'^https://www.xsnvshen.com/album/(.*)$'
        P_J_MODEL = r'^https://www.junmeitu.com/model/(.*?)[-]?([\d+]?).html$'
        P_J_ALBUM = r'^https://www.junmeitu.com/beauty/(.*?)[-]?([\d+]?).html$'
        
        R_K_ALBUM = re.compile(r'^https://tw.kissgoddess.com/album/(\d+?)(_\d+).html$', re.VERBOSE)
        R_J_MODEL = re.compile(r'^https://www.junmeitu.com/model/(.*?)(-\d+).html$', re.VERBOSE)
        R_J_ALBUM = re.compile(r'^https://www.junmeitu.com/beauty/(.*?)(-\d+).html$', re.VERBOSE)

        self.output = os.path.abspath(config['output'])
        self.log = os.path.abspath(config['log'])
        self.error_msgs = list()

        imgur_urls = list()
        kiss_urls = {'album': list(), 'model': list()}
        xsnvshen_urls = {'album': list(), 'model': list()}
        junmeitu_urls = {'album': list(), 'model': list()}
        for url in urls:
            if re.search(P_IMGUR, url):
                imgur_urls.append(url)
            elif re.search(P_K_ALBUM, url):
                kiss_urls['album'].append(
                    R_K_ALBUM.sub(r'https://tw.kissgoddess.com/album/\1.html', url))
            elif re.search(P_K_MODEL, url):
                kiss_urls['model'].append(url)
            elif re.search(P_X_MODEL, url):
                xsnvshen_urls['model'].append(url)
            elif re.search(P_X_ALBUM, url):
                xsnvshen_urls['album'].append(url)
            elif re.search(P_J_MODEL, url):
                junmeitu_urls['model'].append(
                    R_J_MODEL.sub(r'https://www.junmeitu.com/model/\1.html', url))
            elif re.search(P_J_ALBUM, url):
                junmeitu_urls['album'].append(
                    R_J_ALBUM.sub(r'https://www.junmeitu.com/beauty/\1.html', url))
            else:
                now = datetime.now()
                self.error_msgs.append(f'{now.strftime("%Y/%m/%d %H:%M:%S")} - [ERR]: Failed to parse URL {url}.')

        with open(self.log, 'a') as log:
            log.write('\n'.join(self.error_msgs))
        
        Imgur(imgur_urls, self.output, self.log)
        KissGoddess(kiss_urls, self.output, self.log)
        Xsnvshen(xsnvshen_urls, self.output, self.log)
        Junmeitu(junmeitu_urls, self.output, self.log)
