# -*- coding: utf-8 -*-
import os
import re

import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music.settings")

django.setup()


def get_all_hotSong():  # 获取热歌榜所有歌曲名称和id
    url = 'http://music.163.com/discover/toplist?id=3778678'  # 网易云云音乐热歌榜url
    header = {  # 请求头部
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    request = requests.get(url=url, headers=header)
    html = str(request.content)
    pat1 = r'<ul class="f-hide"><li><a href="/song\?id=\d*?">.*</a></li></ul>'  # 进行第一次筛选的正则表达式
    result = re.compile(pat1).findall(html)  # 用正则表达式进行筛选
    result = result[0]  # 获取tuple的第一个元素

    pat2 = r'<li><a href="/song\?id=\d*?">(.*?)</a></li>'  # 进行歌名筛选的正则表达式
    pat3 = r'<li><a href="/song\?id=(\d*?)">.*?</a></li>'  # 进行歌ID筛选的正则表达式
    pat4 = r'<span title="(.*?)"><a class="" href="/artist?id=\d*?'
    hot_song_name = re.compile(pat2).findall(result)  # 获取所有热门歌曲名称
    hot_song_id = re.compile(pat3).findall(result)  # 获取所有热门歌曲对应的Id
    hot_song_author = re.compile(pat4).findall(result)

    return hot_song_name, hot_song_id, hot_song_author


def get_hotComments(hot_song_name, hot_song_id):
    res = {}
    url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_' + hot_song_id + '?csrf_token='  # 歌评url
    header = {  # 请求头部
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    # post请求表单数据
    data = {
        'params': 'zC7fzWBKxxsm6TZ3PiRjd056g9iGHtbtc8vjTpBXshKIboaPnUyAXKze+KNi9QiEz/IieyRnZfNztp7yvTFyBXOlVQP/JdYNZw2+GRQDg7grOR2ZjroqoOU2z0TNhy+qDHKSV8ZXOnxUF93w3DA51ADDQHB0IngL+v6N8KthdVZeZBe0d3EsUFS8ZJltNRUJ',
        'encSecKey': '4801507e42c326dfc6b50539395a4fe417594f7cf122cf3d061d1447372ba3aa804541a8ae3b3811c081eb0f2b71827850af59af411a10a1795f7a16a5189d163bc9f67b3d1907f5e6fac652f7ef66e5a1f12d6949be851fcf4f39a0c2379580a040dc53b306d5c807bf313cc0e8f39bf7d35de691c497cda1d436b808549acc'}
    request = requests.post(url, headers=header, data=data)
    json_dict = request.json()
    hot_comments = json_dict.get('hotComments', [])  # 获取json中的热门评论

    num = 0
    fhandle = open('./song_comments', 'a', encoding='utf-8')  # 写入文件
    fhandle.write(hot_song_name + ':' + '\n')

    for item in hot_comments:
        liked_count = item.get("likedCount", 0)
        update_time = item.get("timeStr", "2022-1-1")
        res["name"] = hot_song_name
        res["num"] = liked_count

        num += 1
        fhandle.write(str(num) + '.' + item['content'] + '\n')
    fhandle.write('\n==============================================\n\n')
    fhandle.close()


def save_to_database():
    pass


def main():
    hot_song_name, hot_song_id, hot_song_author = get_all_hotSong()  # 获取热歌榜所有歌曲名称和id
    player_iframe = '<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=330 height=86 src="//music.163.com/outchain/player?type=2&id={}&auto=1&height=66"></iframe>'
    num = 0
    while num < len(hot_song_name):  # 保存所有热歌榜中的热评
        print('正在抓取第%d首歌曲热评...' % (num + 1))
        get_hotComments(hot_song_name[num], hot_song_id[num])
        print('第%d首歌曲热评抓取成功' % (num + 1))
        num += 1


if __name__ == '__main__':

    hot_song_name, hot_song_id, hot_song_author = get_all_hotSong()  # 获取热歌榜所有歌曲名称和id
    for i, j, k in zip(hot_song_name, hot_song_id, hot_song_author):
        print(i, "=", j, "=", k)
    # num = 0
    # while num < len(hot_song_name):  # 保存所有热歌榜中的热评
    #     print('正在抓取第%d首歌曲热评...' % (num + 1))
    #     get_hotComments(hot_song_name[num], hot_song_id[num])
    #     print('第%d首歌曲热评抓取成功' % (num + 1))
    #     num += 1
