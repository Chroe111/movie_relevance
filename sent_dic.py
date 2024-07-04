import spacy
import pickle

nlp = spacy.load('ja_ginza')
file_name = './pa_dic/pn_ja.dic'
with open(file_name, encoding='shift-jis') as f:
    raw = f.read()

dic = {}
for line in raw.split('\n'):
    words = line.split(':')
    word = nlp(words[0])
    if len(word) == 1 and word[0].norm_ not in dic.keys():
        dic[word[0].norm_] = float(words[-1])

with open('sent_dic.pickle', 'wb') as f:
    pickle.dump(dic, f)