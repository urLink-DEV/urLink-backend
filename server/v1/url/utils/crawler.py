import asyncio
from urllib.parse import urlparse

import aiohttp
import requests
from bs4 import BeautifulSoup


class Crawler:
    IMAGE_404 = 'https://urlink.s3.ap-northeast-2.amazonaws.com/static/404-image.png'
    IMAGE_FAVICON = 'https://urlink.s3.ap-northeast-2.amazonaws.com/static/favicon.png'

    async def get_html(self, path):
        self.path = path
        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'Sec-Fetch-Dest': 'document'
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.path, headers=headers, timeout=5) as response:
                    response.encoding = None
                    return await response.text()
        except Exception as e:
            return str(e)

    def get_meta_data(self, html, keys):
        for key in keys:
            if html.find('meta', key) and html.find('meta', key).get('content'):
                return html.find('meta', key).get('content')
        return '알수없음'

    def get_favicon(self, html, keys):
        for key in keys:
            if html.find('link', key) and html.find('link', key).get('href'):
                return html.find('link', key).get('href')
        return '알수없음'

    def is_correct_image(self, path):
        try:
            response = requests.get(path)
            if "image" in response.headers['Content-Type']:
                return True
        except Exception as e:
            print(e)
        return False

    def is_unknown_image_or_favicon(self, type, path):
        if path == "알수없음":
            if type == 'image':
                return self.IMAGE_404
            else:
                return self.IMAGE_FAVICON
        else:
            return path

    def is_insufficient_url(self, path):
        if urlparse(path).scheme == '':
            url = urlparse(self.path)
            if urlparse(path).netloc == '':
                return f"{url.scheme}://{url.netloc}{path}"
            else:
                return f"{url.scheme}:{path}"
        else:
            return path

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        head = soup.head

        if not head:
            return {
                'title': '알수없음',
                'description': '알수없음',
                'image_path': self.IMAGE_404,
                'favicon_path': self.IMAGE_FAVICON
            }

        if head.title:
            title = head.title.text.strip()
        else:
            title = self.get_meta_data(head, [{'name': 'title'}, {'property': 'og:title'}])
        description = self.get_meta_data(head, [{'name': 'description'}, {'property': 'og:description'}])
        image_path = self.is_insufficient_url(self.is_unknown_image_or_favicon('image', self.get_meta_data(head, [
            {'property': 'og:image'}, {'property': 'twitter:image'}])))
        favicon_path = self.is_insufficient_url(self.is_unknown_image_or_favicon('favicon', self.get_favicon(head, [
            {'rel': 'shortcut icon'}, {'rel': 'icon'}])))

        if not self.is_correct_image(image_path):
            image_path = self.is_unknown_image_or_favicon('image', '알수없음')
        if not self.is_correct_image(favicon_path):
            favicon_path = self.is_unknown_image_or_favicon('favicon', '알수없음')

        return {
            'title': title,
            'description': description,
            'image_path': image_path,
            'favicon_path': favicon_path
        }


async def main():
    c = Crawler()
    for i in [c.parse_html(i) for i in (await asyncio.gather(*[c.get_html(url) for url in urls]))]:
        pprint(i)


if __name__ == "__main__":
    from pprint import pprint
    import time

    start = time.time()
    urls = [
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
    asyncio.run(main())
    print(time.time() - start)
