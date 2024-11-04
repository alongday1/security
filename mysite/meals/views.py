from django.shortcuts import render, redirect
from .models import Meal
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


def record_list(request):
    # 检查会话中是否存在日期
    if 'current_date' not in request.session:
        request.session['current_date'] = datetime.now().date().strftime('%Y-%m-%d')

    current_date = datetime.strptime(request.session['current_date'], '%Y-%m-%d').date()

    if request.method == "GET" and 'date' in request.GET:
        current_date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
        request.session['current_date'] = current_date.strftime('%Y-%m-%d')

    if request.method == "POST":
        print(request.POST)
        meal_name = request.POST.get('name')
        meal_type = request.POST.get('meal_type')
        calories = request.POST.get('calories')
        date_to_use = request.POST.get('current_date')
        if date_to_use:  # 确保 date_to_use 不是 None
            date_to_use = datetime.strptime(date_to_use, '%Y-%m-%d').date()
        else:
            date_to_use = current_date  # 如果未提供，使用当前日期
        comment = request.POST.get('comment')  # 获取评论
        image = request.FILES.get('image')  # 获取图片

        print(f"Received: meal_name={meal_name}, meal_type={meal_type}, calories={calories}, date_to_use={date_to_use}")

        if meal_name and meal_type and calories and date_to_use:  # 确保字段不为空
            Meal.objects.create(
             name=meal_name,
             meal_type=meal_type,
             calories=calories,
             created_at=date_to_use,
             comment=comment,  # 保存评论
             image=image
            )

        return redirect(f"/record/?date={date_to_use}")
    else:
        print("Missing data fields!")

    meals = Meal.objects.filter(created_at=current_date,)

    # 分类餐记录
    categorized_meals = {meal_type: [] for meal_type in ['breakfast', 'lunch', 'dinner', 'more']}
    for meal in meals:
        categorized_meals[meal.meal_type].append(meal)

    meal_types_display = [('breakfast', '早餐'), ('lunch', '午餐'), ('dinner', '晚餐'), ('more', '加餐')]

    total_intake = sum(meal.calories for meal in meals) if meals else 0
    daily_calorie_goal = request.session.get('daily_calorie_goal', 2000)  # 设置每日卡路里目标（可以根据需求调整）
    remaining_calories = daily_calorie_goal - total_intake 
    remainingcalories =  total_intake - daily_calorie_goal
    total = total_intake


    # 获取当前日期并生成日历
    today = datetime.now()
    year = current_date.year
    month = current_date.month
    days_in_month = list(range(1, calendar.monthrange(year, month)[1] + 1))

    # 获取每日的卡路里数据
    calendar_data = {}
    
    for day in days_in_month:
        date_key = f"{year}-{month:02d}-{day:02d}"
        
        # 将字符串转换为日期对象
        date_object = datetime.strptime(date_key, "%Y-%m-%d").date()
        
        # 查询当天的所有记录
        meals_for_day = Meal.objects.filter(created_at=date_object)
        
        # 计算总卡路里
        total_intake = sum(meal.calories for meal in meals_for_day)
        if date_object <= today.date():
            if meals_for_day:
               if total_intake >= 0.8 * daily_calorie_goal and total_intake <= 1.2 * daily_calorie_goal:
                 color = "green"
               elif total_intake < 0.8 * daily_calorie_goal:
                 color = "yellow"
               else:
                 color = "red"
            else:
               color = "white"  # 没有记录的日期标记为白色
        else:
            continue  # 跳过今天及未来的日期，不设置颜色
        
        calendar_data[date_key] = color

        todaydate = timezone.now().date()
        last_week_start = todaydate - timedelta(days=todaydate.weekday() + 7)  # 上周开始日期
        last_week_end = last_week_start + timedelta(days=6)  # 上周结束日期

        # 查询上周的所有餐点
        meals = Meal.objects.filter(created_at__range=[last_week_start, last_week_end])

        # 用于存储每种餐点的记录次数和卡路里
        meal_counts = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'calories': 0}))

        for meal in meals:
          meal_counts[meal.meal_type][meal.name]['count'] += 1  # 统计每种餐点的记录次数
          meal_counts[meal.meal_type][meal.name]['calories'] += meal.calories  # 累加卡路里

        
         # 定义所有的餐点类型
        all_meal_types = ['breakfast', 'lunch', 'dinner', 'more']  # 根据模型定义的选项

        # 找出每种餐点类型中吃的次数最多的前三个记录（吃一次的不显示）
        favorite_meals = {meal_type: [] for meal_type in all_meal_types}  # 初始化为所有类型

        for meal_type in all_meal_types:
            items = meal_counts[meal_type]
            top_items = [(name, data) for name, data in items.items() if data['count'] > 1]  # 只保留吃多次的
            top_three = sorted(top_items, key=lambda x: x[1]['count'], reverse=True)[:3]
            favorite_meals[meal_type] = [{'name': name, 'count': data['count'], 'calories': data['calories']} for name, data in top_three]

    return render(request, 'meals/record_list.html', {
        'categorized_meals': categorized_meals,
        'current_date': current_date.strftime('%Y-%m-%d'),
        'meal_types_display': meal_types_display,
        'total_intake': total,
        'daily_calorie_goal': daily_calorie_goal,
        'remaining_calories':remaining_calories,
        'calendar_data': calendar_data,
        'current_month': month,
        'current_year': year,
        'days_in_month': days_in_month, 
        'favorite_meals': favorite_meals,
        'remainingcalories': remainingcalories,
        'active_link': 'record_list',
    })

def delete_meal(request, meal_id):
    if request.method == "POST":
        try:
            meal = Meal.objects.get(id=meal_id)
            meal.delete()
            return JsonResponse({"success": True})
        except Meal.DoesNotExist:
            return JsonResponse({"success": False, "error": "记录未找到"})
        
@csrf_exempt
def set_calorie_goal(request):
    if request.method == "POST":
        data = json.loads(request.body)
        new_goal = data.get('goal')
        if new_goal:
            request.session['daily_calorie_goal'] = int(new_goal)  # 将新的目标卡路里存储到会话中
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def get_calendar_data(request, year, month):
     
    daily_calorie_goal = request.session.get('daily_calorie_goal', 2000)  # 设置每日卡路里目标（可以根据需求调整）
    
    # 根据传入的年和月，生成对应的日历数据
    days_in_month = list(range(1, calendar.monthrange(year, month)[1] + 1))
    today = datetime.now()
    calendar_data = {}

    for day in days_in_month:
        date_key = f"{year}-{month:02d}-{day:02d}"
        date_object = datetime.strptime(date_key, "%Y-%m-%d").date()

        meals_for_day = Meal.objects.filter(created_at=date_object)
        total_intake = sum(meal.calories for meal in meals_for_day)

        if date_object <= today.date():
            if meals_for_day:
                if 0.8 * daily_calorie_goal <= total_intake <= 1.2 * daily_calorie_goal:
                    color = "green"
                elif total_intake < 0.8 * daily_calorie_goal:
                    color = "yellow"
                else:
                    color = "red"
            else:
                color = "white"
        else:
            continue

        percentage = (total_intake / daily_calorie_goal) * 100 if daily_calorie_goal > 0 else 0
        calendar_data[date_key] = color

    return JsonResponse(calendar_data)


def meal_search_ajax(request):

    query = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    page_size = 5  # 每页显示 5 条记录

    meals = Meal.objects.filter(name__icontains=query)
    total_count = meals.count()
    meals = meals[(page - 1) * page_size:page * page_size]

    meal_type_order = {
    'breakfast': 0,
    'lunch': 1,
    'dinner': 2,
    'more': 3,
    }

    # 排序 meals 列表
    meals = sorted(meals, key=lambda x: meal_type_order.get(x.meal_type, 4))

    data = []
    for meal in meals:
        data.append({
            
            'name': meal.name,
            'image_url': meal.image.url if meal.image else None,
            'comment': meal.comment,
            'calories': meal.calories,
            'meal_type_display': meal.get_meal_type_display(),
            'created_at': meal.created_at.strftime('%Y-%m-%d'),  # 格式化日期为 YYYY-MM-DD
        })

    return JsonResponse({
        'data': data,
        'total_count': total_count,
        'page': page,
        'page_size': page_size,
    })