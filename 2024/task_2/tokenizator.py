import collections
import nltk
import os
import pymorphy3
from bs4 import BeautifulSoup

html_directory = './html_directory'
tokens_file = './tokens.txt'
lemmas_file = './lemmas.txt'
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


def get_text(directory):
    texts = []
    for filename in os.listdir(directory):
        file_path = directory + '/' + filename
        with open(file_path, 'r', encoding=UTF_8) as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            texts.append(' '.join(soup.stripped_strings))
    return ' '.join(texts)


def processing(directory, tokenizer, stop_words, morphy):
    tokens = set()
    lemmas = collections.defaultdict(set)

    text = get_text(directory)
    row_tokens = tokenizer.tokenize(text)
    for token in row_tokens:
        token = token.lower()
        if len(token) < 2:
            continue
        if token in stop_words:
            continue
        morph = morphy.parse(token)
        if any([x for x in BAD_TOKENS if x in morph[0].tag]):
            continue
        tokens.add(token)
        if morph[0].score >= 0.5:
            lemmas[morph[0].normal_form].add(token)

    return tokens, lemmas


def save(tokens, lemmas, tokens_filename, lemmas_filename):
    with open(tokens_filename, 'w', encoding=UTF_8) as file:
        file.write('\n'.join(tokens) + '\n')
    with open(lemmas_filename, 'w', encoding=UTF_8) as file:
        for lemma, tokens in lemmas.items():
            file.write(f'{lemma} {' '.join(tokens)}\n')


def main():
    nltk.download('stopwords')

    stop_words = set(nltk.corpus.stopwords.words(RUSSIAN))
    tokenizer = nltk.tokenize.WordPunctTokenizer()
    morphy = pymorphy3.MorphAnalyzer()

    tokens, lemmas = processing(html_directory, tokenizer, stop_words, morphy)
    save(tokens, lemmas, tokens_file, lemmas_file)


if __name__ == '__main__':
    main()
