import logging
from functools import wraps

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from rest_framework.renderers import JSONRenderer

from cache_keys import ITEM_CACHE
from .forms import *
from .recommend_musics import recommend_by_item_id

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
            password = form.get("password", "")
            result = User.objects.filter(username=username)
            if result:
                user = User.objects.get(username=username)
                if user.password == password:
                    return JSONResponse({"code": 200, "msg": "登录成功"})  # 跳转到登录界面
                else:
                    return JSONResponse({"code": 500, "msg": "登录失败"})  # 跳转到登录界面

        else:
            return JSONResponse({"code": 500, "msg": "登录失败，账户或者密码错误"})  # 跳转到登录界面
    return JSONResponse({"code": 500, "msg": "登录失败，账户或者密码错误"})


def register(request):
    """用户注册"""
    try:
        if request.method == "POST":
            form = request.POST
            if form:
                username = form.get("username")
                password = form.get("password2")
                email = form.get("email")
                name = form.get("name")
                phone = form.get("phone")
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
    except Exception as e:
        msg = "用户名已存在" if "UNIQUE constraint" in str(e) else str(e)
        return JSONResponse({"code": 500, "msg": msg})
    return JSONResponse({"code": 500, "msg": "注册失败"})


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


def music_detail(request, music_id):
    """
    返回接口的详情信息、词云、情感聚类
    :param request:
    :param music_id:
    :return:
    """
    code, msg = 200, "查询成功"
    res = {
        "detail": {},
        "topic": {},
        "word_cloud": {}
    }
    try:
        detail = Music.objects.filter(sump=music_id).values()
        res["detail"] = [item for item in detail]
    except Exception as e:
        msg = str(e)
    return JSONResponse({"data": res, "code": 200, "msg": msg})


@require_http_methods(["POST"])
def mycollect(request):
    code, msg = 200, "查询成功"
    data = []
    try:
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        music = user.music_set.all()
        if music:
            data = [item for item in music.values()]
    except Exception as e:
        code, msg = 500, str(e)
    return JSONResponse({
        "data":data,
        "code":code,
        "msg":msg
    })


@require_http_methods(["POST"])
def collect(request, music_id):
    """
    添加收藏
    :param request:
    :param music_id:
    :return:
    """
    code, msg = 200, "收藏成功"
    try:
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        music = Music.objects.filter(sump=music_id)[0]
        music.collect.add(user)
        music.save()
    except Exception as e:
        code, msg = 500, str(e)
    return JSONResponse({"code": code, "msg": msg})


@require_http_methods(["POST"])
def decollect(request, music_id):
    """取消收藏"""
    code, msg = 200, "取消收藏成功"
    try:
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        music = Music.objects.filter(sump=music_id)[0]
        music.collect.remove(user)
        music.save()
    except Exception as e:
        code, msg = 500, str(e)
    return JSONResponse({"code": code, "msg": msg})


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
