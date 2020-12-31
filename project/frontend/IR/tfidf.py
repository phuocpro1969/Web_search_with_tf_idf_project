import math
import os
import pickle
import re
import string
import time

from data.models import Data
from nltk import sent_tokenize, stem, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.stem import PorterStemmer, SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer

INPUT_FILES = "./input/Cranfield"

# Clear text


def remove_special_character(text):
    processed_text = text.lower()
    processed_text = processed_text.replace("’", "'")
    processed_text = processed_text.replace("“", '"')
    processed_text = processed_text.replace("”", '"')

    non_words = re.compile(r"[^A-Za-z']+")
    processed_text = re.sub(non_words, ' ', processed_text)

    return processed_text


def remove_stopwords(text):  # step 1
    stop_words = set(stopwords.words('english'))
    # xóa stopwords
    words = [
        w for w in text.split(" ")
        if w not in stop_words
    ]
    return ' '.join(words)


def remove_punctuation(text):  # step 2
    words = [
        char for char in text.split(" ")
        if char not in string.punctuation
    ]
    return " ".join(words)


def remove_stem(text):  # step 3
    porter = PorterStemmer()
    token_words = word_tokenize(text)
    words = [
        porter.stem(word) for word in token_words
    ]
    return " ".join(words)


def clear_text(text):
    # processing
    text = text.lower()
    text = remove_stopwords(text)
    text = remove_special_character(text)
    text = remove_punctuation(text)
    text = remove_stem(text)

    return text

# Read data


def get_text_from_file(filename):
    with open(filename, encoding='cp1252', mode='r') as f:
        text = f.read()
    f.close()
    return text


def read_data():
    data = []
    arr_file = []
    for doc_file in os.listdir(INPUT_FILES):
        filename = os.path.join(INPUT_FILES, doc_file)
        text = get_text_from_file(filename)
        if len(text) == 0:
            continue
        arr_file.append(doc_file.split(".")[0])
        data.append(clear_text(text))
    return data, arr_file


def read_data_from_database():
    data = []
    arr_file = []
    allFiles = Data.objects.all()
    for file in allFiles:
        text = file.text
        words = get_words_from_text(text)
        if len(text) == 0:
            continue
        arr_file.append(file.id)
        data.append(clear_text(text))
    return data, arr_file

# build index, tf_idf arrays


def build_tf_idf_sklearn(data):
    tfidfVectorizer = TfidfVectorizer(
        analyzer='word', ngram_range=(1, 6), min_df=0.01, sublinear_tf=True,
        use_idf=True, smooth_idf=True
    )

    tfidf_matrix = tfidfVectorizer.fit_transform(data)
    feature_names = tfidfVectorizer.get_feature_names()

    # init
    tfidf_scores = dict()
    for index in feature_names:
        tfidf_scores[index] = []
    for index in range(len(data)):
        feature_index = tfidf_matrix[index, :].nonzero()[1]
        for x in feature_index:
            tfidf_scores[feature_names[x]].append(
                [index, tfidf_matrix[index, x]])
    return tfidfVectorizer, tfidf_scores


def open_queries():
    result = dict()
    for i in open("./input/query.txt").readlines():
        t = i.split('\t')
        result[t[0]] = t[1]
    return result


def get_data_ground_truth():
    path = os.path.join('./input', 'RES')
    data = dict()

    for file in os.listdir(path):
        filename = os.path.join(path, file)
        text = get_text_from_file(filename)
        text = text.rstrip('\n')
        cutLine = text.split('\n')
        for index, line in enumerate(cutLine):
            # cutTab[1] chua can quan tam toi do chua can dung
            cutTab = line.split('\t')
            cutSpace = cutTab[0].split(" ")
            if cutSpace[0] not in data.keys():
                data[cutSpace[0]] = [cutSpace[1]]
            else:
                data[cutSpace[0]].append(cutSpace[1])
    return data


def get_relevant_ranking_for_query(query, tfidfVectorizer, tfidf_scores, feature_names, arr_file):
    # clear query
    query = clear_text(query)
    query = " ".join(
        [
            word for word in query.split(" ")
            if word in feature_names
        ]
    )

    # compute tf_idf
    tfidf_matrix = tfidfVectorizer.fit_transform([query])
    feature_index = tfidf_matrix[0, :].nonzero()[1]

    # get vocal in query
    feature_names_query = tfidfVectorizer.get_feature_names()

    # check word in vocal
    query_tfidf_scores = dict()

    for x in feature_index:
        if feature_names_query[x] in feature_names:
            if feature_names_query[x] not in query_tfidf_scores.keys():
                query_tfidf_scores[feature_names_query[x]] = [
                    tfidf_matrix[0, x]]
            else:
                query_tfidf_scores[feature_names_query[x]].append(
                    tfidf_matrix[0, x])

    # find q length
    q_length = 0

    relevant_between_words = dict()
    # compute relevant query and data_train
    relevant_between_words = {
        word: [
            [
                item[0],
                item[1] * query_tfidf_scores[word][0]
            ] for item in tfidf_scores[word]
        ] for word in query_tfidf_scores.keys()
    }

    for key, value in query_tfidf_scores.items():
        q_length += math.pow(value[0], 2)
    q_length = math.sqrt(q_length)

    q_score = dict()
    for _, value in relevant_between_words.items():
        for i in value:
            if i[0] not in q_score.keys():
                q_score[i[0]] = i[1]
            else:
                q_score[i[0]] += i[1]
    for key in q_score.keys():
        q_score[key] = q_score[key] / (q_length + 0.01)

    # rank
    q = sorted(q_score.items(), key=lambda item: item[1], reverse=True)

    x_retrieved = []
    for i in q:
        x_retrieved.append(arr_file[i[0]])
    return x_retrieved


def get_Average_Precision(x_retrieved, relevant_docs):
    # find R_Precision value
    validation_result = {'R': [], 'P': []}
    c = 0
    for i in range(len(relevant_docs)):
        if x_retrieved[i] in relevant_docs:
            c += 1
        validation_result['R'].append((c / len(relevant_docs)))
        validation_result['P'].append((c / (i + 1)))
    return sum(validation_result['P']) / len(validation_result['P'])


def train():
    try:
        pkl_file = open(os.path.join('.\input', 'data',
                                     'train_in_database.pickle'), 'rb')
        arr_file = pickle.load(pkl_file)
        tfidfVectorizer = pickle.load(pkl_file)
        tfidf_scores = pickle.load(pkl_file)
        pkl_file.close()
    except:
        data, arr_file = read_data_from_database()
        tfidfVectorizer, tfidf_scores = build_tf_idf_sklearn(data)
        with open(os.path.join('.\input', 'data', 'train_in_database.pickle'), mode='wb') as f:
            pickle.dump(arr_file, f)
            pickle.dump(tfidfVectorizer, f)
            pickle.dump(tfidf_scores, f)
        f.close()
    return arr_file, tfidfVectorizer, tfidf_scores


def search_in_database(query, arr_file, tfidfVectorizer, tfidf_scores):
    feature_names = tfidfVectorizer.get_feature_names()
    return get_relevant_ranking_for_query(
        query, tfidfVectorizer, tfidf_scores, feature_names, arr_file
    )


def main():
    try:
        pkl_file = open(os.path.join('.\input', 'data', 'train.pickle'), 'rb')
        arr_file = pickle.load(pkl_file)
        tfidfVectorizer = pickle.load(pkl_file)
        tfidf_scores = pickle.load(pkl_file)
        pkl_file.close()
    except:
        data, arr_file = read_data()
        tfidfVectorizer, tfidf_scores = build_tf_idf_sklearn(data)
        with open(os.path.join('.\input', 'data', 'train.pickle'), mode='wb') as f:
            pickle.dump(arr_file, f)
            pickle.dump(tfidfVectorizer, f)
            pickle.dump(tfidf_scores, f)
        f.close()

    feature_names = tfidfVectorizer.get_feature_names()
    queries = open_queries()
    list_of_x_retrieved = dict()
    for key, query in queries.items():
        list_of_x_retrieved[key] = get_relevant_ranking_for_query(
            query, tfidfVectorizer, tfidf_scores, feature_names, arr_file
        )

     # Bắt đầu đánh giá mô hình.
    data_ground_truth = get_data_ground_truth()
    Average_precision_of_all_x_retrieved = \
        {
            key: get_Average_Precision(value, data_ground_truth[key])
            for key, value in list_of_x_retrieved.items()
        }
    MAP = 0
    for key, value in Average_precision_of_all_x_retrieved.items():
        MAP += value
    MAP = MAP / len(Average_precision_of_all_x_retrieved)
    print("MAP:", MAP)


if __name__ == '__main__':
    t0 = time.clock()
    main()
    t1 = time.clock() - t0
    print("Time elapsed: ", t1)
