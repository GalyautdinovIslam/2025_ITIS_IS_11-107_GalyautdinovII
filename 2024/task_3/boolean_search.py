import collections

import pymorphy3

index_file = './index.txt'  # from task_1
indexes_file = './indexes.txt'
UTF_8 = 'utf-8'

AND = 'and'
OR = 'or'
NOT = 'not'


def init():
    all_indexes = set()
    lemma_indexes = collections.defaultdict(set)
    with open(indexes_file, 'r', encoding=UTF_8) as file:
        lines = file.readlines()
        for line in lines:
            elements = line.split()
            if len(elements) > 1:
                key = elements[0]
                indexes = set(elements[1:])
                all_indexes = all_indexes.union(indexes)
                lemma_indexes[key] = indexes

    urls = collections.defaultdict(str)
    with open(index_file, 'r', encoding=UTF_8) as file:
        lines = file.readlines()
        for line in lines:
            elements = line.split()
            if len(elements) == 2:
                key = elements[0]
                url = elements[1]
                urls[key] = url

    return lemma_indexes, urls, all_indexes


def get_normalized(morphy, word):
    return morphy.parse(word)[0].normal_form


def process(datas, all_indexes):
    result = set()

    processing = []
    is_need_invert = False
    for i in range(len(datas)):
        if datas[i] != NOT:
            if is_need_invert:
                processing.append(all_indexes.difference(datas[i]))
            else:
                processing.append(datas[i])
            is_need_invert = False
        else:
            is_need_invert = not is_need_invert

    for i in range(len(processing)):
        if i == 0:
            result = result.union(processing[i])
        elif i % 2 == 1:
            if processing[i] == AND:
                result = result.intersection(processing[i + 1])
            elif processing[i] == OR:
                result = result.union(processing[i + 1])

    return result


def search(morphy, string, lemma_indexes, all_indexes):
    string = string.replace('(', ' ( ').replace(')', ' ) ').split()

    stack = []
    result = []

    for word in string:
        word = word.lower()
        if word == '(':
            stack.append(result)
            result = []
        elif word == ')':
            processed = process(result, all_indexes)
            result = stack.pop()
            result.append(processed)
        else:
            if word != AND and word != OR and word != NOT:
                normalized = get_normalized(morphy, word)
                result.append(lemma_indexes[normalized])
            else:
                result.append(word)

    return process(result, all_indexes)


def main():
    lemma_indexes, urls, all_indexes = init()
    morphy = pymorphy3.MorphAnalyzer()

    while True:
        indexes = search(morphy, input('Ваш запрос: '), lemma_indexes, all_indexes)
        for index in indexes:
            print(urls.get(index))


if __name__ == '__main__':
    main()
