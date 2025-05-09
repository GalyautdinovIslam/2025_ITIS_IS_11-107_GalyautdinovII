import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse, urlunparse, quote, unquote
import os

urls = [
    'https://ru.wikipedia.org/wiki/Noize_MC',
    'https://t-j.ru/short/bubble-tea-spb/',
]


def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def is_already_encoded(url):
    return unquote(url) != url


def normalize_url(url):
    try:
        parsed = urlparse(url)

        encoded_path = parsed.path if is_already_encoded(parsed.path) else quote(parsed.path)
        params = parsed.params if parsed.params else ''
        encoded_params = params if is_already_encoded(params) else quote(params)

        clean_parsed = parsed._replace(
            path=encoded_path,
            params=encoded_params,
            query='',
            fragment=''
        )

        normalized_url = urlunparse(clean_parsed)

        if any(ord(char) > 127 for char in normalized_url):
            scheme, netloc, path, params, _, _ = urlparse(normalized_url)
            try:
                decoded_netloc = netloc.encode('ascii').decode('idna')
                if decoded_netloc != netloc:
                    netloc = decoded_netloc.encode('idna').decode('ascii')
            except:
                netloc = netloc.encode('idna').decode('ascii')

            normalized_url = urlunparse((scheme, netloc, path, params, '', ''))

        return normalized_url
    except Exception as e:
        print(f"Ошибка нормализации URL {url}: {e}")
        raise e


def get_clean_text(soup):
    for element in soup(['script', 'style', 'head', 'meta', 'link', 'nav', 'footer', 'iframe']):
        element.decompose()

    text = soup.get_text(separator=' ', strip=True)

    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def count_words(text):
    return len(text.split())


def extract_links(url, soup):
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        absolute_url = urljoin(url, href)
        if is_valid_url(absolute_url):
            normalized_url = normalize_url(absolute_url)
            links.add(normalized_url)
    return links


def is_mostly_cyrillic(text):
    cyrillic_count = sum(1 for char in text if 'а' <= char <= 'я' or 'А' <= char <= 'Я' or char == 'ё' or char == 'Ё')
    total_letters = sum(1 for char in text if char.isalpha())

    if total_letters == 0:
        return False

    ratio = cyrillic_count / total_letters
    return ratio >= 0.5


class WebCrawler:
    def __init__(self):
        self.visited_urls = set()
        self.downloaded_urls = {}
        self.counter = 1
        self.max_pages = 100
        self.min_words = 1000

    def save_page(self, url, text):
        filename = f"crawled_pages/page_{self.counter}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)

        self.downloaded_urls[self.counter] = url
        with open('index.txt', 'a', encoding='utf-8') as index_file:
            index_file.write(f"{self.counter}: {url}\n")

        self.counter += 1

    def crawl(self, urls):
        queue = set(urls)

        while queue and len(self.downloaded_urls) < self.max_pages:
            url = normalize_url(queue.pop())

            if url in self.visited_urls:
                print(f"Страница отброшена, так как была обработана ранее: {url}")
                continue

            print(f"Начинаем обрабатывать: {url}")
            self.visited_urls.add(url)

            try:
                head_response = requests.head(url, timeout=5)
                head_response.raise_for_status()

                content_type = head_response.headers.get('Content-Type', '').lower()

                if 'pdf' in content_type or 'xml' in content_type:
                    print(f"Страница отброшена (PDF/XML): {url}")
                    continue

                parsed_url = urlparse(url)
                path = parsed_url.path.lower()
                if path.endswith('.pdf') or path.endswith('.xml'):
                    print(f"Страница отброшена (расширение PDF/XML): {url}")
                    continue

                response = requests.get(url, timeout=5)
                response.raise_for_status()
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')

                text = get_clean_text(soup)
                word_count = count_words(text)

                if not is_mostly_cyrillic(text):
                    print(f"Страница отброшена (мало кириллицы): {url}")
                    continue

                if word_count >= self.min_words:
                    self.save_page(url, text)
                else:
                    print(f"Страница отброшена, так как не хватает количества слов: {url}")

                if len(self.downloaded_urls) < self.max_pages:
                    new_links = extract_links(url, soup)
                    queue.update(new_links - self.visited_urls)

            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")

        print(f"Завершено. Скачано {len(self.downloaded_urls)} страниц.")


def main():
    crawler = WebCrawler()

    for url in urls:
        if not is_valid_url(url):
            print(f"Недопустимый URL: {url}")
            urls.remove(url)

    if not urls:
        print("Не указаны начальные корректные URL.")
        exit(1)

    os.makedirs('crawled_pages', exist_ok=True)

    crawler.crawl(urls)


if __name__ == "__main__":
    main()
