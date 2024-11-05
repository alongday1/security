"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

from mainpage import views as mainpageViews

from management.views import home_view
from forum.views import forum_home_view,forum_post_view,post_detail,post_create_view,create_tag,group_post_view,group_detail,join_group,forum_message_view,pass_request,reject_request,confirm_request,delete_post,delete_group_post,edit_post,edit_group_post
from django.conf import settings
from django.conf.urls.static import static
from api.views import PostListView,SearchPostView


from main.views import ChangeLanguageView, IndexPageView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexPageView.as_view(), name="index"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("language/", ChangeLanguageView.as_view(), name="change_language"),
    path("accounts/", include("accounts.urls")),
    path("review/", include("review.urls")),


    path('user/my_cv/', mainpageViews.my_cv),
    path('main_page', mainpageViews.main_page),
    path('test_mp', mainpageViews.test_mp, name='main_page'),



    path('', home_view, name='home'),
    path('record/', include('meals.urls')),
    path('forum/post/create/', post_create_view, name='post_create'),
    path('forum/<int:forum_id>/', forum_post_view, name='forum_post'),
    path('forum/', forum_post_view, name='forum_post_default'),
    path('forum/group/', group_post_view, name='group_post_list'),
    path('forum/post/<uuid:uuid>/', post_detail, name='post_detail'),
    path('forum/group_post/<uuid:uuid>/', group_detail, name='group_detail'),
    path('api/posts/', PostListView.as_view(), name='post-list'),
    path('search/post/', SearchPostView.as_view(), name='search-post'),
    path('create-tag/', create_tag, name='create_tag'),
    path('forum/group_post/join/<uuid:group_post_id>/', join_group, name='join_group'),
    path('message/forum/', forum_message_view, name='message_forum', ),
    path('forum/pass/<uuid:join_request_id>/', pass_request, name='pass_request'),
    path('forum/reject/<uuid:join_request_id>/', reject_request, name='reject_request'),
    path('forum/confirm/<uuid:join_request_id>/', confirm_request, name='confirm_request'),
    path('forum/post/delete/<uuid:post_id>/', delete_post, name='delete_post'),
    path('forum/group_post/delete/<uuid:post_id>/', delete_group_post, name='deletegroup__post'),
    path('forum/post/edit/<uuid:post_id>/', edit_post, name='edit_post'),
    path('forum/group_post/edit/<uuid:post_id>/', edit_group_post, name='edit_group_post'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
