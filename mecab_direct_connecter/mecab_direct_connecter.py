# -*- coding: utf-8 -*-
# !/usr/local/bin/python
# vim: set fileencoding=utf-8:

"""
Mac等からアクセス可能なMecabバインディングを用いて、高速な形態素解析環境を提供します。
使用例は、Mecab_Motherクラス内に記述。
"""
import re
import MeCab
import neologdn
import pandas

import logging

# logging.basicConfig(filemode='a', filename="./logs/mecab_direct_connecter.log")


class MecabMother(object):
    """
    >>> mecab_proc = MecabMother()

    # Mecab_Motherのプロパティtextに解析対象の文字列を登録
    >>> mecab_proc.set_text_to_parse("基礎,講座")

    >>> mecab_proc.extracted_category_word(["名詞"])
    ['\u57fa\u790e', '\u8b1b\u5ea7']

    >>> mecab_proc.set_text_to_parse("単体テストができる(????)")

    # 単語リストと品詞リストのジェネレータを作成
    >>> words_gen = mecab_proc.word_generator()

    # クラス内プロパティそのものから未知語を削除する。
    >>> mecab_proc.unknown_word_buster_by_parts()

    #>>> mecab_proc.unknown_word_buster()

    # ユニコード型の単語が入ったリストが返ってくる
    >>> print(next(words_gen))
    ['\u5358\u4f53\u30c6\u30b9\u30c8', '\u304c', '\u3067\u304d\u308b']

    # ユニコード型の品詞が入ったリストが返ってくる
    >>> print(next(words_gen))
    ['\u540d\u8a5e', '\u52a9\u8a5e', '\u52d5\u8a5e']

    # 読みを取ってくる。もしも、読みが解析不能ならもう未知語として扱う。
    >>> print(next(words_gen))
    ['\u30bf\u30f3\u30bf\u30a4\u30c6\u30b9\u30c8', '\u30ac', '\u30c7\u30ad\u30eb']

    # 原形を出力
    >>> print(next(words_gen))
    ['\u5358\u4f53\u30c6\u30b9\u30c8', '\u304c', '\u3067\u304d\u308b']

    # 名詞の抽出
    >>> mecab_proc.extracted_category_word(["名詞"])
    ['\u5358\u4f53\u30c6\u30b9\u30c8']

    # 動詞の抽出
    >>> mecab_proc.extracted_category_word(["動詞"])
    ['\u3067\u304d\u308b']
    """
    def __init__(self, mecab_dict_path='', neologd_normalizer=True):
        """
        メソッドで活用するために、MeCabのTaggerを定義し、プロパティ化する。

        """
        # デフォルトエンコーディングのチェック
        checkdefaultencoding()

        # クラス内共有変数
        # 解析対象のテキスト
        self.text = []

        # 結果を格納する変数群
        # [XXX] Too Many Class Properties... Maybe Better managed by pandas.
        self.result = str()  # This will replaced by mecab result."
        self.words = []
        self.parts = []
        self.parts_detail_1 = []
        self.parts_detail_2 = []
        self.parts_detail_3 = []
        self.con_1 = []
        self.con_2 = []
        self.original_shape = []
        self.readings = []
        self.pronunciations = []

        # Mecab Setup
        # New Words Dictionary Implemented.
        dict_path = [
            "-d /usr/local/Cellar/mecab/0.996/lib/mecab/dic/mecab-ipadic-neologd -x 未知語,*,*,*,*,*,*,*,* --eos-format=",
            "-d /usr/lib64/mecab/dic/mecab-ipadic-neologd -x 未知語,*,*,*,*,*,*,*,* --eos-format=",
            "-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -x 未知語,*,*,*,*,*,*,*,* --eos-format=",
            "-d /usr/lib/mecab/dic/mecab-ipadic-neologd -x 未知語,*,*,*,*,*,*,*,* --eos-format=",
            "-d {0} -x 未知語,*,*,*,*,*,*,*,* --eos-format=".format(mecab_dict_path),
            "-x 未知語,*,*,*,*,*,*,*,* --eos-format="]
        for path in dict_path:
            try:
                self.parser = MeCab.Tagger(path)
                dict_available = path.split(" ")
                break
            except RuntimeError:
                self.parser = None
        if self.parser is None:
            raise(RuntimeError("Runtime Place is unknown, please set your env's Mecab_dictionay path."))

        logging.warning("Mecab Command line: mecab {0}".format(dict_available))

    def set_text_to_parse(self, input_text):
        """
        Mecabで処理すべき文章をインスタンスに登録
        さらに、形態素解析処理およびリスト化
        """
        self.text = str(input_text)

        # カンマとタブで文字列を区切る正規表現
        splitter = re.compile(",|\t")

        # Mecabパース執行
        self.result = self.parser.parse(self.text)
        # 単語区切り(\nで区切る)
        # noinspection PyUnresolvedReferences
        word_with_attribute = self.result.split('\n')
        # 出力最終行が空欄になっているので、削除
        word_with_attribute.pop()
        # カンマとタブで区切られている処理結果をリスト化
        self.result = [splitter.split(x) for x in word_with_attribute]

        # リストをUnicode型にする。
        # 表層形\t品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
        self.words = [x[0] for x in self.result]
        self.parts = [x[1] for x in self.result]
        self.parts_detail_1 = [x[2] for x in self.result]
        self.parts_detail_2 = [x[3] for x in self.result]
        self.parts_detail_3 = [x[4] for x in self.result]
        self.con_1 = [x[5] for x in self.result]
        self.con_2 = [x[6] for x in self.result]
        self.original_shape = [x[7] for x in self.result]
        self.readings = [x[8] for x in self.result]
        self.pronunciations = [x[9] for x in self.result]

    def word_generator(self):
        """
        ジェネレータ(形態素解析済み単語リスト・品詞リスト)
        """
        # 単語リスト
        yield self.words
        # 品詞リスト
        yield self.parts
        # 読みリスト
        yield self.pronunciations
        # 単語の原形リスト
        yield self.original_shape

    def extracted_category_word(self, category):
        """
        ジェネレータ(指定品詞で単語を抽出)
        """
        logging.warning("This Method will return clean words.")
        self.unknown_word_buster_by_parts()
        self.unknown_word_buster_by_readings()
        category = list(category)
        if isinstance(category, list):
            TypeError("extracted_category_word needs list type arg.")
        # 結果を格納するリスト
        extracted_word = []
        # 指定された品詞を抽出する作業
        for i, word in enumerate(self.words):
            if self.parts[i] in category:
                extracted_word.append(word)
        return extracted_word

    def extract_category_originalshape(self, category):
        """
        ジェネレータ(指定品詞で単語を抽出)
        """
        category = list(category)
        # 結果を格納するリスト
        extracted_word = []
        # 指定された品詞を抽出する作業
        for i, word in enumerate(self.original_shape):
            if self.parts[i] in category:
                extracted_word.append(word)
        return extracted_word

    def unknown_word_buster_by_readings(self):
        """
        未知語(読みが不明な単語を指す)の除去
        """
        del_factor_num = []
        for i, reading in enumerate(self.pronunciations):
            if reading == "*":
                del_factor_num.append(i)

        for i in reversed(del_factor_num):
            del self.words[i]
            del self.parts[i]
            del self.original_shape[i]
            del self.readings[i]
            del self.pronunciations[i]

    def unknown_word_buster_by_parts(self):
        """
        未知語であるとMecabに判断された単語を除去する
        """
        del_factor_num = []
        for i, part in enumerate(self.parts):
            if part == "未知語":
                del_factor_num.append(i)

        for i in reversed(del_factor_num):
            del self.words[i]
            del self.parts[i]
            del self.original_shape[i]
            del self.readings[i]
            del self.pronunciations[i]


class StopWordKiller(object):
    def __init__(self):
        inline_def = ["拝読", "の", "こと", "もの", "よう", "http://", "人", "私", "様", "ー", "一", "が", "ため", "方", "ほう", "こと", "場合",
                      "何", "さま", "それ", "これ", "ん", "相談者", "%"]
        zenkaku_num = ["１", "２", "３", "４", "５", "６", "７", "８", "９", "０"]
        stop_word_ext = pandas.read_csv(settings.STOP_WORD_DATA, header=None).iloc[:, 0].tolist()

        self.stop_word = stop_word_ext + inline_def + zenkaku_num + list(range(0, 10))

    def killer(self, list_data):
        """Kill Stop words from list.

        >>> stopworddisposal = StopWordKiller()
        >>> stopworddisposal.killer(["相談", "の", "相談者さま"])"""
        return [i for i in list_data if not i in self.stop_word]


def checkdefaultencoding():
    """
    Python環境がUTF-8をデフォルトエンコーディングとしているかをチェックする。

    site-packages/sitecustomize.pyに以下を記入

    import sys
    sys.setfdefaultencoding('utf-8')

    参考サイト:http://qiita.com/puriketu99/items/55e04332881d7b679b00
    >>> checkdefaultencoding()

    """
    import sys
    if sys.getdefaultencoding() == 'ascii':
        raise UnicodeError("Please set sys.setfdefaultencoding('utf-8') in site-packages/sitecustomize.py")


if __name__ == '__main__':
    import doctest

    # 単体テスト執行
    doctest.testmod(verbose=True)
