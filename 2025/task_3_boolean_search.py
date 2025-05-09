import json
import re
from pymorphy3 import MorphAnalyzer

AND = 'И'
OR = 'ИЛИ'
NOT = 'НЕ'


def load_inverted_index():
    with open('inverted_index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)
    return {lemma: set(map(str, doc_ids)) for lemma, doc_ids in index.items()}


def load_url_map():
    url_map = {}
    with open('index.txt', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(': ')
            if len(parts) == 2:
                doc_id, url = parts
                url_map[doc_id] = url
    return url_map


def parse_query(query):
    query = re.sub(r'\s+', ' ', query)
    return query.split()


class BooleanSearch:
    def __init__(self):
        self.morph = MorphAnalyzer()
        self.inverted_index = load_inverted_index()
        self.url_map = load_url_map()
        self.all_doc_ids = set(self.url_map.keys())

    def normalize_word(self, word):
        return self.morph.parse(word)[0].normal_form

    def process_token(self, token):
        token_lower = token.lower()

        if token_lower == AND.lower():
            return AND
        elif token_lower == OR.lower():
            return OR
        elif token_lower == NOT.lower():
            return NOT
        else:
            return self.normalize_word(token)

    def evaluate_expression(self, tokens):
        current_operation = None
        is_need_invert = False
        result = None

        for token in tokens:
            if token in [AND, OR]:
                current_operation = token
            elif token == NOT:
                is_need_invert = True
            else:
                docs = self.inverted_index.get(token, set())

                if is_need_invert:
                    docs = self.all_doc_ids - docs
                    is_need_invert = False

                if result is None:
                    result = docs
                else:
                    if current_operation == AND:
                        result = result & docs
                    elif current_operation == OR:
                        result = result | docs
                    current_operation = None

        return result or set()

    def search(self, query):
        if not query.strip():
            return []

        tokens = parse_query(query)
        processed_tokens = [self.process_token(t) for t in tokens]
        doc_ids = self.evaluate_expression(processed_tokens)

        sorted_docs = sorted(doc_ids, key=lambda x: int(x))
        return [(doc_id, self.url_map[doc_id]) for doc_id in sorted_docs]


def main():
    searcher = BooleanSearch()

    while True:
        query = input("Поисковый запрос: ").strip()
        results = searcher.search(query)

        if results:
            print(f"Найдено документов: {len(results)}")
            for doc_id, url in results:
                print(f"{doc_id}: {url}")
        else:
            print("Ничего не найдено.")


if __name__ == "__main__":
    main()
