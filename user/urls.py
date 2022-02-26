from django.urls import path
from user import views

urlpatterns = [
    path("", views.all_music, name="index"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),
    # path("item/", views.item, name="item"),
    path("all_music/", views.all_music, name="all_music"),
    path("music/<int:music_id>/", views.music_detail, name="music"),
    # path("good/<int:commen_id>/<int:music_id>/", views.good, name="good"),
    path("collect/<int:music_id>/", views.collect, name="collect"),
    path("decollect/<int:music_id>/", views.decollect, name="decollect"),
    path("mycollect/", views.mycollect, name="mycollect")
    # path("myjoin/", views.myjoin, name="myjoin"),
    # path("my_comments/", views.my_comments, name="my_comments"),
    # path("my_rate/", views.my_rate, name="my_rate"),
    # path("delete_comment/<int:comment_id>", views.delete_comment, name="delete_comment"),
    # path("delete_rate/<int:rate_id>", views.delete_rate, name="delete_rate"),
    # # 收藏最多
    # path("hot_music/", views.hot_music, name="hot_music"),
    # path("most_view/", views.most_view, name="most_view"),
    # path("most_mark/", views.most_mark, name="most_mark"),
    # path("latest_music/", views.latest_music, name="latest_music"),
    # path("search/", views.search, name="search"),
    # path("golden_horse/", views.golden_horse, name="golden_horse"),
    # path("oscar/", views.oscar, name="oscar"),
    # path("begin/", views.begin, name="begin"),
    # path("kindof/", views.kindof, name="kindof"),
    # path("kind/<int:kind_id>/", views.kind, name="kind"),
    # path("week_reco/", views.reco_by_week, name="week_reco"),
    # path("item_recommend/", views.item_recommend, name="item_recommend"),
    # path("monthitem/", views.reco_by_week, name="monthitem"),
]
