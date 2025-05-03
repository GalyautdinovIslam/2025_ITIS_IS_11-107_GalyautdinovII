import collections
import nltk
import os
import pymorphy3

txt_directory = './txt_directory'
tokens_file = './tokens.txt'
lemmas_file = './lemmas.txt'
indexes_file = './indexes.txt'
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


def get_index(filename):
    result = ''
    for char in filename:
        if char.isdigit():
            result += char
    return result


def get_text(directory):
    texts = collections.defaultdict(str)
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            index = int(get_index(filename))
            with open(file_path, 'r', encoding=UTF_8) as file:
                texts[index] = file.read()
    return texts


def processing(directory, tokenizer, stop_words, morphy):
    tokens = set()
    lemmas = collections.defaultdict(set)
    indexes = collections.defaultdict(set)

    texts = get_text(directory)
    keys = sorted(texts.keys())
    for index in keys:
        row_tokens = tokenizer.tokenize(texts.get(index))
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
                normal_form = morph[0].normal_form
                lemmas[normal_form].add(token)
                indexes[normal_form].add(index)

    return tokens, lemmas, indexes


def save(tokens, lemmas, indexes, tokens_filename, lemmas_filename, indexes_filename):
    with open(tokens_filename, 'w', encoding=UTF_8) as file:
        file.write('\n'.join(sorted(tokens)) + '\n')

    with open(lemmas_filename, 'w', encoding=UTF_8) as file:
        for lemma in sorted(lemmas.keys()):
            file.write(f'{lemma} {" ".join(sorted(lemmas[lemma]))}\n')

    with open(indexes_filename, 'w', encoding=UTF_8) as file:
        for lemma in sorted(indexes.keys()):
            sorted_indexes = sorted(indexes[lemma])
            file.write(f'{lemma} {" ".join(map(str, sorted_indexes))}\n')


def main():
    nltk.download('stopwords')

    stop_words = set(nltk.corpus.stopwords.words(RUSSIAN))
    tokenizer = nltk.tokenize.WordPunctTokenizer()
    morphy = pymorphy3.MorphAnalyzer()

    tokens, lemmas, indexes = processing(txt_directory, tokenizer, stop_words, morphy)
    save(tokens, lemmas, indexes, tokens_file, lemmas_file, indexes_file)


if __name__ == '__main__':
    main()
