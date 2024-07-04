import pandas as pd
from pandas.core.series import Series
import spacy
import jaconv

nlp = spacy.load('ja_ginza')

try:
    movie_df = pd.read_csv('movie.csv')
except Exception:
    print('映画データを読み込めませんでした。')
    exit(0)

try:
    attr_df = pd.read_csv('attr.csv')
except Exception:
    print('属性データを読み込めませんでした。')
    exit(0)

try:
    relation_df = pd.read_csv('relation.csv')
except Exception:
    print('関係データを読み込めませんでした。')
    exit(0)

try:
    review_df = pd.read_csv('review.csv')
except Exception:
    print('レビューデータを読み込めませんでした。')
    exit(0)

try:
    analyze_df = pd.read_csv('analyze.csv')
except Exception:
    analyze_df = pd.DataFrame(columns=['review_id', 'movie_id', 'attr_id', 'obj', 'value'])

# 文字列の正規化
def normalize(text: str) -> str:
    text = jaconv.z2h(text, kana=False, ascii=True, digit=True)
    text = jaconv.h2z(text, kana=True, ascii=False, digit=False)
    text = jaconv.kata2hira(text)

    return text

# 属性名の分割
def split_attr(attr_id, name) -> dict:
    doc = nlp(name)
    dic = {normalize(spl.text): attr_id for spl in doc}
    return dic

# 属性名辞書
def attr_to_id(movie_id: int):
    attr_to_id = {}
    for index, rel in relation_df[relation_df['movie_id'] == movie_id].iterrows():
        attr = attr_df[attr_df['attr_id'] == rel['attr_id']]
        attr_id = attr.iat[0, 0]
        attr_name = attr.iat[0, 2]
        attr_to_id = {**{normalize(attr_name): attr_id}, **split_attr(attr_id, attr_name), **attr_to_id}

        sub_label = rel['sub_label']
        if sub_label != '!none':
            attr_to_id = {**{normalize(sub_label): attr_id}, **split_attr(attr_id, sub_label), **attr_to_id}
    return attr_to_id

# データフレームの更新
def register_data(review_id: int, movie_id: int, attr_id: int, obj: list, value:list) -> None:
    global analyze_df
    for o in obj:
        for v in value:
            data = pd.DataFrame([[review_id, movie_id, attr_id, o, v]], columns=analyze_df.columns)
            analyze_df = pd.concat([analyze_df, data], ignore_index=True)

# 解析
def analyze(review: Series, attr_dic: dict, debug: bool=False) -> None:
    review_id = review['review_id']
    movie_id = review['movie_id']
    text = review['text']
    print(text)

    text_split = text.split('\n')
    for t in text_split:
        doc = nlp(t)
        ent_list = [ent for ent in doc.ents]
        
        if debug:
            print()
            for t in doc:
                print(t.i, t.text, t.lemma_, t.norm_, t.pos_, t.tag_, t.dep_, t.head.i)

        for attr in ent_list:
            attr_name = normalize(attr.text)
            if attr_name in attr_dic.keys():
                attr_id = attr_dic[attr_name]
            else:
                continue
            token = doc[attr.start]

            obj = []
            value = []
            prev_dep = ''
            while True:
                if token.dep_ == 'nmod':
                    token = token.head
                    if token.pos_ == 'PROPN' or ('人名' in token.tag_):
                        while token.dep_ == 'compound':
                            token = token.head
                        continue
                    else:
                        prev_dep = 'nmod'
                        obj.append(token.norm_)
                        continue
                elif token.dep_ == 'nsubj':
                    token = token.head
                    if token.lemma_ == 'なる':
                        advcl = [t for t in token.children if t.dep_ == 'advcl']
                        if len(advcl) > 0:
                            value.append(advcl[0].norm_)
                    else:
                        value.append(token.norm_)
                    prev_dep = 'nsubj'
                    continue
                elif token.dep_ == 'acl':
                    token = token.head
                    prev_dep = 'acl'
                    value.append(token.norm_)
                    continue
                elif token.dep_ == 'advcl':
                    token = token.head
                    value.append(token.norm_)
                    if prev_dep == 'advcl':
                        break
                    else:
                        prev_dep = 'advcl'
                        continue
                elif token.dep_ == 'obl':
                    token = token.head
                    prev_dep = 'obl'
                    value.append(token.norm_)
                    continue
                elif token.dep_ == 'compound':
                    token = token.head
                    continue
                elif token.dep_ == 'ROOT':
                    break
                else:
                    break
                    
            if debug:
                print(attr.orth_, attr.label_, attr.start, attr.end)
                print(f'obj: {obj}')
                print(f'value: {value}')

            if len(obj) * len(value) == 0: continue
            register_data(review_id, movie_id, attr_id, obj, value)


unanalyzed_review_list = review_df[review_df['is_analyzed'] == False]
movie_ids = set(unanalyzed_review_list['movie_id'].to_list())

for movie_id in movie_ids:
    attr_dic = attr_to_id(movie_id)

    review_list = unanalyzed_review_list[unanalyzed_review_list['movie_id'] == movie_id]
    for index, row in review_list.iterrows():
        print(f'===== review_id: {row["review_id"]} =====')
        analyze(row, attr_dic)
        review_df.loc[review_df.review_id == row['review_id'], 'is_analyzed'] = True

print(analyze_df)

review_df.to_csv('review.csv', index=False)
analyze_df.to_csv('analyze.csv', index=False)