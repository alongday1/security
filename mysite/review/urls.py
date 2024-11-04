from django.urls import path
from . import views


urlpatterns = [
    path("", views.review, name='review'),
    path('get_dishes_by_search/', views.get_dishes_by_search, name='get_dishes_by_search'),
    path("comments/", views.comments, name='comments'),
    path("add_tag/", views.add_tag, name='add_tag'),
    path("add_dish/", views.add_dish, name='add_dish'),

    path("comments/submit_form/<int:dish_id>/", views.submit_form, name='submit_form'),
    path("comments/submit_rating/<int:dish_id>/", views.submit_rating, name='submit_rating'),
    path("comments/update_like/", views.update_like, name='update_like'),
    path("comments/update_dish_info/", views.update_dish_info, name='update_dish_info'),
    path("comments/add_image/", views.add_image, name='add_image'),
    path("comments/refresh_comments/", views.refresh_comments, name='refresh_comments'),
]