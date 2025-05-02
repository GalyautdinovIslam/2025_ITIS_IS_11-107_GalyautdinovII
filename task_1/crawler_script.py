import os
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zipfile import ZipFile

ixbt = 'https://www.ixbt.com'
news = '/news/'
ixbt_news = ixbt + news
suffix = '.html'

UTF_8 = 'utf-8'
txt_directory = './task_1/txt_directory'
index_file = './task_1/index.txt'
zip_filename = './task_1/txt.zip'

bad_tags = [
    'script', 'link', 'style'
]


def get_website_urls(start_date, pages_needed):
    date = start_date
    websites = set()
    while len(websites) < pages_needed:
        formatted_date = date.strftime("%Y/%m/%d")
        time.sleep(5)
        response = requests.get(ixbt_news + formatted_date)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [link.get('href') for link in soup.find_all('a') if link.get('href')]
            filtered_links = [link for link in links if link.startswith(news) and link.endswith(suffix)]
            for link in filtered_links:
                websites.add(ixbt + link)
                if len(websites) >= pages_needed:
                    break
        date = date - timedelta(days=1)
    return websites, date


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def handle_response(response, tags_for_removal, directory, idx):
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(tags_for_removal):
            script.extract()

        clean_text = soup.get_text(separator='\n', strip=True)

        # if len(clean_text.split()) <= 1000:
        #     return False

        filename = f'{directory}/page_{idx}.txt'
        with open(filename, 'w', encoding=UTF_8) as txt_file:
            txt_file.write(clean_text)
        print('Успешно: ', idx)
        return True

    return False


def create_zip_file(filename, directory):
    with ZipFile(filename, 'w') as zip_file:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(str(file_path), os.path.relpath(str(file_path), directory))


def main():
    total_pages_needed = 100
    downloaded_pages = 0
    current_date = datetime.now()

    create_directory(txt_directory)

    with open(index_file, 'w') as index:
        while downloaded_pages < total_pages_needed:
            print('Ислам, тут не хватило, мы пробуем снова: ', downloaded_pages)
            websites, current_date = get_website_urls(current_date, total_pages_needed - downloaded_pages)

            for idx, url in enumerate(websites, start=downloaded_pages + 1):
                time.sleep(2)
                response = requests.get(url)
                if handle_response(response, bad_tags, txt_directory, idx):
                    index.write(f'{idx} {url}\n')
                    downloaded_pages += 1

                    if downloaded_pages >= total_pages_needed:
                        break

    create_zip_file(zip_filename, txt_directory)


if __name__ == '__main__':
    main()
