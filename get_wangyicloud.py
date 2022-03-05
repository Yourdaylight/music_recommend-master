# -*- coding: utf-8 -*-
import json
import os
import re
import time
import traceback

import django
import requests
from bs4 import BeautifulSoup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music.settings")
django.setup()
from user.models import Music, Detail


def save_to_database(item):
    try:
        if isinstance(item, dict):
            Music.objects.get_or_create(name=item["name"], sump=item.get("sump"),
                                        artist=item.get('artist', "未知歌手"),
                                        pic=item.get("pic", "https://p2.music.126.net/G91csin09maPrNgqcUKnBQ==/109951165698553069.jpg?param=50y50"),
                                        album=item.get("album", "未知"), comments=item.get("comment"),
                                        years=item.get("years"), num=item.get("num"))
    except Exception as e:
        traceback.print_exc()



def get_hotComments(hot_song_name, hot_song_id, album, artist, pic_url):
    res = {}
    url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(hot_song_id) + '?csrf_token='  # 歌评url
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
    all_comments = [item.get("content") for item in json_dict.get("comments",[])]
    num = 0
    for item in hot_comments:
        liked_count = item.get("likedCount", 0)
        update_time = item.get("timeStr", "2022-1-1")
        res["name"] = hot_song_name
        res["num"] = liked_count
        res["sump"] = hot_song_id
        res['years'] = update_time
        res["comment"] = item.get("content")
        all_comments.append(item.get("content"))
        res["artist"] = artist
        res["album"] = album
        res["pic"] = pic_url
        save_to_database(res)
        num += 1
        print(str(num) + '.' + item['content'] + '\n')
    # 针对所有评论存一份到详情表用作词云
    from user.nlp_utils.lda_model import get_tags
    tags = get_tags(hot_song_id)
    rate = sum(tags.values())
    Detail.objects.get_or_create(comments="".join(all_comments), sump=hot_song_id,
                                 tags=json.dumps(tags), rate=rate)



def main():
    url1 = 'http://music.163.com/discover/toplist?id=3778678'  # 云音乐热歌榜
    # UA必須要設置，未设置获取的网页不完整
    headers = {
        'Cookie': '__e_=1515461191756; _ntes_nnid=af802a7dd2cafc9fef605185da6e73fb,1515461190617; _ntes_nuid=af802a7dd2cafc9fef605185da6e73fb; JSESSIONID-WYYY=HMyeRdf98eDm%2Bi%5CRnK9iB%5ChcSODhA%2Bh4jx5t3z20hhwTRsOCWhBS5Cpn%2B5j%5CVfMIu0i4bQY9sky%5CsvMmHhuwud2cDNbFRD%2FHhWHE61VhovnFrKWXfDAp%5CqO%2B6cEc%2B%2BIXGz83mwrGS78Goo%2BWgsyJb37Oaqr0IehSp288xn5DhgC3Cobe%3A1515585307035; _iuqxldmzr_=32; __utma=94650624.61181594.1515583507.1515583507.1515583507.1; __utmc=94650624; __utmz=94650624.1515583507.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmb=94650624.4.10.1515583507',
        'Host': 'music.163.com',
        'Refere': 'http://music.163.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }

    response = requests.get(url1, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    # 找到json数据
    textarea = soup.find('textarea').text
    contents = json.loads(str(textarea))
    for item in contents:
        # 发行时间
        t1 = time.localtime(item.get('publishTime') / 1000)
        public_time = time.strftime("%Y-%m-%d %H:%M:%S", t1)
        # 歌曲时长
        play_time = item.get('duration') / 1000
        min = str(play_time / 60)
        sec = str(play_time % 60)
        if len(sec) < 2:
            sec = '0' + str(sec)
        # 歌手
        artist = item.get('artists')[0].get('name')
        # 歌名
        music_name = item.get('name')
        # 专辑
        album = item.get('album').get('name')
        # 图片链接
        pic_url = item.get("album").get("picUrl")
        # 歌曲的id
        hot_song_id = item.get("id")
        get_hotComments(music_name, hot_song_id, album, artist, pic_url)


if __name__ == '__main__':
    main()
