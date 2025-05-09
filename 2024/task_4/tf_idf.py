import collections
import math

import nltk
import os
import pymorphy3
from bs4 import BeautifulSoup

html_directory = './html_directory'
BAD_TOKENS = {
    'NUMB',  # Числа
    'ROMN',  # Римские числа
    'PNCT',  # Пунктуация
    'PREP',  # Предлоги
    'CONJ',  # Союзы
    'PRCL',  # Частицы
    'INTJ',  # Междометия (а ещё тип личности Стратег)
    'LATN',  # Латиница
    'UNKN',  # Неизвестное
}

UTF_8 = 'utf-8'
RUSSIAN = 'russian'
PREFIX_TOKENS = './tokens/page_'
PREFIX_LEMMAS = './lemmas/page_'
SUFFIX_TXT = '.txt'


class Tokenizator:

    def __init__(self, text):
        self.text = text
        self.tokenizer = nltk.tokenize.WordPunctTokenizer()
        self.morphy = pymorphy3.MorphAnalyzer()
        self.stop_words = set(nltk.corpus.stopwords.words(RUSSIAN))

        self.row_tokens = self.tokenizer.tokenize(self.text)
        self.tokens = set()
        self.lemmas = collections.defaultdict(set)

    def processing(self):
        for token in self.row_tokens:
            token = token.lower()
            if len(token) < 2:
                continue
            if token in self.stop_words:
                continue
            morph = self.morphy.parse(token)
            if any([x for x in BAD_TOKENS if x in morph[0].tag]):
                continue
            self.tokens.add(token)
            if morph[0].score >= 0.5:
                self.lemmas[morph[0].normal_form].add(token)


def get_index(filename):
    result = ''
    for char in filename:
        if char.isdigit():
            result += char
    return result


def get_text(directory):
    texts = collections.defaultdict(str)
    for filename in os.listdir(directory):
        file_path = directory + '/' + filename
        index = int(get_index(filename))
        with open(file_path, 'r', encoding=UTF_8) as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            texts[index] = ' '.join(soup.stripped_strings)
    return texts


def count(token, texts):
    cnt = 0
    for text in texts.values():
        if token in text.lower():
            cnt += 1
    return cnt


def count_lemma(lemma, tokens, texts):
    cnt = 0
    for text in texts.values():
        if any(token in text.lower() for token in tokens) or lemma in text.lower():
            cnt += 1
    return cnt


def save(filename, word, idf, tf_idf):
    with open(filename, 'a', encoding=UTF_8) as file:
        file.write(f"{word} {idf} {tf_idf}\n")


def main():
    texts = get_text(html_directory)
    keys = sorted(texts.keys())
    for index in keys:
        text = texts[index]
        text_tokenizator = Tokenizator(text)
        text_tokenizator.processing()
        counter = collections.Counter(text_tokenizator.tokens)
        for token in text_tokenizator.tokens:
            tf = counter[token] / len(text_tokenizator.tokens)
            idf = math.log(len(texts) / count(token, texts))
            tf_idf = tf * idf
            save(PREFIX_TOKENS + str(index) + SUFFIX_TXT, token, idf, tf_idf)
        for lemma in text_tokenizator.lemmas.keys():
            cnt = counter[lemma]
            tokens = text_tokenizator.lemmas.get(lemma)
            for token in tokens:
                cnt += counter[token]
            tf = cnt / len(text_tokenizator.tokens)
            idf = math.log(len(texts) / count_lemma(lemma, tokens, texts))
            tf_idf = tf * idf
            save(PREFIX_LEMMAS + str(index) + SUFFIX_TXT, lemma, idf, tf_idf)


if __name__ == '__main__':
    main()
