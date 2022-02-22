# -*- coding: utf-8 -*-
# @Time    :2022/2/20 18:25
# @Author  :lzh
# @File    : get_detail.py
# @Software: PyCharm

# import requests
# from lxml import etree
#
# # 热歌榜首页网址
# url = 'https://music.163.com/discover/toplist?id=3778678'
# # 歌曲下载链接前半部分
# url_base = 'http://music.163.com/song/media/outer/url?id='
# # U-A伪装，模拟浏览器
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
#                   '(KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
# # 抓取网站信息并使用etree预处理数据
# response = requests.get(url=url, headers=headers)
# html = etree.HTML(response.text)
# # 原始id、name列表（包含无关信息）
# raw_id_list = html.xpath('//a[contains(@href, "song?")]/@href')
# raw_name_list = html.xpath('//a[contains(@href, "song?")]/text()')
# id_list = []
# name_list = []
# # 过滤无关信息，得到纯净列表
# for id in raw_id_list:
#     music_id = id.split('=')[1]
#     if '$' not in music_id:
#         id_list.append(music_id)
# for music_name in raw_name_list:
#     if '{' not in music_name:
#         name_list.append(music_name)
# # 遍历所有歌曲
# for i in range(len(id_list)):
#     # 完整下载链接
#     music_url = url_base + id_list[i]
#     # 对应歌曲名称
#     music_name = name_list[i]
#     # 获取每首歌取得具体信息
#     music = requests.get(url=music_url, headers=headers)
#     # 以二进制形式写入到本文件夹的（具体保存路径可自己修改）
#     with open('./%s.mp3' % music_name, 'wb') as file:
#         file.write(music.content)
#         print('<%s>下载成功...' % music_name)
if __name__ == '__main__':

    import os
    lists = os.listdir(".")
    base = os.path.abspath(".")
    for mp3 in lists:
        if ".mp3" in mp3:
            os.remove(os.path.join(base, mp3))
