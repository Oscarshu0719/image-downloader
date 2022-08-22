from datetime import datetime
import os
import re

from src.imgur import Imgur
from src.junmeitu import Junmeitu
from src.kissgoddess import KissGoddess
from src.fapello import Fapello
from src.xsnvshen import Xsnvshen
from src.twofourfa import TwoFourFA


class Solver(object):
    def __init__(self, urls: list, config: dict) -> None:
        """
        Patterns.
        """
        P_IMGUR = r'^https://imgur.com/'
        P_KISSGODDESS_MODEL = r'^http[s]?://tw.kissgoddess.com/people/(.*).html$'
        P_KISSGODDESS_ALBUM = r'^http[s]?://tw.kissgoddess.com/album/(\d+)[_]?([\d+]?).html$'
        P_XSNVSHEN_MODEL = r'^https://www.xsnvshen.com/girl/(.*)$'
        P_XSNVSHEN_ALBUM = r'^https://www.xsnvshen.com/album/(.*)$'
        P_JUNMEITU_MODEL = r'^https://www.junmeitu.com/model/(.*?)[-]?([\d+]?).html$'
        P_JUNMEITU_ALBUM = r'^https://www.junmeitu.com/beauty/(.*?)[-]?([\d+]?).html$'
        P_TWOFOURFA = r'^https://www.24fa.com/n(\d+)c(\d+).aspx$'
        P_FAPELLO = r'^https://fapello.com/(.*)/$'
        
        """
        Regex objects.
        """
        R_K_ALBUM = re.compile(r'^https://tw.kissgoddess.com/album/(\d+?)(_\d+).html$', re.VERBOSE)
        R_J_MODEL = re.compile(r'^https://www.junmeitu.com/model/(.*?)(-\d+).html$', re.VERBOSE)
        R_J_ALBUM = re.compile(r'^https://www.junmeitu.com/beauty/(.*?)(-\d+).html$', re.VERBOSE)

        self.output = os.path.abspath(config['output'])
        self.log = os.path.abspath(config['log'])
        self.error_msgs = list()

        imgur_urls = list()
        kissgoddess_urls = {'album': list(), 'model': list()}
        xsnvshen_urls = {'album': list(), 'model': list()}
        junmeitu_urls = {'album': list(), 'model': list()}
        twofourfa_urls = list()
        fapello_urls = list()
        for url in urls:
            if re.search(P_IMGUR, url) and url not in imgur_urls:
                imgur_urls.append(url)
            elif re.search(P_KISSGODDESS_ALBUM, url) and url not in kissgoddess_urls['album']:
                kissgoddess_urls['album'].append(
                    R_K_ALBUM.sub(r'https://tw.kissgoddess.com/album/\1.html', url))
            elif re.search(P_KISSGODDESS_MODEL, url) and url not in kissgoddess_urls['model']:
                kissgoddess_urls['model'].append(url)
            elif re.search(P_XSNVSHEN_MODEL, url) and url not in xsnvshen_urls['model']:
                xsnvshen_urls['model'].append(url)
            elif re.search(P_XSNVSHEN_ALBUM, url) and url not in xsnvshen_urls['album']:
                xsnvshen_urls['album'].append(url)
            elif re.search(P_JUNMEITU_MODEL, url) and url not in junmeitu_urls['model']:
                junmeitu_urls['model'].append(
                    R_J_MODEL.sub(r'https://www.junmeitu.com/model/\1.html', url))
            elif re.search(P_JUNMEITU_ALBUM, url) and url not in junmeitu_urls['album']:
                junmeitu_urls['album'].append(
                    R_J_ALBUM.sub(r'https://www.junmeitu.com/beauty/\1.html', url))
            elif re.search(P_TWOFOURFA, url) and url not in twofourfa_urls:
                twofourfa_urls.append(url)
            elif re.search(P_FAPELLO, url) and url not in fapello_urls:
                fapello_urls.append(url)
            else:
                now = datetime.now()
                self.error_msgs.append(f'{now.strftime("%Y/%m/%d %H:%M:%S")} - [ERR]: Failed to parse URL {url}.')

        with open(self.log, 'a') as log:
            log.write('\n'.join(self.error_msgs))
        
        if len(imgur_urls) != 0:
            Imgur(imgur_urls, self.output, self.log)
        if len(kissgoddess_urls['album']) != 0 or len(kissgoddess_urls['model']) != 0:
            KissGoddess(kissgoddess_urls, self.output, self.log)
        if len(xsnvshen_urls['album']) != 0 or len(xsnvshen_urls['model']) != 0:
            Xsnvshen(xsnvshen_urls, self.output, self.log)
        if len(junmeitu_urls['album']) != 0 or len(junmeitu_urls['model']) != 0:
            Junmeitu(junmeitu_urls, self.output, self.log)
        if len(twofourfa_urls) != 0:
            TwoFourFA(twofourfa_urls, self.output, self.log)
        if len(fapello_urls) != 0:
            Fapello(fapello_urls, self.output, self.log)
