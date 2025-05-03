import collections
import math
import nltk
import os
import pymorphy3

txt_directory = './txt_directory'
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
    return ''.join(filter(str.isdigit, filename))


def get_text(directory):
    texts = collections.defaultdict(str)
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            index = int(get_index(filename))
            with open(file_path, 'r', encoding=UTF_8) as file:
                texts[index] = file.read()
    return texts


def count(token, texts):
    return sum(1 for text in texts.values() if token in text.lower())


def count_lemma(lemma, tokens, texts):
    return sum(1 for text in texts.values()
               if any(token in text.lower() for token in tokens) or lemma in text.lower())


def save_table(filename, data):
    with open(filename, 'a', encoding=UTF_8) as file:
        for word, idf, tf_idf in data:
            file.write(f"{word} {idf} {tf_idf}\n")

    # with open(filename, 'w', encoding=UTF_8) as file:
    #     file.write(f"{'Term':<30}{'IDF':<15}{'TF-IDF':<15}\n")
    #     file.write('-' * 60 + '\n')
    #
    #     for word, idf, tf_idf in data:
    #         file.write(f"{word:<30}{idf:<15.6f}{tf_idf:<15.6f}\n")


def main():
    nltk.download('stopwords')

    os.makedirs('tokens', exist_ok=True)
    os.makedirs('lemmas', exist_ok=True)

    texts = get_text(txt_directory)
    keys = sorted(texts.keys())

    for index in keys:
        text = texts[index]
        text_tokenizator = Tokenizator(text)
        text_tokenizator.processing()
        counter = collections.Counter(text_tokenizator.tokens)

        token_data = []
        for token in text_tokenizator.tokens:
            tf = counter[token] / len(text_tokenizator.tokens)
            idf = math.log(len(texts) / max(1, count(token, texts)))
            tf_idf = tf * idf
            token_data.append((token, round(idf, 6), round(tf_idf, 6)))

        lemma_data = []
        for lemma, tokens in text_tokenizator.lemmas.items():
            cnt = counter.get(lemma, 0)
            for token in tokens:
                cnt += counter.get(token, 0)
            tf = cnt / len(text_tokenizator.tokens)
            idf = math.log(len(texts) / max(1, count_lemma(lemma, tokens, texts)))
            tf_idf = tf * idf
            lemma_data.append((lemma, round(idf, 6), round(tf_idf, 6)))

        save_table(PREFIX_TOKENS + str(index) + SUFFIX_TXT, sorted(token_data))
        save_table(PREFIX_LEMMAS + str(index) + SUFFIX_TXT, sorted(lemma_data))


if __name__ == '__main__':
    main()
