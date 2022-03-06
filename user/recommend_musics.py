import os
import pandas as pd
import json
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music.settings")

django.setup()

from user.models import *


def recommend_by_item(username):
    """推荐"""
    user = User.objects.get(name=username)
    music = user.music_set.all()
    if music:
        score = []
        for item in music:
            # 获取所有收藏歌单对应歌曲的评分
            music_id = item.sump
            detail = Detail.objects.get(sump=music_id)
            score.append(detail.rate)
        # 获取所有歌曲的评分与id，作差，返回分数差最小的作为推荐
        rate = [i.rate for i in Detail.objects.all()]
        sump = [i.sump for i in Detail.objects.all()]
        df = pd.DataFrame({
            "rate":rate,
            "sump":sump
        })
        # 返回评分最接近的10首歌
        df["recommend"] = df["rate"]-sum(score)/len(score)
        df["recommend"] = df["recommend"].abs()
        df = df.sort_values(by="recommend")
        recommend_id = df["sump"][1:11]
        recommend_music = Music.objects.filter(sump__in=recommend_id)
        temp_dict = {}
        res = []
        for music in recommend_music.values():
            if not temp_dict.get(music.get("sump")):
                temp_dict[music["sump"]] = 1
                res.append(music)
        return res

if __name__ == '__main__':
    # random_music_id()
    # 随机生成用户打分 参数为生成数量
    print(recommend_by_item("admin"))

