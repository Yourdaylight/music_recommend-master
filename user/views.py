import logging
from functools import wraps

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.renderers import JSONRenderer

from cache_keys import USER_CACHE, ITEM_CACHE
from .forms import *
from .recommend_musics import recommend_by_user_id, recommend_by_item_id

logger = logging.getLogger()
logger.setLevel(level=0)


def login_in(func):  # 验证用户是否登录
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        is_login = request.session.get("login_in")
        if is_login:
            return func(*args, **kwargs)
        else:
            return redirect(reverse("login"))

    return wrapper


def musics_paginator(musics, page):
    paginator = Paginator(musics, 6)
    if page is None:
        page = 1
    musics = paginator.page(page)
    return musics


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs["content_type"] = "application/json"
        super(JSONResponse, self).__init__(content, **kwargs)


def login(request):
    if request.method == "POST":
        form = request.POST
        if form:
            username = form.get("username", "")
            password = form.get["password", ""]
            result = User.objects.filter(username=username)
            if result:
                user = User.objects.get(username=username)
                if user.password == password:
                    return JSONResponse({"code": 200, "msg": "登录成功"})  # 跳转到登录界面
                else:
                    return JSONResponse({"code": 500, "msg": "登录失败"})  # 跳转到登录界面

        else:
            return JSONResponse({"code": 500, "msg": "注册失败"})  # 跳转到登录界面
    form = Login()
    return render(request, "user/login.html", {"form": form})


def register(request):
    if request.method == "POST":
        form = request.POST
        error = None
        if form:
            username = form.get("username"),
            password = form.get("password2"),
            email = form.get("email"),
            name = form.get("name"),
            phone = form.get("phone"),
            address = form.get("address")
            User.objects.create(
                username=username,
                password=password,
                email=email,
                name=name,
                phone=phone,
                address=address,
            )
            # 根据表单数据创建一个新的用户
            return JSONResponse({"code": 200, "msg": "注册成功"})  # 跳转到登录界面
        else:
            return JSONResponse({"code": 500, "msg": "注册失败"})  # 跳转到登录界面
    form = RegisterForm()
    return render(request, "user/register.html", {"form": form})


def logout(request):
    if not request.session.get("login_in", None):  # 不在登录状态跳转回首页
        return redirect(reverse("index"))
    request.session.flush()  # 清除session信息
    return redirect(reverse("index"))


def all_music(request):
    """"""
    musics = Music.objects.all().values()
    res = []
    temp_dict = {}
    for music in musics:
        # 去重，因为数据库是按评论存的
        if not temp_dict.get(music["name"]):
            temp_dict[music["name"]] = 1
            res.append(music)

    return JSONResponse({"code": 200, "data": res, "msg": "查询成功"})


def search(request):  # 搜索
    if request.method == "POST":  # 如果搜索界面
        key = request.POST["search"]
        request.session["search"] = key  # 记录搜索关键词解决跳页问题
    else:
        key = request.session.get("search")  # 得到关键词
    musics = Music.objects.filter(
        Q(name__icontains=key) | Q(lyric__icontains=key) | Q(artist__icontains=key)
    )  # 进行内容的模糊搜索
    page_num = request.GET.get("page", 1)
    musics = musics_paginator(musics, page_num)
    return render(request, "user/item.html", {"musics": musics})


def music(request, music_id):
    music = Music.objects.get(pk=music_id)
    music.num += 1
    music.save()
    comments = music.comment_set.order_by("-create_time")
    user_id = request.session.get("user_id")
    music_rate = Rate.objects.filter(music=music).all().aggregate(Avg('mark'))
    if music_rate:
        music_rate = music_rate['mark__avg']
    if user_id is not None:
        user_rate = Rate.objects.filter(music=music, user_id=user_id).first()
        user = User.objects.get(pk=user_id)
        is_collect = music.collect.filter(id=user_id).first()
    return render(request, "user/music.html", locals())


@login_in
def mycollect(request):
    user = User.objects.get(id=request.session.get("user_id"))
    music = user.music_set.all()
    return render(request, "user/mycollect.html", {"music": music})



@login_in
def item_recommend(request):
    page = request.GET.get("page", 1)
    user_id = request.session.get("user_id")
    cache_key = ITEM_CACHE.format(user_id=user_id)
    music_list = cache.get(cache_key)
    if music_list is None:
        music_list = recommend_by_item_id(user_id)
        cache.set(cache_key, music_list, 60 * 5)
        print('设置缓存')
    else:
        print('缓存命中!')
    musics = musics_paginator(music_list, page)
    path = request.path
    title = "依据item推荐"
    return render(
        request, "user/item.html", {"musics": musics, "path": path, "title": title}
    )
