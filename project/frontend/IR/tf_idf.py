import math
import os
import pickle
import re
import string
import time

import nltk

try:
    from nltk import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk.probability import FreqDist
    from nltk.stem import PorterStemmer, SnowballStemmer
except:
    nltk.download("stopwords")
    nltk.download("punkt")

# cleared text


def remove_punctuation(text):
    words = [
        char for char in text.split(" ")
        if char not in string.punctuation
    ]
    return " ".join(words)


def remove_special_character(text):  # step 1
    processed_text = text.lower()
    text = remove_punctuation(text)
    processed_text = processed_text.replace("’", "'")
    processed_text = processed_text.replace("“", '"')
    processed_text = processed_text.replace("”", '"')
    non_words = re.compile(r"[^A-Za-z']+")
    processed_text = re.sub(non_words, ' ', processed_text)

    return processed_text


def remove_stem(text):  # step 2
    porter = PorterStemmer()
    token_words = word_tokenize(text)
    words = [
        porter.stem(word) for word in token_words
    ]
    return " ".join(words)


def remove_stopwords(text):  # step 3
    stop_words = set(stopwords.words('english'))
    # xóa stopwords
    words = [
        w for w in text.split(" ")
        if w not in stop_words
    ]
    return ' '.join(words)


def clear_text(text):
    # processing
    text = text.lower()
    text = remove_special_character(text)
    text = remove_stem(text)
    text = remove_stopwords(text)

    return text


def get_words_from_text(text):
    words = [w for w in text.split()]
    return words


def get_words_from_text_in_vocabulary(text, vocal):
    words = [w for w in text.split() if w in vocal]
    return words

# Read data and build index


def get_text_from_file(filename):
    with open(filename, encoding='cp1252', mode='r') as f:
        text = f.read()
    f.close()
    return text


def build_inverted_index(docs_path):
    arr = dict()
    arr_file = []
    for id, doc_file in enumerate(os.listdir(docs_path)):
        arr_file.append(doc_file.split('.')[0])
        filename = os.path.join(docs_path, doc_file)
        text = get_text_from_file(filename)
        words = get_words_from_text(clear_text(text))
        len_word_in_doc = len(words)
        for word in words:
            if word not in arr.keys():
                arr[word] = {'count': 1, 'num_doc': 1, 'index': []}
                arr[word]['index'].append([id, 1, len_word_in_doc])
            else:
                arr[word]['count'] += 1
                if arr[word]['index'][-1][0] == id:
                    arr[word]['index'][-1][1] += 1
                else:
                    arr[word]['index'].append([id, 1, len_word_in_doc])
                    arr[word]['num_doc'] += 1
    return arr, arr_file


def build_inverted_index_from_database():
    from data.models import Data
    arr = dict()
    arr_file = []
    allFiles = Data.objects.all()
    for id, file in enumerate(allFiles):
        arr_file.append(file.id)
        text = file.text
        words = get_words_from_text(clear_text(text))
        len_word_in_doc = len(words)
        for word in words:
            if word not in arr.keys():
                arr[word] = {'count': 1, 'num_doc': 1, 'index': []}
                arr[word]['index'].append([id, 1, len_word_in_doc])
            else:
                arr[word]['count'] += 1
                if arr[word]['index'][-1][0] == id:
                    arr[word]['index'][-1][1] += 1
                else:
                    arr[word]['index'].append([id, 1, len_word_in_doc])
                    arr[word]['num_doc'] += 1

    return arr, arr_file

# compute tf-idf


def calc_tf_idf(tf, len_word_in_doc, count, num_doc):
    return math.log(1 + tf) * math.log(1 + count / num_doc)


def convert_tf_idf_arr(arr):
    for keys, values in arr.items():
        arr[keys]['index'] = [
            [
                item[0],
                calc_tf_idf(
                    item[1],
                    item[2],
                    values['count'],
                    values['num_doc']
                )
            ] for item in values['index']
        ]
    return arr

# find docs train length


def get_vector_length_of_docs(tf_idf_index):
    docs_length = dict()
    for key, values in tf_idf_index.items():
        for value in values['index']:
            if value[0] not in docs_length.keys():
                docs_length[value[0]] = math.pow(value[1], 2)
            else:
                docs_length[value[0]] += math.pow(value[1], 2)
    for key in docs_length.keys():
        docs_length[key] = math.sqrt(docs_length[key])
    return docs_length

# train data


def get_data_train():
    INPUT_ROOT = os.path.abspath(os.path.dirname(__file__))
    try:
        # clone if files exist
        pkl_file = open(os.path.join(
            INPUT_ROOT, 'input/data/inverted_1.pickle'), 'rb')
        tf_idf_index = pickle.load(pkl_file)
        docs_length = pickle.load(pkl_file)
        pkl_file.close()

        pkl_file = open(os.path.join(
            INPUT_ROOT, 'input/data/index_1.pickle'), 'rb')
        arr_file = pickle.load(pkl_file)
        pkl_file.close()

    except:
        # create if file doesn't exist'
        docs_path = os.path.join(INPUT_ROOT, "input/Cranfield")
        arr, arr_file = build_inverted_index(docs_path)
        tf_idf_index = convert_tf_idf_arr(arr)
        docs_length = get_vector_length_of_docs(tf_idf_index)

        with open(os.path.join(INPUT_ROOT, 'input', 'data', 'inverted_1.pickle'), mode='wb') as f:
            pickle.dump(tf_idf_index, f)
            pickle.dump(docs_length, f)
        f.close()

        with open(os.path.join(INPUT_ROOT, 'input', 'data', 'index_1.pickle'), mode='wb') as f:
            pickle.dump(arr_file, f)
        f.close()

    return tf_idf_index, docs_length, arr_file


def get_data_train_from_database():
    from data.models import Data
    INPUT_ROOT = os.path.abspath(os.path.dirname(__file__))
    try:
        pkl_file = open(os.path.join(
            INPUT_ROOT, 'input/data/inverted_2.pickle'), 'rb')
        tf_idf_index = pickle.load(pkl_file)
        docs_length = pickle.load(pkl_file)
        pkl_file.close()

        pkl_file = open(os.path.join(
            INPUT_ROOT, 'input/data/index_2.pickle'), 'rb')
        arr_file = pickle.load(pkl_file)
        pkl_file.close()

    except:
        arr, arr_file = build_inverted_index_from_database()
        tf_idf_index = convert_tf_idf_arr(arr)
        docs_length = get_vector_length_of_docs(tf_idf_index)

        with open(os.path.join(INPUT_ROOT, 'input', 'data', 'inverted_2.pickle'), mode='wb') as f:
            pickle.dump(tf_idf_index, f)
            pickle.dump(docs_length, f)
        f.close()

        with open(os.path.join(INPUT_ROOT, 'input', 'data', 'index_2.pickle'), mode='wb') as f:
            pickle.dump(arr_file, f)
        f.close()

    return tf_idf_index, docs_length, arr_file

# query


def get_relevant_ranking_for_query(query, tf_idf_index, docs_length, arr_file):
    # lấy từ trong query
    q_words = get_words_from_text_in_vocabulary(
        clear_text(query), tf_idf_index.keys())

    if len(q_words) == 0:
        return []

    # đếm từ
    q_word_with_count = dict()
    for word in q_words:
        if word not in q_word_with_count.keys():
            q_word_with_count[word] = 1
        else:
            q_word_with_count[word] += 1

    if len(q_word_with_count) == 0:
        return []

    # compute tf-idf query
    tf_idf_for_querry = {
        word: calc_tf_idf(
            q_word_with_count[word],
            len(q_word_with_count),
            tf_idf_index[word]['count'],
            tf_idf_index[word]['num_doc']
        )
        for word in q_word_with_count.keys()
        if word in tf_idf_index.keys()
    }
    # find q length
    q_length = 0

    # multiply
    relevant_between_words = {
        word: [[
            item[0],
            item[1] * tf_idf_for_querry[word]
        ] for item in tf_idf_index[word]['index']
        ]
        for word in q_word_with_count.keys()
        if word in tf_idf_index.keys()
    }

    # find query length
    for key, value in tf_idf_for_querry.items():
        q_length += math.pow(value, 2)
    q_length = math.sqrt(q_length)

    # count term
    q_score = dict()
    for _, value in relevant_between_words.items():
        for i in value:
            if i[0] not in q_score.keys():
                q_score[i[0]] = i[1]
            else:
                q_score[i[0]] += i[1]

    # computer norm

    for key in q_score.keys():
        q_score[key] = q_score[key] / (docs_length[key] * (q_length + 0.01))

    q_score = {
        key: value
        for key, value in q_score.items()
        if value >= 0.01
    }

    x_retrieved = sorted(
        q_score.items(), key=lambda item: item[1], reverse=True)

    return x_retrieved


def open_queries():
    INPUT_ROOT = os.path.abspath(os.path.dirname(__file__))
    result = dict()
    for i in open(os.path.join(INPUT_ROOT, "input/query.txt")).readlines():
        t = i.split('\t')
        result[t[0]] = t[1]
    return result

# get data truth


def get_data_ground_truth():
    path = os.path.join('input', 'RES')
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

# precision


def get_Average_Precision(x_retrieved, relevant_docs, arr_file):
    # find R_Precision value
    validation_result = {'R': [], 'P': []}
    count = 0
    for i in range(len(relevant_docs)):
        if arr_file[int(x_retrieved[i][0])] in relevant_docs:
            count += 1
        validation_result['R'].append((count / len(relevant_docs)))
        validation_result['P'].append((count / (i + 1)))
    return sum(validation_result['P']) / len(validation_result['P'])

# calc MAP


def main():
    tf_idf_index, docs_length, arr_file = get_data_train()

    queries = open_queries()
    list_of_x_retrieved = dict()
    for key, value in queries.items():
        list_of_x_retrieved[key] = get_relevant_ranking_for_query(
            value, tf_idf_index, docs_length, arr_file)

    # Bắt đầu đánh giá mô hình.
    data_ground_truth = get_data_ground_truth()

    Average_precision_of_all_x_retrieved = {
        key: get_Average_Precision(
            value, data_ground_truth[key], arr_file)
        for key, value in list_of_x_retrieved.items()
    }
    MAP = 0

    for key, value in Average_precision_of_all_x_retrieved.items():
        MAP += value
    MAP = MAP / len(Average_precision_of_all_x_retrieved)
    print("MAP:", MAP)


if __name__ == "__main__":
    t0 = time.clock()
    main()
    t1 = time.clock() - t0
    print("Time elapsed: ", t1)
