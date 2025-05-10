import os
import re
from pymorphy3 import MorphAnalyzer
from nltk.corpus import stopwords
import nltk


def tokenize(text):
    cleaned_text = re.sub(r'[^а-яёА-ЯЁ\s-]', ' ', text.lower())
    tokens = re.findall(r'\b[а-яё]+\b', cleaned_text)
    return tokens


def is_russian(word):
    return word.score > 0.8


class TextProcessor:
    def __init__(self):
        nltk.download('stopwords')
        self.morph = MorphAnalyzer()
        self.russian_stopwords = set(stopwords.words('russian'))

    def lemmatize(self, tokens):
        lemmas = []
        for token in tokens:
            if token.isdigit():
                continue

            parsed = self.morph.parse(token)[0]

            if not is_russian(parsed):
                continue

            lemma = parsed.normal_form
            lemmas.append(lemma)
        return lemmas

    def remove_stopwords(self, lemmas):
        return [lemma for lemma in lemmas if lemma not in self.russian_stopwords]

    def process_text(self, text):
        tokens = tokenize(text)
        lemmas = self.lemmatize(tokens)
        clean_lemmas = self.remove_stopwords(lemmas)
        return ' '.join(clean_lemmas)


def main():
    input_dir = 'crawled_pages'
    output_dir = 'lemmas'

    processor = TextProcessor()
    os.makedirs(output_dir, exist_ok=True)

    for filename in sorted(os.listdir(input_dir)):
        if filename.startswith('page_') and filename.endswith('.txt'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                processed_text = processor.process_text(text)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(processed_text)

                print(f"Обработан файл: {filename}")
            except Exception as e:
                print(f"Ошибка при обработке файла {filename}: {e}")

    print("Обработка всех документов завершена!")


if __name__ == "__main__":
    main()
