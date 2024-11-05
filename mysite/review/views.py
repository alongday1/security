from django.shortcuts import render, redirect
from review.models import *
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from mysite.settings import MEDIA_ROOT, MEDIA_URL
from django.db import IntegrityError
from django.template import TemplateDoesNotExist
from django.db.models import Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from decimal import Decimal
import os
import uuid
import json

# Create your views here.

def review(request):
    tags = Tag.objects.all()
    tags_1 = Tag.objects.filter(type=1)
    tags_2 = Tag.objects.filter(type=2)
    tags_3 = Tag.objects.filter(type=3)
    tags_4 = Tag.objects.filter(type=4)
    tags_5 = Tag.objects.filter(type=5)
    tags_0 = Tag.objects.filter(type=0)
    canteen_list = Canteen.objects.all()
    canteen_names = [canteen.name for canteen in canteen_list]  # 提取 name 列表
    return render(request, "review.html", {
        "restaurants": canteen_list,
        "tags": tags,
        "tags_1": tags_1,
        "tags_2": tags_2,
        "tags_3": tags_3,
        "tags_4": tags_4,
        "tags_5": tags_5,
        "tags_0": tags_0,
        "canteen_names": canteen_names
    })


def add_tag(request):
    if request.method == 'POST':
        new_tag_name = request.POST.get('new-tag')
        print("new-tag", new_tag_name)
        if (request.user.is_authenticated == False):
            return JsonResponse({'success': False, 'error': "请先登录！"})
        try:
            new_tag = Tag.objects.create(name=new_tag_name, type=0)
            new_tag.save()
            return JsonResponse({'success': True})  # 返回成功响应
        except IntegrityError:
            return JsonResponse({'success': False, 'error': "该tag已存在！"})  # 返回错误响应

    return JsonResponse({'success': False, 'error': "无效的请求！"})  # 处理无效请求


def add_dish(request):
    if request.method == "POST":
        if request.user.is_authenticated == False:
            return JsonResponse({'message': "请先登录！"})

        dish_name = request.POST.get('dishName')
        canteen = request.POST.get('canteen')
        description = request.POST.get('description')

        new_dish = Dish.objects.create(
            name=dish_name,
            canteen=Canteen.objects.get(name=canteen),
            description=description,
        )
        new_dish.save()

        # 图片处理
        image = request.FILES.get('file-input')
        upload_dir = os.path.join(MEDIA_ROOT, 'dish_images')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        ext = image.name.split('.')[-1]  # 获取文件扩展名
        filename = f"{dish_name}.{ext}"
        file_path = os.path.join(upload_dir, filename)
        relative_path = os.path.join('dish_images/', filename)

        print(f"Saving image {image.name} to {file_path}")
        # 使用 `with open` 将图片保存到本地
        with open(file_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        if os.path.exists(file_path):
            print(f"Image {filename} saved successfully!")
            dish_image = DishImage.objects.create(
                dish=new_dish,
                image=relative_path,
                is_main=True,
            )
            dish_image.save()
            new_dish.main_image=dish_image
            new_dish.save()
        else:
            print(f"Failed to save image {filename}.")

        return JsonResponse({"message": "菜品添加成功！"})
    return JsonResponse({"error": "请求方法错误"}, status=400)


def get_dishes_by_search(request):
    # 获取对应餐厅的所有菜品
    canteen_id = request.GET.get('canteen_id')
    if canteen_id == '0':
        dishes = Dish.objects.all()
        canteen_name = '全部'
    else:
        canteen_name = Canteen.objects.get(id=canteen_id).name
        dishes = Dish.objects.filter(canteen_id=canteen_id)

    # 获取名字包含搜索内容的菜品
    search_name = request.GET.get('search_name')
    if search_name:
        dishes = dishes.filter(name__icontains=search_name)

    # 获取对应tags的菜品
    included_tags = request.GET.get('included_tags')
    excluded_tags = request.GET.get('excluded_tags')
    if included_tags:  # 检查 included_tags 是否为空
        # 将字符串拆分为列表
        included_tags_list = included_tags.split(',')
        # 将字符串转换为整数
        included_tags_set = set(map(int, included_tags_list))
    else:
        included_tags_set = set()
    if excluded_tags:
        excluded_tags_list = excluded_tags.split(',')
        excluded_tags_set = set(map(int, excluded_tags_list))
    else:
        excluded_tags_set = set()

    # 不包含任一excludedTags的菜品
    dishes = dishes.exclude(
        tags__in=excluded_tags_set  # 排除包含 excludedTags 中任一标签的菜品
    ).distinct()  # 去重，确保每道菜只出现一次

    # 获取排序类型
    sort_category = request.GET.get('sort_category', 'name')  # 默认为按名字排序
    sort_order = request.GET.get('sort_order', 'asc')  # 默认为正序
    print("sort", sort_category, sort_order)
    if sort_category == 'comment_count':
        if sort_order == 'asc':
            dishes = dishes.order_by('count_comment')
        else:
            dishes = dishes.order_by('-count_comment')
    elif sort_category == 'name':
        if sort_order == 'asc':
            dishes = dishes.order_by('name')
        else:
            dishes = dishes.order_by('-name')
    elif sort_category == 'rating':
        if sort_order == 'asc':
            dishes = dishes.order_by('rating')
        else:
            dishes = dishes.order_by('-rating')

    # 包含所有includedTags的菜品
    filtered_dishes = []
    for dish in dishes:
        # 获取当前菜品的所有标签
        dish_tags = set(dish.tags.values_list('id', flat=True))
        # 检查菜品的标签是否包含所有的 included_tags
        if included_tags_set.issubset(dish_tags):
            filtered_dishes.append(dish)

    # 打印筛选结果
    for dish in filtered_dishes:
        print(dish.name)
        print(dish.main_image.image.url if dish.main_image else '')

    dishes_data = [{
        'id': dish.id,
        'name': dish.name,
        'description': dish.description,
        'canteen': dish.canteen.name,
        'rating': dish.rating,
        'count_comment': dish.count_comment,
        'image': dish.main_image.image.url if dish.main_image else '',
        'tags': [tag.name for tag in dish.tags.all()]  # 嵌套的集合，用于包含菜品的标签
    } for dish in filtered_dishes]
    return JsonResponse({
        'canteen_name': canteen_name,
        'dishes': dishes_data,
        'media_root': str(MEDIA_ROOT),
    })


def comments(request):
    dish_id = int(request.GET.get('dish_id'))
    dish = Dish.objects.get(id=dish_id)
    if dish.main_image:
        main_image = dish.main_image.image.url
    else:
        main_image = ''
    images = [image.image.url for image in dish.images.filter(is_main=False)]  # 获取每个非代表图的dishImage的URL

    count_rating = 0
    # 更新对应Dish的评分
    if dish.ratings.exists():
        count_rating = dish.ratings.count()
        average_rating = dish.ratings.aggregate(Avg('value'))['value__avg']
        # 将平均值保留一位小数
        if average_rating is not None:
            average_rating = round(average_rating, 1)
        dish.rating = average_rating
        dish.save()
    else:
        dish.rating = None
        dish.save()

    # 获取当前页码，默认为第一页
    page = request.GET.get('page', 1)
    # 将页码转换为整数，如果无法转换则捕获异常
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1  # 如果传递的页码不合法，默认为第一页
    # 设置每页显示 5 条评论
    paginator = Paginator(dish.comments.all(), 5)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)  # 如果请求页码超出范围，返回最后一页
    except PageNotAnInteger:
        page_obj = paginator.page(1)  # 如果请求页码不是整数，返回第一页

    value = ''
    if request.user.is_authenticated:
        try:
            current_rating = Rating.objects.get(user=request.user, dish=dish)
            value = str(current_rating.value)
        except Rating.DoesNotExist:
            value = ''

    return render(
        request, 'comment.html', {
            'dish_id': dish_id,
            'dish_name': dish.name,
            'dish_canteen': dish.canteen,
            'dish_description': dish.description,
            'main_image': main_image,
            'images': images,
            'count_rating': count_rating,
            'count_comment': dish.count_comment,
            'avg_rating': dish.rating,
            'current_rating': value,
            'rating_list': json.dumps([rating.value for rating in dish.ratings.all()]),
            'page_obj': page_obj,
            'tags': [tag.name for tag in dish.tags.all()],
            'all_tags': [tag.name for tag in Tag.objects.all()]
        })


def refresh_comments(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # 解析 JSON 数据
            dish_id = int(data.get('dish_id'))
            text = data.get('search_text', '')
            show_mine = data.get('show_mine', False)  # 默认为 'false'
            print("show_mine", show_mine)

            dish = Dish.objects.get(id=dish_id)
            print('dish', dish.name)
            comments = dish.comments.filter(content__icontains=text)
            print('comments', comments)

            show_mine_success = 'true'
            if show_mine == True:
                if request.user.is_authenticated:
                    print("user", request.user)
                    comments = comments.filter(user=request.user)
                else:
                    print("user", request.user)
                    show_mine_success = 'false'

            # 获取当前页码，默认为第一页
            page = data.get('page', 1)
            try:
                page = int(page)
            except (TypeError, ValueError):
                page = 1

            # 设置每页显示 5 条评论
            paginator = Paginator(comments, 5)
            try:
                page_obj = paginator.page(page)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            except PageNotAnInteger:
                page_obj = paginator.page(1)

            try:
                html = render_to_string('comments_partial.html', {'page_obj': page_obj, 'dish_id': dish_id})
            except TemplateDoesNotExist as e:
                print(f"Template does not exist: {e}")
            except Exception as e:
                print(f"Error rendering template: {e}")

            return JsonResponse({'html': html, 'show_mine_success': show_mine_success})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)  # 捕获并返回异常

    return JsonResponse({"error": "请求方法错误"}, status=400)


@login_required  # 要求用户登录才能提交
def submit_form(request, dish_id):
    referer_url = request.META.get('HTTP_REFERER', '/')
    current_dish = Dish.objects.get(id=dish_id)

    if request.method == 'POST':
        # 获取文本数据
        text = request.POST.get('post-message')
        rating = int(request.POST.get('rating'))
        # 将数据保存到数据库
        new_comment = Comment.objects.create(
            user=request.user,  # 假设你有登录的用户
            content=text,
            dish=current_dish,
        )
        new_comment.save()

        try:
            rating = Rating.objects.get(user=request.user, dish=current_dish)
        except Rating.DoesNotExist:
            new_rating = Rating.objects.create(
                user=request.user,
                value=rating,
                dish=current_dish,
            )
            new_rating.save()

        # 更新对应Dish的评分
        average_rating = current_dish.ratings.aggregate(Avg('value'))['value__avg']
        # 将平均值保留一位小数
        if average_rating is not None:
            average_rating = round(average_rating, 1)
        current_dish.rating = average_rating
        current_dish.save()

        # 更新Dish的评论数
        current_dish.count_comment = current_dish.comments.count()
        current_dish.save()

        # 获取上传的文件（图片）
        images = request.FILES.getlist('file-input')
        print('len', len(images))
        # 保存图片到指定的路径（例如 MEDIA_ROOT/uploads）
        upload_dir = os.path.join(MEDIA_ROOT, 'comment_images')
        # 如果目录不存在，则创建它
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        for image in images:
            if image:
                ext = image.name.split('.')[-1]  # 获取文件扩展名
                unique_filename = f"{uuid.uuid4()}.{ext}"  # 使用唯一文件名
                file_path = os.path.join(upload_dir, unique_filename)
                relative_path = os.path.join('comment_images/',unique_filename)
                print(f"Saving image {image.name} to {file_path}")
                # 使用 `with open` 将图片保存到本地
                with open(file_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

                if os.path.exists(file_path):
                    print(f"Image {unique_filename} saved successfully!")
                    submission2 = CommentImage.objects.create(
                        comment = new_comment,
                        image = relative_path,
                    )
                    submission2.save()
                else:
                    print(f"Failed to save image {unique_filename}.")

        return HttpResponseRedirect(referer_url)

    return HttpResponseRedirect(referer_url)


@login_required  # 要求用户登录才能提交
def submit_rating(request, dish_id):
    referer_url = request.META.get('HTTP_REFERER', '/')
    current_dish = Dish.objects.get(id=dish_id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        try:
            old_rating = Rating.objects.get(user=request.user, dish=current_dish)
            old_rating.value = rating
            old_rating.save()
        except Rating.DoesNotExist:
            new_rating = Rating.objects.create(
                user=request.user,
                value=rating,
                dish=current_dish,
            )
            new_rating.save()

        # 更新对应Dish的评分
        print('dict', current_dish.ratings.aggregate(Avg('value')))
        average_rating = current_dish.ratings.aggregate(Avg('value'))['value__avg']
        # 将平均值保留一位小数
        if average_rating is not None:
            average_rating = round(average_rating, 1)
        current_dish.rating = average_rating
        current_dish.save()

        return HttpResponseRedirect(referer_url)

    return HttpResponseRedirect(referer_url)


@login_required
def update_dish_info(request):
    if request.method == 'POST':
        try:
            # 解析 JSON 数据
            data = json.loads(request.body)
            tags = data.get('tags', [])  # 获取 tags，默认为空列表
            dish_id = int(data.get('dish_id'))  # 获取 dish_id
            desc = data.get('desc')
            print('tags', tags, 'desc', desc)
            dish = Dish.objects.get(id=dish_id)
            tag_objects = Tag.objects.filter(name__in=tags)
            dish.description = desc
            dish.tags.set(tag_objects)
            dish.save()

            return JsonResponse({'status': 'success', 'tags': tags, 'dish_id': dish_id})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({"error": "请求方法错误"}, status=400)


@login_required
def add_image(request):
    if request.method == "POST":
        dish_id = int(request.POST.get('dish_id'))
        dish = Dish.objects.get(id=dish_id)
        images = request.FILES.getlist("file-input")  # 获取上传的多张图片
        upload_dir = os.path.join(MEDIA_ROOT, 'dish_images')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        for image in images:
            if image:
                ext = image.name.split('.')[-1]  # 获取文件扩展名
                unique_filename = f"{uuid.uuid4()}.{ext}"  # 使用唯一文件名
                file_path = os.path.join(upload_dir, unique_filename)
                relative_path = os.path.join('dish_images/', unique_filename)
                print(f"Saving image {image.name} to {file_path}")
                # 使用 `with open` 将图片保存到本地
                with open(file_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

                if os.path.exists(file_path):
                    print(f"Image {unique_filename} saved successfully!")
                    dish_image = DishImage.objects.create(
                        dish=dish,
                        image=relative_path,
                    )
                    dish_image.save()
                else:
                    print(f"Failed to save image {unique_filename}.")

        updated_images = [image.image.url for image in dish.images.filter(is_main=False)]


        return JsonResponse({"updated_images": updated_images})
    return JsonResponse({"error": "请求方法错误"}, status=400)
