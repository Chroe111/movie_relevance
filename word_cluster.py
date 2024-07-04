import numpy as np
import pandas as pd
from gensim.models import KeyedVectors
from sklearn.cluster import KMeans
import pickle

# 解析データの読み込み
try:
    analyze_df = pd.read_csv('analyze.csv')
except Exception:
    print('解析データを読み込めませんでした。')
    exit(0)


# chiVeの読み込み
def load_chive():
    print('単語ベクトルを読み込み中...')
    chive = KeyedVectors.load('chive-1.2-mc30_gensim/chive-1.2-mc30.kv')
    print('単語ベクトルの読み込み完了')
    return chive

# 単語のクラスタリング
def word_to_cluster(n_cluster: int):
    word_list = analyze_df['obj'].to_list()
    chive = load_chive()

    word_to_id = {}
    obj_vec_list = []
    for word in word_list:
        if word in word_to_id.keys():
            continue
        if word in chive:
            word_to_id[word] = len(word_to_id)
            obj_vec_list.append(chive[word])
    obj_vec = np.array(obj_vec_list)

    pred = KMeans(n_clusters=n_cluster, n_init=15).fit_predict(obj_vec)
    word_to_cluster = {word: pred[word_to_id[word]] for word in word_to_id.keys()}

    return word_to_cluster

n_cluster = int(input('クラスタ数を指定:'))

cluster = word_to_cluster(n_cluster)

cluster_to_word = {}
for word in cluster.keys():
    if cluster[word] not in cluster_to_word.keys():
        cluster_to_word[cluster[word]] = []
    cluster_to_word[cluster[word]].append(word)
for i in range(len(cluster_to_word)):
    print(f'{i}: {cluster_to_word[i]}')

print(f'ratio: {float(n_cluster / len(cluster))}')

with open('word_cluster.pickle', 'wb') as f:
    pickle.dump(cluster, f)