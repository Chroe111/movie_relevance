import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import urllib.parse
import re

# 正規化
def normalize(s: str):
    s = re.sub('（\d{4}）', '', s)
    s = s.translate(str.maketrans({' ': '', '　': '', '/': '', '／': '', ':': '', '：': '', '・': '', '.': '', ',': ''}))
    print(s)
    return s

# 映画テーブルの読み込み
try:
    movie_df = pd.read_csv('movie.csv', dtype={'movie_id': int, 'movie_id_com':int, 'movie_id_fil': int, 'title': str})
except Exception:
    movie_df = pd.DataFrame(columns=['movie_id', 'movie_id_com', 'movie_id_fil', 'title']).astype(
        {'movie_id': int, 'movie_id_com':int, 'movie_id_fil': int, 'title': str}
    )

# 関係テーブルの読み込み
try:
    relation_df = pd.read_csv('relation.csv', dtype={'movie_id': int, 'attr_id': int, 'label': str, 'sub_label': str})
except Exception:
    relation_df = pd.DataFrame(columns=['movie_id', 'attr_id', 'label', 'sub_label']).astype(
        {'movie_id': int, 'attr_id': int, 'label': str, 'sub_label': str}
    )

# 属性テーブルの読み込み
try:
    attr_df = pd.read_csv('attr.csv', dtype={'attr_id': int, 'attr_id_com': int, 'name': str})
except Exception:
    attr_df = pd.DataFrame(columns=['attr_id', 'attr_id_com', 'name']).astype(
        {'attr_id': int, 'attr_id_com': int, 'name': str}
    )

# ページの読み込み
url_com = input('映画ドットコムのURLを入力：')
movie_id_com = int(url_com.split('/')[-2])

if movie_id_com in movie_df['movie_id_com'].to_list():
    print('登録済み')
    exit(0)

responce_com = requests.get(url_com)
dom_com = bs(responce_com.text, 'html.parser')

# 映画情報の取得
title = dom_com.find('h1', attrs={'class': 'page-title'}).text

url_fil = f'https://filmarks.com/search/movies?q={urllib.parse.quote(title)}'
responce_fil = requests.get(url_fil)
dom_fil = bs(responce_fil.text, 'html.parser')

movie_cand_list = dom_fil.find_all('div', attrs={'class': 'p-content-cassette__info'})

movie_id_fil = -1
for cand in movie_cand_list:
    title_cand = cand.find('h3', attrs={'p-content-cassette__title'}).text
    if normalize(title_cand) == normalize(title):
        movie_id_fil = cand.find("a", attrs={"p-content-cassette__readmore"}).get("href").split("/")[2]
        break

movie_id = movie_df.shape[0]
movie_data = pd.DataFrame([[movie_id, movie_id_com, movie_id_fil, title]], columns=movie_df.columns)
movie_df = pd.concat([movie_df, movie_data], ignore_index=True)

# スタッフの取得
for tag in dom_com.find('dl', attrs={'class': 'movie-staff'}).children:
    if tag.name == 'dt':
        label = tag.text
    elif tag.name == 'dd':
        if tag.a is not None:
            name = tag.a.text
            attr_id_com = int(tag.a.get('href').split('/')[2])

            if attr_id_com in attr_df['attr_id_com'].to_list():
                attr_id = attr_df[attr_df['attr_id_com'] == attr_id_com].iat[0, 0]
            else:
                attr_id = attr_df.shape[0]
                attr_data = pd.DataFrame([[attr_id, attr_id_com, name]], columns=attr_df.columns)
                attr_df = pd.concat([attr_df, attr_data], ignore_index=True)

        else:
            name = tag.text

            if name in attr_df['name'].to_list():
                attr_id = attr_df[attr_df['name'] == name].iat[0, 0]
            else:
                attr_id = attr_df.shape[0]
                attr_data = pd.DataFrame([[attr_id, attr_id_com, name]], columns=attr_df.columns)
                attr_df = pd.concat([attr_df, attr_data], ignore_index=True)

        relation_data = pd.DataFrame([[movie_id, attr_id, label, '!none']], columns=relation_df.columns)
        relation_df = pd.concat([relation_df, relation_data], ignore_index=True)

# キャストの取得
for tag in dom_com.find('ul', attrs={'class': 'movie-cast'}).children:
    if tag.name == 'li':
        if tag.a is not None:
            name = tag.a.p.span.text
            attr_id_com = int(tag.a.get('href').split('/')[2])
            if tag.a.p.small is not None:
                sub_label = tag.a.p.small.text
            else:
                sub_label = '!none'

            if attr_id_com in attr_df['attr_id_com'].to_list():
                attr_id = attr_df[attr_df['attr_id_com'] == attr_id_com].iat[0, 0]
            else:
                attr_id = attr_df.shape[0]
                attr_data = pd.DataFrame([[attr_id, attr_id_com, name]], columns=attr_df.columns)
                attr_df = pd.concat([attr_df, attr_data], ignore_index=True)

        else:
            name = tag.span.p.span.text
            if tag.span.p.small is not None:
                sub_label = tag.span.p.small.text
            else:
                sub_label = '!none'

            if name in attr_df['name'].to_list():
                attr_id = attr_df[attr_df['name'] == name].iat[0, 0]
            else:
                attr_id = attr_df.shape[0]
                attr_data = pd.DataFrame([[attr_id, attr_id_com, name]], columns=attr_df.columns)
                attr_df = pd.concat([attr_df, attr_data], ignore_index=True)

        label = '出演'

        relation_data = pd.DataFrame([[movie_id, attr_id, label, sub_label]], columns=relation_df.columns)
        relation_df = pd.concat([relation_df, relation_data], ignore_index=True)

# 結果の表示
print(movie_df)
print(attr_df)
print(relation_df)

# csv書き出し
movie_df.to_csv('movie.csv', index=False)
attr_df.to_csv('attr.csv', index=False)
relation_df.to_csv('relation.csv', index=False)