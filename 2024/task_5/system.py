import collections
import natasha
import numpy
import os


def load_urls():
    urls = collections.defaultdict(str)
    with open('./index.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.split(' ')
            urls[int(parts[0])] = parts[1].replace('\n', '')
    return urls


def load_lemmas_tf_idf():
    lemmas_tf_idf = collections.defaultdict()
    for filename in os.listdir('./lemmas'):
        file_path = './lemmas/' + filename
        index = ''
        for char in filename:
            if char.isdigit():
                index += char
        index = int(index)
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lemma_info = collections.defaultdict()
            for line in lines:
                parts = line.split(' ')
                lemma_info[parts[0]] = [float(parts[1]), float(parts[2])]
            lemmas_tf_idf[index] = lemma_info
    return lemmas_tf_idf


def parse_request(request, segmenter, news_morph_tagger, morph_vocab):
    doc_request = natasha.Doc(request)
    doc_request.segment(segmenter)
    doc_request.tag_morph(news_morph_tagger)

    keys = []

    for token in doc_request.tokens:
        if token.pos in ['ADJ', 'NOUN', 'PRON', 'VERB']:
            token.lemmatize(morph_vocab)
            keys.append(token.lemma.lower())

    return keys


def parse_lemmas(keys, segmenter, news_morph_tagger, morph_vocab):
    lemmas = {}

    for i in range(0, len(keys)):
        doc = natasha.Doc(keys[i])
        doc.segment(segmenter)
        doc.tag_morph(news_morph_tagger)
        doc.tokens[0].lemmatize(morph_vocab)
        keys[i] = doc.tokens[0].lemma.lower()
        if keys[i] not in lemmas.keys():
            lemmas[keys[i]] = 1
        else:
            lemmas[keys[i]] += 1

    return lemmas


def calculate_tf_idf(keys, lemmas):
    tf_idf = {}
    for lemma in lemmas.keys():
        tf_idf[lemma] = lemmas[lemma] / len(keys)
    return tf_idf


def vector_search(lemmas_tf_idf, tf_idf):
    found = {}
    for i in lemmas_tf_idf.keys():
        lemmas_info = lemmas_tf_idf[i]
        lemmas_tf = []
        request_tf = []
        for lemma in lemmas_info.keys():
            lemmas_tf.append(lemmas_info[lemma][0])
            request_tf.append(tf_idf[lemma] if lemma in tf_idf.keys() else 0.0)
        if numpy.linalg.norm(request_tf) != 0:
            result = numpy.dot(lemmas_tf, request_tf) / (numpy.linalg.norm(lemmas_tf) * numpy.linalg.norm(request_tf))
            if result != 0:
                found[i] = result
    return sorted(found, reverse=False)


class System:
    def __init__(self):
        self.segmenter = natasha.Segmenter()
        self.morph_vocab = natasha.MorphVocab()
        self.news_embedding = natasha.NewsEmbedding()
        self.news_morph_tagger = natasha.NewsMorphTagger(self.news_embedding)

        self.urls = load_urls()
        self.lemmas_tf_idf = load_lemmas_tf_idf()

    def find(self, request):
        keys = parse_request(request, self.segmenter, self.news_morph_tagger, self.morph_vocab)
        lemmas = parse_lemmas(keys, self.segmenter, self.news_morph_tagger, self.morph_vocab)
        tf_idf = calculate_tf_idf(keys, lemmas)
        found = vector_search(self.lemmas_tf_idf, tf_idf)
        return [self.urls[index] for index in found]
