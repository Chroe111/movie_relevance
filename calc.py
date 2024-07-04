import numpy as np
import pandas as pd
import spacy
import pickle

nlp = spacy.load('ja_ginza')

word_to_cluster = {}
sent_dic = {}

# 映画データの読み込み
try:
    movie_df = pd.read_csv('movie.csv')
except Exception:
    print('映画データを読み込めませんでした。')
    exit(0)

# 関係データの読み込み
try:
    relation_df = pd.read_csv('relation.csv')
except Exception:
    print('関係データを読み込めませんでした。')
    exit(0)

# 解析データの読み込み
try:
    analyze_df = pd.read_csv('analyze.csv')
except Exception:
    print('解析データを読み込めませんでした。')
    exit(0)

# cos類似度
def cos_sim(v1, v2):
    norm_mult = np.linalg.norm(v1) * np.linalg.norm(v2)
    if norm_mult == 0:
        return 0.0
    else:
        return np.dot(v1, v2) / norm_mult

# cos類似度（正規化）
def cos_sim_norm(v1, v2):
    return (cos_sim(v1, v2) + 1) / 2

# 重み計算
def attr_weight(movie_id1: int, movie_id2: int, attr_id: int):
    movie1_df = analyze_df[(analyze_df['movie_id'] == movie_id1) & (analyze_df['attr_id'] == attr_id)]
    movie2_df = analyze_df[(analyze_df['movie_id'] == movie_id2) & (analyze_df['attr_id'] == attr_id)]

    movie1_review_num = len(set(movie1_df['review_id'].to_list()))
    movie2_review_num = len(set(movie2_df['review_id'].to_list()))

    if movie1_review_num == 0:
        return 0
    else:
        return float(movie2_review_num / movie1_review_num)

# 属性リスト
def attr_list(movie_id: int):
    l = relation_df[(relation_df['movie_id'] == movie_id)]['attr_id'].to_list()
    return l

# 評価対象-評価値ベクトル
def obj_value_vec(movie_id: int, attr_id: int):
    df = analyze_df[(analyze_df['movie_id'] == movie_id) & (analyze_df['attr_id'] == attr_id)]
    vec = np.zeros(len(set(word_to_cluster.values())))

    for index, row in df.iterrows():
        obj = row['obj']
        value = row['value']
        if obj in word_to_cluster.keys() and value in sent_dic.keys():
            vec[word_to_cluster[obj]] += sent_dic[value]
    return vec

# レビューを参照しない関連度
def similar_common_attrs(movie_id1: int, movie_id2: int):
    attr_id_set1 = set(attr_list(movie_id1))
    attr_id_set2 = set(attr_list(movie_id2))

    sim = float(len(attr_id_set1 & attr_id_set2) / len(attr_id_set1))

    return sim

# レビューを参照する関連度
def similar_attr_evaluate(movie_id1: int, movie_id2: int):
    attr_id_list1 = attr_list(movie_id1)
    attr_id_list2 = attr_list(movie_id2)
    attr_ids_common = set(attr_id_list1) & set(attr_id_list2)

    attrs_evaluates = {attr_id: cos_sim(obj_value_vec(movie_id1, attr_id), obj_value_vec(movie_id2, attr_id)) for attr_id in attr_ids_common}

    return attrs_evaluates

# 総合的な関連度
def relavance(movie_id1: int, movie_id2: int, weight: float=0.5):
    common_attrs_sim = similar_common_attrs(movie_id1, movie_id2)
    evals = similar_attr_evaluate(movie_id1, movie_id2)
    evals_not_0 = [(value + 1) / 2 for value in evals.values() if value != 0.0]
    if len(evals_not_0) == 0:
        eval_sim = 0.0
    else:
        eval_sim = float(sum(evals_not_0) / len(evals_not_0))
    
    total_sim = weight * common_attrs_sim + (1 - weight) * eval_sim

    return total_sim

# 初期化
def init():
    global word_to_cluster
    global sent_dic
    with open('word_cluster.pickle', 'rb') as f:
        word_to_cluster = pickle.load(f)
    with open('sent_dic.pickle', 'rb') as f:
        sent_dic = pickle.load(f)

init()

print()
movie_id1 = int(input('movie_id1: '))
movie_id2 = int(input('movie_id2: '))
print()

print(similar_common_attrs(movie_id1, movie_id2))
print(similar_attr_evaluate(movie_id1, movie_id2))
print(relavance(movie_id1, movie_id2, weight=0.6))