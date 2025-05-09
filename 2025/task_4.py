import json
import math
from collections import defaultdict
import pandas as pd
import os


def load_document_texts(doc_ids):
    docs = {}
    for doc_id in doc_ids:
        file_path = f"lemmas/page_{doc_id}.txt"
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                docs[doc_id] = f.read().split()
    return docs


def calc_tf(doc_texts, terms):
    print("Расчет TF (Term Frequency):")

    tf = defaultdict(dict)
    for doc_id, words in doc_texts.items():
        word_count = len(words)
        term_counts = defaultdict(int)
        for word in words:
            term_counts[word] += 1

        for term, count in term_counts.items():
            if term in terms:
                tf[term][doc_id] = count / word_count

    tf_df = pd.DataFrame.from_dict(tf, orient='index').fillna(0)
    tf_df = tf_df.reindex(terms)
    tf_df = tf_df[sorted(tf_df.columns, key=int)]
    tf_df = tf_df.round(6)
    print(tf_df.head())

    tf_df.to_csv('./task_4/tf_table.csv', float_format='%.6f', sep=';')
    print("Таблица TF сохранена")
    return tf


def calc_idf(inverted_index, terms, N):
    print("Расчет IDF (Inverse Document Frequency):")

    idf = {}
    for term in terms:
        df = len(inverted_index[term])
        idf[term] = math.log(N / (df + 1))

    idf_df = pd.DataFrame.from_dict(idf, orient='index', columns=['IDF'])
    idf_df = idf_df.reindex(terms)
    idf_df = idf_df.round(6)
    print(idf_df.head())

    idf_df.to_csv('./task_4/idf_table.csv', float_format='%.6f', sep=';')
    print("Таблица IDF сохранена")
    return idf


def calc_tf_idf(terms, doc_ids, tf, idf):
    print("Расчет TF-IDF:")

    tf_idf = defaultdict(dict)
    for term in terms:
        for doc_id in doc_ids:
            tf_value = tf[term].get(doc_id, 0.0)
            tf_idf[term][doc_id] = tf_value * idf[term]

    tf_idf_df = pd.DataFrame.from_dict(tf_idf, orient='index')
    tf_idf_df = tf_idf_df.reindex(terms)
    tf_idf_df = tf_idf_df[sorted(tf_idf_df.columns, key=int)]
    tf_idf_df = tf_idf_df.round(6)
    print(tf_idf_df.head())

    tf_idf_df.to_csv('./task_4/tf_idf_table.csv', float_format='%.6f', sep=';')
    print("Таблица TF-IDF сохранена")


def main():
    os.makedirs('./task_4', exist_ok=True)

    with open('inverted_index.json', 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)

    with open('index.txt', 'r', encoding='utf-8') as f:
        doc_ids = sorted([line.split(':')[0].strip() for line in f], key=int)

    doc_texts = load_document_texts(doc_ids)
    N = len(doc_ids)
    terms = sorted(inverted_index.keys())

    tf = calc_tf(doc_texts, terms)
    idf = calc_idf(inverted_index, terms, N)
    calc_tf_idf(terms, doc_ids, tf, idf)


if __name__ == "__main__":
    main()
