from django.shortcuts import render, HttpResponse
from review.models import *
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from mysite.settings import MEDIA_ROOT
import os
import uuid
from meals.models import Meal
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from calendar import monthrange
import calendar
import json
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
import requests
from datetime import datetime
from forum.models import GroupPost,Post,Forum,Tag,PostImage,JoinRequest
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
import random
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from markdown import markdown
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q,Count
from forum.views import base_view


# Create your views here.

def my_cv(request):
    return render(request, "myweb.html")


def main_page(request):
    dishes = Dish.objects.all()[:6]
    dishImages = DishImage.objects.all()[:6]

    message_reminder_visible = base_view(request)
    response = requests.get("https://canteen.sjtu.edu.cn/CARD/Ajax/Place")
    canteen_data = response.json()
    group_posts = GroupPost.objects.order_by('-create_at')[:3]
    posts = Post.objects.order_by('-click')[:5]
    return render(request, "main_page.html", {'dishes': dishes, 'dish_image':  dishImages, 'canteen_data': canteen_data,'group_posts': group_posts,'posts':posts,'message_reminder_visible': message_reminder_visible,})


def test_mp(request):
    dishes = Dish.objects.all()[:6]
    dishImages = DishImage.objects.all()[:6]

    message_reminder_visible,is_authenticated = base_view(request)
    response = requests.get("https://canteen.sjtu.edu.cn/CARD/Ajax/Place")
    canteen_data = response.json()
    group_posts = GroupPost.objects.order_by('-create_at')[:3]
    posts = Post.objects.order_by('-click')[:5]

    if is_authenticated:
        user = request.user
    else:
        user = None

    return render(request, "index.html", {'active_link':'home','dishes': dishes, 'dish_image':  dishImages, 'canteen_data': canteen_data,'group_posts': group_posts,'posts':posts,'message_reminder_visible': message_reminder_visible,'is_authenticated':is_authenticated,'user':user,})
