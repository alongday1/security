from django.urls import path
from meals import views 
from . import views
from .views import record_list,delete_meal,set_calorie_goal, meal_search_ajax
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', record_list, name='record_list'),
    path('meals/', views.record_list, name='record_list'), 
    path('delete_meal/<int:meal_id>/', delete_meal, name='delete_meal'),
    path('set-calorie-goal/', set_calorie_goal, name='set_calorie_goal'),  
    path('get_calendar_data/<int:year>/<int:month>/', views.get_calendar_data, name='get_calendar_data'),
    path('search/ajax/', meal_search_ajax, name='meal_search_ajax'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
