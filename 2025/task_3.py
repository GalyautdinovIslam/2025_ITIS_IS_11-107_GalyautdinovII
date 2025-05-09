import os
import json
from collections import defaultdict


def build_inverted_index():
    lemmas_dir = 'lemmas'
    inverted_index = defaultdict(list)

    for filename in os.listdir(lemmas_dir):
        if filename.startswith('page_') and filename.endswith('.txt'):
            try:
                doc_id = int(filename[5:-4])
                with open(os.path.join(lemmas_dir, filename), 'r', encoding='utf-8') as f:
                    lemmas = f.read().split()

                for lemma in set(lemmas):
                    inverted_index[lemma].append(doc_id)

            except Exception as e:
                print(f"Ошибка обработки файла {filename}: {e}")

    for lemma in inverted_index:
        inverted_index[lemma].sort()

    return inverted_index


def save_inverted_index(inverted_index):
    sorted_index = dict(sorted(inverted_index.items(), key=lambda item: item[0]))

    with open('inverted_index.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_index, f, ensure_ascii=False, indent=2)


def main():
    inverted_index = build_inverted_index()
    save_inverted_index(inverted_index)

    print(f"Инвертированный индекс успешно построен и сохранен в inverted_index.json")
    print(f"Всего уникальных лемм: {len(inverted_index)}")


if __name__ == "__main__":
    main()
