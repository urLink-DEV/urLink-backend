import asyncio
import time
from pprint import pprint
from urllib.parse import urlparse

import aiohttp
import requests
from bs4 import BeautifulSoup


class Crawler:
    IMAGE_404 = 'https://urlink.s3.ap-northeast-2.amazonaws.com/static/404-image-20210113.png'
    IMAGE_FAVICON = 'https://urlink.s3.ap-northeast-2.amazonaws.com/static/favicon.png'
    DEFAULT_TITLE_TEXT = '제목을 가져오지 못했어요. 직접 제목을 입력해보세요.'
    DEFAULT_DESCRIPTION_TEXT = '본문을 가져오지 못했어요. 저장한 링크의 내용을 간단히 기록해보세요.'
    MAXIMUM_PATH_LENGTH = 500
    HEADERS = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        'Sec-Fetch-Dest': 'document'
    }

    async def get_html_by_async(self, path):
        self.path = path
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.path, headers=Crawler.HEADERS, timeout=5) as response:
                    response.encoding = None
                    return await response.text()
        except Exception as e:
            return str(e)

    def get_html_by_sync(self, path):
        self.path = path
        try:
            response = requests.get(self.path, headers=Crawler.HEADERS, timeout=5)
            response.encoding = None
            return response.text
        except Exception as e:
            return str(e)

    def get_meta_data(self, html, keys):
        for key in keys:
            if html.find('meta', key) and html.find('meta', key).get('content') and \
                    not html.find('meta', key).get('content').isspace():
                return html.find('meta', key).get('content')
        return None

    def get_favicon(self, html, keys):
        for key in keys:
            if html.find('link', key) and html.find('link', key).get('href'):
                return html.find('link', key).get('href')
        return None

    def is_correct_image(self, path):
        try:
            response = requests.get(path)
            if "image" in response.headers['Content-Type']:
                return True
        except Exception as e:
            print(e)
        return False

    def attach_full_scheme_on_path(self, path):
        if urlparse(path).scheme == '':
            url = urlparse(self.path)
            if urlparse(path).netloc == '':
                return f"{url.scheme}://{url.netloc}{path}"
            else:
                return f"{url.scheme}:{path}"
        else:
            return path

    def examine_image_or_favicon_path(self, type, path):
        default_path_dict = {"image": Crawler.IMAGE_404, "favicon": Crawler.IMAGE_FAVICON}

        if path is None:
            return default_path_dict[type]
        else:
            path = self.attach_full_scheme_on_path(path)
            if len(path) > Crawler.MAXIMUM_PATH_LENGTH:
                path = self.shorten_path(path)

            if self.is_correct_image(path):
                return path
            else:
                return default_path_dict[type]

    @staticmethod
    def shorten_path(path):
        response = requests.post('https://cutt.ly/scripts/shortenUrl.php', data={'url': path, 'domain': '0'})
        if response.ok:
            return response.text
        else:
            return None

    def parse_html(self, path, html):
        soup = BeautifulSoup(html, 'html.parser')
        head = soup.head
        path = path if len(path) <= Crawler.MAXIMUM_PATH_LENGTH else self.shorten_path(path)

        if not head:
            return {
                'path': path,
                'title': Crawler.DEFAULT_TITLE_TEXT,
                'description': Crawler.DEFAULT_DESCRIPTION_TEXT,
                'image_path': Crawler.IMAGE_404,
                'favicon_path': Crawler.IMAGE_FAVICON
            }

        if head.title:
            title = head.title.text.strip()
        else:
            title = self.get_meta_data(head, [{'name': 'title'}, {'property': 'og:title'}])
        description = self.get_meta_data(head, [{'name': 'description'}, {'property': 'og:description'}])
        image_path = self.examine_image_or_favicon_path("image", self.get_meta_data(head, [{'property': 'og:image'},
                                                                                           {'property': 'twitter:image'}]))
        favicon_path = self.examine_image_or_favicon_path("favicon", self.get_favicon(head, [{'rel': 'shortcut icon'},
                                                                                             {'rel': 'icon'}]))

        return {
            'path': path,
            'title': title[:500] if title else Crawler.DEFAULT_TITLE_TEXT,
            'description': description[:500] if description else Crawler.DEFAULT_DESCRIPTION_TEXT,
            'image_path': image_path,
            'favicon_path': favicon_path
        }


async def main():
    for i in [c.parse_html(urls[idx], html) for idx, html in
              enumerate(await asyncio.gather(*[c.get_html_by_async(url) for url in urls]))]:
        pprint(i)


if __name__ == "__main__":
    c = Crawler()
    urls = ['https://woowabros.github.io/experience/2020/10/08/excel-download.html',
            'https://programmers.co.kr/learn/challenges?tab=all_challenges',
            'https://www.acmicpc.net/',
            'https://ssungkang.tistory.com/category/%EC%9B%B9%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D/Django',
            'https://tech.cloud.nongshim.co.kr/techblog/',
            'https://mail.google.com/mail/u/0/#inbox',
            'https://syundev.tistory.com/29?category=868616',
            'https://github.com/hotire/turnover-story',
            'http://www.bloter.net/archives/257437',
            'https://www.youtube.com/watch?v=r6TFnNQsQLY&feature=youtu.be',
            'https://ofcourse.kr/css-course/cursor-%EC%86%8D%EC%84%B1',
            'https://material.io/design/layout/responsive-layout-grid.html',
            'https://www.kobaco.co.kr/site/main/content/what_public_ad']

    # 1. async
    print("###async start###")
    start = time.time()
    asyncio.run(main())
    print("async : ", time.time() - start)

    time.sleep(5)

    # 2. sync
    print("###sync start###")
    start = time.time()
    for path in urls:
        html = c.get_html_by_sync(path)
        pprint(c.parse_html(path, html))
    print("sync : ", time.time() - start)
