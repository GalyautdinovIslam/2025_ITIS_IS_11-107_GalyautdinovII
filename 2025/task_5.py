import pandas as pd
import numpy as np
from pymorphy3 import MorphAnalyzer


class VectorSearch:
    def __init__(self):
        self.tf_idf_df = None
        self.terms = None
        self.doc_ids = None
        self.tf_idf_matrix = None
        self.url_map = None

        self.morph = MorphAnalyzer()
        self.load_indexes()
        self.load_url_map()

    def load_indexes(self):
        self.tf_idf_df = pd.read_csv('./task_4/tf_idf_table.csv', index_col=0, sep=';')
        self.terms = self.tf_idf_df.index.tolist()
        self.doc_ids = [col for col in self.tf_idf_df.columns if col.isdigit()]
        self.tf_idf_matrix = self.tf_idf_df.values.T

    def load_url_map(self):
        self.url_map = {}
        with open('index.txt', 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(': ')
                if len(parts) == 2:
                    doc_id, url = parts
                    self.url_map[doc_id] = url

    def normalize_query(self, query):
        words = query.lower().split()
        return [self.morph.parse(word)[0].normal_form for word in words]

    def get_query_vector(self, query_terms):
        query_vector = np.zeros(len(self.terms))

        for term in query_terms:
            if term in self.terms:
                idx = self.terms.index(term)
                query_vector[idx] = 1

        return query_vector

    def cosine_similarity(self, query_vector):
        doc_norms = np.linalg.norm(self.tf_idf_matrix, axis=1)
        normalized_tf_idf = self.tf_idf_matrix / doc_norms[:, np.newaxis]

        query_norm = np.linalg.norm(query_vector)
        if query_norm == 0:
            return np.zeros(len(self.doc_ids))
        normalized_query = query_vector / query_norm

        scores = normalized_tf_idf.dot(normalized_query)
        return scores

    def search(self, query):
        query_terms = self.normalize_query(query)
        if not query_terms:
            return []

        query_vector = self.get_query_vector(query_terms)
        scores = self.cosine_similarity(query_vector)

        results = []
        for idx in np.argsort(scores)[::-1]:
            doc_id = self.doc_ids[idx]
            score = scores[idx]
            if score > 0:
                results.append((doc_id, self.url_map[doc_id], round(score, 6)))

        return results


def main():
    searcher = VectorSearch()

    while True:
        query = input("Поисковый запрос: ").strip()
        results = searcher.search(query)

        if results:
            print(f"Найдено документов: {len(results)}")
            print("Рейтинг | Документ | URL")
            print("------------------------")
            for doc_id, url, score in results:
                print(f"{score:.6f} | {doc_id} | {url}")
        else:
            print("Ничего не найдено.")


if __name__ == "__main__":
    main()
