# -*- coding: utf-8 -*-
import re
import unicodedata

import nltk
from nltk.corpus import wordnet


def normalize(text):
    normalized_text = normalize_unicode(text)
    normalized_text = normalize_number(normalized_text)
    normalized_text = lower_text(normalized_text)
    return normalized_text


def lower_text(text):
    return text.lower()


def normalize_unicode(text, form='NFKC'):
    normalized_text = unicodedata.normalize(form, text)
    return normalized_text


def lemmatize_term(term, pos=None):
    if pos is None:
        synsets = wordnet.synsets(term)
        if not synsets:
            return term
        pos = synsets[0].pos()
        if pos == wordnet.ADJ_SAT:
            pos = wordnet.ADJ
    return nltk.WordNetLemmatizer().lemmatize(term, pos=pos)


def normalize_number(text):
    """
    pattern = r'\d+'
    replacer = re.compile(pattern)
    result = replacer.sub('0', text)
    """
    # 連続した数字を0で置換
    replaced_text = re.sub(r'\d+', '0', text)
    return replaced_text


# refer to https://github.com/neologd/mecab-ipadic-neologd/wiki/Regexp
def unicode_normalize(cls, text):
    pt = re.compile('([{}]+)'.format(cls))

    def norm(c):
        return unicodedata.normalize('NFKC', c) if pt.match(c) else c

    text = ''.join(norm(x) for x in re.split(pt, text))
    text = re.sub('－', '-', text)
    return text


def remove_extra_spaces(text):
    text = re.sub('[ 　]+', ' ', text)
    blocks = ''.join(('\u4E00-\u9FFF',  # CJK UNIFIED IDEOGRAPHS
                      '\u3040-\u309F',  # HIRAGANA
                      '\u30A0-\u30FF',  # KATAKANA
                      '\u3000-\u303F',  # CJK SYMBOLS AND PUNCTUATION
                      '\uFF00-\uFFEF'  # HALFWIDTH AND FULLWIDTH FORMS
                      ))
    basic_latin = '\u0000-\u007F'

    def remove_space_between(cls1, cls2, s):
        p = re.compile('([{}]) ([{}])'.format(cls1, cls2))
        while p.search(s):
            s = p.sub(r'\1\2', s)
        return s

    text = remove_space_between(blocks, blocks, text)
    text = remove_space_between(blocks, basic_latin, text)
    text = remove_space_between(basic_latin, blocks, text)
    return text


def normalize_neologd(text):
    text = text.strip()
    text = unicode_normalize('０-９Ａ-Ｚａ-ｚ｡-ﾟ', text)

    def maketrans(f, t):
        return {ord(x): ord(y) for x, y in zip(f, t)}

    text = re.sub('[˗֊‐‑‒–⁃⁻₋−]+', '-', text)  # normalize hyphens
    text = re.sub('[﹣－ｰ—―─━ー]+', 'ー', text)  # normalize choonpus
    text = re.sub('[~∼∾〜〰～]', '', text)  # remove tildes
    text = text.translate(
        maketrans('!"#$%&\'()*+,-./:;<=>?@[¥]^_`{|}~｡､･｢｣',
                  '！”＃＄％＆’（）＊＋，－．／：；＜＝＞？＠［￥］＾＿｀｛｜｝〜。、・「」'))

    text = remove_extra_spaces(text)
    text = unicode_normalize('！”＃＄％＆’（）＊＋，－．／：；＜＞？＠［￥］＾＿｀｛｜｝〜', text)  # keep ＝,・,「,」
    text = re.sub('[’]', '\'', text)
    text = re.sub('[”]', '"', text)
    return text
