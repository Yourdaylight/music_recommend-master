# -*- coding: utf-8 -*-
import os
import re
from collections import Counter

import django
import jieba
import pandas as pd
from gensim.corpora import Dictionary
from gensim.models import LdaModel

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music.settings")
django.setup()
from user.models import Detail,Music


def get_tags(music_id):
    """根据歌曲的Id获取评论，根据评论内容进行主题提取,返回主题"""
    detail = Detail.objects.get(sump=music_id)
    comments = [detail.comments]
    ids = [detail.sump]
    data = pd.DataFrame({
        "comment": comments,
        "id": ids
    })
    data_ao = data["comment"]
    data_ao = data_ao.dropna().apply(lambda x: re.sub('\n', '', x))
    data_ao = data_ao.apply(lambda x: re.sub('&[a-zA-Z]+;', '', x))
    data_ao.drop_duplicates(inplace=True)
    # 分词
    data_cut = data_ao.apply(jieba.lcut)
    # 读取停用词表并去掉评论中的停用词
    stop_word = pd.read_csv('stopword.txt', sep='haha', engine="python")
    stop_words = list(stop_word.iloc[:, 0]) + [' ']
    data_after_stop = data_cut.apply(lambda x: [i for i in x if i not in stop_words])  # 去除停用词
    result_topic = {}
    for index, i in enumerate(data_after_stop):
        dictionary = Dictionary([i])
        # 将文档转成数值型预料库
        bow = [dictionary.doc2bow(comment) for comment in [i]]
        # 构建LDA主题模型
        pos_model = LdaModel(corpus=bow, id2word=dictionary, num_topics=3)
        res = pos_model.print_topic(1) + "+" + pos_model.print_topic(2)  # 打印主题
        for topics in res.split("+"):
            score, topic = topics.split("*")
            topic = topic.replace('"', '')
            # 将名称至少两个字的主题加入返回值
            if len(topic) > 2:
                if result_topic.get(topic):
                    result_topic[topic] += float(score)
                else:
                    result_topic[topic] = float(score)
    return result_topic


def word_frequency(music_id):
    detail = Detail.objects.get(sump=music_id)
    comments = [detail.comments]
    # 分词
    data_cut = jieba.lcut(detail.comments)
    # 读取停用词表并去掉评论中的停用词
    stop_word = pd.read_csv('stopword.txt', sep='haha', engine="python")
    stop_words = list(stop_word.iloc[:, 0]) + [' '] + ["\n"]
    data_after_stop = []  # 去除停用词
    for word in data_cut:
        if word not in stop_words:
            data_after_stop.append(word)
    frequency_dict = dict(Counter(data_after_stop))
    # 词频统计只统计出现次数大于等于2的
    frequency_dict = {k:v for k,v in frequency_dict.items() if v>1}
    frequency_dict = dict(sorted(frequency_dict.items(), key=lambda x: x[1], reverse=True))
    return frequency_dict


if __name__ == '__main__':
    a=Music.objects.filter(name__contains="滚")
    print(len(a))
    print(a)
    # print(word_frequency(1901371647))
