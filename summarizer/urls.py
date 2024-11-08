from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("single-video-summary/", views.single_video_summary, name="single_video_summary"),
    path("search/", views.search, name="search"),
    path("search/results/<str:query>/", views.search_results, name="search_results"),
    path("history/", views.history, name="history"),
    path("profile/", views.user_profile, name="user_profile"),
    path("summary/<int:summary_id>/", views.view_summary, name="view_summary"),
    path("search/<int:search_id>/", views.view_search, name="view_search"),
]
