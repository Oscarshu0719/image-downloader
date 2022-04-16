import argparse
import os

from solver import Solver

INTRO = """
* Websites:
- Imgur: https://imgur.com/
- KissGoddess: http://tw.kissgoddess.com/
- Xsnvshen: https://www.xsnvshen.com/
- Junmeitu: https://www.junmeitu.com/
"""

def main(config: dict) -> None:
    if not os.path.exists(config.output):
        os.makedirs(config.output)

    urls = list()
    if config.input and os.path.isfile(config.input):
        with open(config.input, 'r') as input:
            urls = set(map(str.strip, input.readlines()))
    elif not os.path.isfile(config.input):
        with open(config.log, 'a') as log:
            log.write(f'{config.input} is NOT a file.')

    if config.url:
        urls.append(config.url)    

    Solver(urls, {'log': config.log, 'output': config.output})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--url', type=str, help='URL (link).')
    parser.add_argument('--input', type=str, default='', help='Destination of input file.')
    parser.add_argument('--output', type=str, default=os.path.abspath('output'), help='Destination of output folder.')
    parser.add_argument('--log', type=str, default=os.path.abspath('output.log'), help='Destination of log.')

    config = parser.parse_args()
    print(INTRO)
    print(f'{config}\n')
    main(config)
