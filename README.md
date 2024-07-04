# 属性とその評価に着目した映画関連度の表現手法（卒業研究）
映画推薦に利用することを目的とした映画コンテンツ間の類似度を提案しました。  
以下の要素を用いて算出しています。  

- **関係している人物（スタッフやキャスト）の共通度**  
- **レビューにおけるそれらの類似度**  

つまり、共通して関係している人物が似た評価がされているコンテンツは関連度が高いと推定します。  
評価実験により、順序尺度としての有効性を示すことができました。

## モジュール
- movie.py : 映画情報をスクレイピング
- review.py : レビューをスクレイピング
- sent_dic.py: 極性辞書を整形
- word_cluster.py : 単語ベクトルをクラスタリング
- analyze.py : レビューを解析
- calc.py : 映画関連度を計算

## リファレンス
- [filmarks](https://filmarks.com/)  
- [映画ドットコム](https://eiga.com/)  
- [chiVe: Sudachi による日本語単語ベクトル](https://github.com/WorksApplications/chiVe)  
- [単語感情極性対応表(リンク切れ)](http://www.lr.pi.titech.ac.jp/~takamura/pndic_ja.html)  
