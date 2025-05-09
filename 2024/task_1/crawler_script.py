import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zipfile import ZipFile

ixbt = 'https://www.ixbt.com'
news = '/news/'
ixbt_news = ixbt + news
suffix = '.html'

UTF_8 = 'utf-8'
html_directory = './task_1/html_directory'
index_file = './task_1/index.txt'
zip_filename = './task_1/html.zip'

bad_tags = [
    'script', 'link', 'style'
]


def get_website_urls():
    date = datetime.now()
    websites = set()
    while len(websites) < 100:
        date = date - timedelta(days=1)
        formatted_date = date.strftime("%Y/%m/%d")
        response = requests.get(ixbt_news + formatted_date)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [link.get('href') for link in soup.find_all('a') if link.get('href')]
            filtered_links = [link for link in links if link.startswith(news) and link.endswith(suffix)]
            for link in filtered_links:
                websites.add(ixbt + link)
                # Можно раскомментировать код ниже, чтобы скачать ровно 100. Либо оставить в комментариях,
                # чтобы скачать 100 и более (возьмёт все ссылки на уже скачанной странице)

                # if len(websites) >= 100:
                #     return websites
    return websites


def create_html_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def handle_response(response, tags_for_removal, directory, idx):
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(tags_for_removal):
            script.extract()

        filename = f'{directory}/page_{idx}.html'
        with open(filename, 'w', encoding=UTF_8) as html_file:
            html_file.write(soup.prettify())
        return True
    return False


def create_zip_file(filename, directory):
    with ZipFile(filename, 'w') as zip_file:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(str(file_path), os.path.relpath(str(file_path), directory))


def main():
    websites = get_website_urls()
    create_html_directory(html_directory)

    with open(index_file, 'w') as index:
        for idx, url in enumerate(websites, start=1):
            response = requests.get(url)
            if handle_response(response, bad_tags, html_directory, idx):
                index.write(f'{idx} {url}\n')

    create_zip_file(zip_filename, html_directory)


if __name__ == '__main__':
    main()
