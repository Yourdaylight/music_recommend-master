# -*- coding: utf-8 -*-
import pandas as pd
from gensim.corpora import Dictionary
from gensim.models import LdaModel

pos_com = pd.read_csv('neg_com.csv', header=None, index_col=0)    # 读取预处理好后的数据

pos_com.columns = ['comment']  # 更改列名称
mid = list(pos_com['comment'].str.split(' '))    # 将评论文本分词（基于空格）
dictionary = Dictionary(mid)                     # 生成词典
bow = [dictionary.doc2bow(comment) for comment in mid]    # 将文档转成数值型预料库

pos_model = LdaModel(corpus=bow, id2word=dictionary, num_topics=3)    # 构建LDA主题模型
pos_model.print_topic(1)    # 打印主题

