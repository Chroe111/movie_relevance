from urllib.parse import quote
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import re

# 正規化
def normalize(s: str):
    s = re.sub('（\d{4}）', '', s)
    s = s.translate(str.maketrans({' ': '', '　': '', '/': '', '／': '', ':': '', '：': '', '・': '', '.': '', ',': ''}))
    print(s)
    return s

# 映画テーブルの読み込み
try:
    movie_df = pd.read_csv('movie.csv')
except Exception:
    print('映画データを読み込めませんでした。')
    exit(0)

# レビューテーブルの読み込み
try:
    review_df = pd.read_csv('review.csv')
except Exception:
    review_df = pd.DataFrame(columns=['review_id', 'review_id_fil', 'movie_id', 'user_id', 'date', 'rate', 'text', 'is_analyzed'])

# ユーザテーブルの読み込み
try:
    user_df = pd.read_csv('user.csv')
except Exception:
    user_df = pd.DataFrame(columns=['user_id', 'user_id_fil', 'name'])

# 映画情報の取り出し
movie_id_str = input('映画idを入力：')

try:
    movie_id = int(movie_id_str)
    movie = movie_df[movie_df['movie_id'] == movie_id]
    movie_id_fil = movie.iat[0, 2]
    print(f'{movie.iat[0, 3]} (映画id: {movie_id})')
    if movie_id_fil == -1:
        print('Filmarksに存在しない映画です。')
        exit(0)
except Exception:
    print('入力された値が不正です。')
    exit(0)

i = 0
url_fil_0 = f'https://filmarks.com/movies/{movie_id_fil}'

while i < 300:
    i += 1

    # ページの表示
    try:
        url_fil = url_fil_0 + f'?page={i}'
        responce_fil = requests.get(url_fil)
        dom_fil = bs(responce_fil.text, 'html.parser')
    except Exception:
        print('通信エラー')
        break

    # レビュー・ユーザ情報の取得
    review_list = dom_fil.find_all('div', attrs={'class': 'c-media__content'})
    for review in review_list:
        review_id_fil = int(review.h4.a.get('href').split('/')[-1])
        if review_id_fil in review_df['review_id_fil'].to_list():
            print('登録済み')
            continue

        url_review = f'https://filmarks.com/movies/{movie_id_fil}/reviews/{review_id_fil}'
        responce_rev = requests.get(url_review)
        dom_rev = bs(responce_rev.text, 'html.parser')

        # ユーザid
        user_id_fil = dom_rev.find('div', attrs={'class': 'c-media__avator'}).a.get('href').split('/')[-1]
        # 投稿日時
        date = dom_rev.find('time', attrs={'class': 'c-media__date'}).text
        # 評価値
        rate_str = dom_rev.find('div', attrs={'class': 'c-rating__score'}).text
        if rate_str == '-':
            rate = 0.0
        else:
            rate = float(rate_str)
        # レビュー本文
        text = dom_rev.find('div', attrs={'class': 'p-mark__review'})
        for br in text.select('br'):
            br.replace_with('\n')
        ul = text.find('ul', attrs={'class': 'p-timeline-mark__tags'})
        if ul is not None:
            ul.decompose()
        text = text.text

        if user_id_fil in user_df['user_id_fil'].to_list():
            user_id = user_df[user_df['user_id_fil'] == user_id_fil].iat[0, 1]
        else:
            user_id = user_df.shape[0]
            name = dom_rev.find('div', attrs={'class': 'c-media__avator'}).a.img.get('alt')

            user_data = pd.DataFrame([[user_id, user_id_fil, name]], columns=user_df.columns)
            user_df = pd.concat([user_df, user_data], ignore_index=True)

        review_data = pd.DataFrame([[review_df.shape[0], review_id_fil, movie_id, user_id, date, rate, text, False]], columns=review_df.columns)
        print(review_data)
        review_df = pd.concat([review_df, review_data], ignore_index=True)
    
    print('\n休憩中...')
    time.sleep(7)
    print()

# 結果の表示
print(user_df)
print(review_df)

# csv出力
user_df.to_csv('user.csv', index=False)
review_df.to_csv('review.csv', index=False)