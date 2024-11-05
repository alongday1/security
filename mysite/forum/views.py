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

def base_view(request):
    user = request.user
    if request.user.is_authenticated:
        condition1 = JoinRequest.objects.filter(sponser=user, state=0).exists()
        condition2 = JoinRequest.objects.filter(user=user, state=1).exists()
        message_reminder_visible = condition1 or condition2
        is_authenticated = True
    else:
        message_reminder_visible = False
        is_authenticated = False
    return message_reminder_visible,is_authenticated

def forum_message_view(request):
    current_user = request.user
    post_request_unfinished = JoinRequest.objects.filter(Q(sponser=current_user, state=0)|Q(user=current_user, state=1))
    post_request_finished = JoinRequest.objects.filter(Q(sponser=current_user, state__gt=0)|Q(user=current_user, state=2))
    unfinished_count = post_request_unfinished.count()
    finished_count = post_request_finished.count()

    post_unfinished_paginator = Paginator(post_request_unfinished, 8)
    post_finished_paginator = Paginator(post_request_finished, 8)

    post_unfinished_page_number = request.GET.get('post_unfinished_page', 1)
    post_finished_page_number = request.GET.get('post_finished_page', 1)    

    post_unfinished_page_obj = post_unfinished_paginator.get_page(post_unfinished_page_number)
    post_finished_page_obj = post_finished_paginator.get_page(post_finished_page_number)

    message_reminder_visible,is_authenticated = base_view(request)
    return render(request,'post_message.html',{'message_reminder_visible': message_reminder_visible,'is_authenticated':is_authenticated,'current_user':current_user,'unfinished_count':unfinished_count,'post_unfinished_page_obj':post_unfinished_page_obj,'post_finished_page_obj':post_finished_page_obj,'finished_count':finished_count,})

def forum_home_view(request):
    message_reminder_visible,is_authenticated = base_view(request)
    response = requests.get("https://canteen.sjtu.edu.cn/CARD/Ajax/Place")
    canteen_data = response.json()
    group_posts = GroupPost.objects.order_by('-create_at')[:3]
    posts = Post.objects.order_by('-click')[:5]
    return render(request,'forum.html', {'is_authenticated':is_authenticated,'active_link': 'forum_home','canteen_data': canteen_data,'group_posts': group_posts,'posts':posts,'message_reminder_visible': message_reminder_visible,})

def forum_post_view(request, forum_id=0):
    tag_name = request.GET.get('tag', None)
    message_reminder_visible,is_authenticated = base_view(request)
    forums = Forum.objects.all()
    if forum_id == 0:
        forum_target = None
        selected_forum_id = None
        if tag_name:
            posts = Post.objects.filter(tag__name=tag_name).order_by('-last_modified')
        else:
            posts = Post.objects.all().order_by('-last_modified')
    else:
        forum_target = get_object_or_404(Forum, id=forum_id)
        selected_forum_id = forum_target.id
        if tag_name:
            posts = Post.objects.filter(forum=forum_target, tag__name=tag_name).order_by('-last_modified')
        else:
            posts = Post.objects.filter(forum=forum_target).order_by('-last_modified')
    
    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    tag_counts = Tag.objects.annotate(post_count=Count('post')).values('name', 'post_count')
    tag_count = [{'name': tag['name'], 'value': tag['post_count']} for tag in tag_counts]

    return render(request,'forum_post.html',{'is_authenticated':is_authenticated,'tag_count':tag_count,'active_link': 'forum_home','forums':forums,'posts':page_obj,'selected_forum_id': selected_forum_id,'forum_target':forum_target,'message_reminder_visible': message_reminder_visible,'tag_name':tag_name,})

def group_post_view(request):
    message_reminder_visible,is_authenticated = base_view(request)
    forums = Forum.objects.all()
    group_posts = GroupPost.objects.order_by('-create_at')

    paginator = Paginator(group_posts, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    tag_counts = Tag.objects.annotate(post_count=Count('post')).values('name', 'post_count')
    tag_count = [{'name': tag['name'], 'value': tag['post_count']} for tag in tag_counts]

    return render(request,'group_post_list.html',{'is_authenticated':is_authenticated,'tag_count':tag_count,'active_link': 'forum_home','forums':forums,'group_posts':page_obj,'message_reminder_visible': message_reminder_visible,})


def post_detail(request, uuid):
    current_user = request.user
    message_reminder_visible,is_authenticated = base_view(request)
    forums = Forum.objects.all()
    post = get_object_or_404(Post, id=uuid)
    post.click += 1
    content = markdown(post.content)
    post.save(update_fields=['click'])
    return render(request, 'post_detail.html', {'is_authenticated':is_authenticated,'active_link': 'forum_home','forums':forums,'post': post,'message_reminder_visible': message_reminder_visible,'current_user':current_user,'content':content,})

def group_detail(request, uuid):
    message_reminder_visible,is_authenticated = base_view(request)
    current_user = request.user
    forums = Forum.objects.all()
    current_time = timezone.now()
    group_post = get_object_or_404(GroupPost, id=uuid)
    content = markdown(group_post.content)
    return render(request, 'group_post_detail.html', {'is_authenticated':is_authenticated,'active_link': 'forum_home','forums':forums,'group_post': group_post,'current_time':current_time,'current_user':current_user,'message_reminder_visible': message_reminder_visible,'content':content,})

@csrf_exempt
def create_tag(request):
    if request.method == 'POST':
        tag_name = request.POST.get('name')
        if tag_name and not Tag.objects.filter(name=tag_name).exists():
            new_tag = Tag.objects.create(name=tag_name)
            return JsonResponse({'status': 'success', 'name': new_tag.name})
        else:
            return JsonResponse({'status': 'error', 'message': 'Tag already exists or invalid name.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required 
def post_create_view(request):
    message_reminder_visible,is_authenticated = base_view(request)
    current_user = request.user
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = "Guest"

    forums = Forum.objects.all()
    tags = Tag.objects.all()
    if request.method == 'POST':
        try:
            post_type = request.POST.get('type')
            if (post_type == 'normal'):
                title = request.POST.get('title')
                forum_id = request.POST.get('forum_name')
                content = request.POST.get('content')
                tags_string = request.POST.get('tags')
                tags = [tag.strip() for tag in tags_string.split(',')] if tags_string else []
                forum = Forum.objects.get(id=forum_id)
                author = request.user
                
                post = Post.objects.create(
                    title=title,
                    author=author,
                    forum=forum,
                    content=content
                )
                
                if request.FILES.getlist('images'):
                    for image_file in request.FILES.getlist('images'):
                        post_image = PostImage.objects.create(image=image_file)
                        post.images.add(post_image)
                
                for tag_name in tags:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    post.tag.add(tag)
                
                messages.success(request, 'Post created successfully!')
            else :
                title = request.POST.get('title1')
                content = request.POST.get('content1')
                sponser = request.user
                address = request.POST.get('address')
                target_time_str = request.POST.get('target_time')
                max_participants = request.POST.get('max')
                min_participants = request.POST.get('min')
                target_time = datetime.strptime(target_time_str, '%B %d, %Y %I:%M %p')
                target_time = timezone.make_aware(target_time)

                group_post = GroupPost.objects.create(
                    title = title,
                    sponser = sponser,
                    content = content,
                    address = address,
                    target_time = target_time,
                    max_participants = max_participants,
                    min_participants = min_participants
                )

                group_post.participants.add(sponser)
                messages.success(request, 'Post created successfully!')

            return JsonResponse({'status': 'success', 'message': 'Post created successfully!'})
        
        except Exception as e:
            if (post_type == 'normal'):
                context = {
                    'username': request.user.username,
                    'forums': Forum.objects.all(),
                    'tags': Tag.objects.all(),
                    'post_type': post_type,
                    'title': title,
                    'forum_id': forum_id,
                    'content': content,
                    'selected_tags': tags,
                    'error_message': str(e),
                    'is_authenticated':is_authenticated,
                }
            else:
                context = {
                    'username': request.user.username,
                    'forums': Forum.objects.all(),
                    'post_type': post_type,
                    'title': title,
                    'address': address,
                    'target_time':target_time_str,
                    'max':max_participants,
                    'min':min_participants,
                    'content': content,
                    'error_message': str(e),
                    'is_authenticated':is_authenticated,
                }
            return render(request, 'post_add.html', context)
    
    return render(request,'post_add.html', {'is_authenticated':is_authenticated,'active_link': 'forum_home','forums':forums,'username': username,'tags':tags,'message_reminder_visible': message_reminder_visible,})

def join_group(request, group_post_id):
    if request.method == 'POST':
        try:
            group_post = get_object_or_404(GroupPost, id=group_post_id)
            is_valid = True
            if timezone.now() > group_post.target_time:
                is_valid = False
            
            join_request = JoinRequest.objects.create(
                user=request.user, 
                target_post=group_post,
                is_valid = is_valid,
                sponser = group_post.sponser
            )

            return JsonResponse({'status': 'success'})
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'You have already requested to join this group.'}) 

def pass_request(request, join_request_id):
    join_request = get_object_or_404(JoinRequest, id=join_request_id)
    if request.method == "POST":
        join_request.state += 1
        join_request.is_comfirmed = True
        join_request.save()
        post_request = join_request.target_post
        post_request.participants.add(join_request.user)
        post_request.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def reject_request(request, join_request_id):
    join_request = get_object_or_404(JoinRequest, id=join_request_id)
    if request.method == "POST":
        join_request.state += 1
        join_request.is_denied = True
        join_request.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def confirm_request(request, join_request_id):
    join_request = get_object_or_404(JoinRequest, id=join_request_id)
    if request.method == "POST":
        join_request.state += 1
        join_request.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': True})

@require_http_methods(["DELETE"])
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return JsonResponse({'message': 'Post deleted successfully.'}, status=204)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found.'}, status=404)

@require_http_methods(["DELETE"])
def delete_group_post(request, post_id):
    try:
        post = GroupPost.objects.get(id=post_id)
        post.delete()
        return JsonResponse({'message': 'Post deleted successfully.'}, status=204)
    except GroupPost.DoesNotExist:
        return JsonResponse({'error': 'Post not found.'}, status=404)

def edit_post(request, post_id):
    message_reminder_visible,is_authenticated = base_view(request)
    current_user = request.user
    forums = Forum.objects.all()
    tags = Tag.objects.all()
    post = Post.objects.get(id=post_id)
    title = post.title
    forum_id = post.forum.id
    content = post.content
    tag_names = post.tag.values_list('name', flat=True)
    author = post.author

    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            forum_id = request.POST.get('forum_name')
            content = request.POST.get('content')
            tags_string = request.POST.get('tags')
            tags = [tag.strip() for tag in tags_string.split(',')] if tags_string else []
            forum = Forum.objects.get(id=forum_id)
            author = request.user

            post.title = title
            post.forum = forum
            post.content = content
            print(content)

            post.save()

            if request.FILES.getlist('images'):
                for image_file in request.FILES.getlist('images'):
                    post_image = PostImage.objects.create(image=image_file)
                    post.images.add(post_image)
            
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                if not post.tag.filter(name= tag.name).exists():
                    post.tag.add(tag)

            messages.success(request, 'Post edited successfully!')

            return JsonResponse({'status': 'success', 'message': 'Post edited successfully!'})

        except Exception as e:
            context = {
                'username': request.user.username,
                'forums': Forum.objects.all(),
                'tags': Tag.objects.all(),
                'title': title,
                'forum_id': forum_id,
                'content': content,
                'tag_names': tags_string,
                'error_message': str(e),
                'post_id':post_id,
                'is_authenticated':is_authenticated,
            }
            return render(request, 'post_edit.html', context)
    
    return render(request,'post_edit.html',{'is_authenticated':is_authenticated,'active_link': 'forum_home','forums':forums,'tags':tags,'message_reminder_visible': message_reminder_visible,'username': current_user,'title':title,'forum_id':forum_id,'content':content,'tag_names':tag_names,'author':author,'post_id':post_id,})

def edit_group_post(request, post_id):
    message_reminder_visible,is_authenticated = base_view(request)
    current_user = request.user
    group_post = GroupPost.objects.get(id=post_id)
    title = group_post.title
    content = group_post.content
    sponser = group_post.sponser
    max_participants = group_post.max_participants
    min_participants = group_post.min_participants
    address = group_post.address
    target_time = group_post.target_time
    target_time_str = target_time.strftime('%B %d, %Y %I:%M %p')

    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = "Guest"

    if request.method == 'POST':
        try:
            title = request.POST.get('title1')
            content = request.POST.get('content1')
            sponser = request.user
            address = request.POST.get('address')
            target_time_str = request.POST.get('target_time')
            max_participants = request.POST.get('max')
            min_participants = request.POST.get('min')
            target_time = datetime.strptime(target_time_str, '%B %d, %Y %I:%M %p')
            target_time = timezone.make_aware(target_time)

            group_post = GroupPost.objects.create(
                title = title,
                sponser = sponser,
                content = content,
                address = address,
                target_time = target_time,
                max_participants = max_participants,
                min_participants = min_participants
            )

            group_post.participants.add(sponser)
            messages.success(request, 'GroupPost edited successfully!')

            return JsonResponse({'status': 'success', 'message': 'GroupPost edited successfully!'})
        
        except Exception as e:
            context = {
                'username': request.user.username,
                'title': title,
                'address': address,
                'target_time':target_time_str,
                'max':max_participants,
                'min':min_participants,
                'content': content,
                'error_message': str(e),
                'is_authenticated':is_authenticated,
            }
            return render(request, 'group_post_edit.html', context)
    
    return render(request,'group_post_edit.html', {'username': request.user.username,'active_link': 'forum_home','message_reminder_visible': message_reminder_visible,'title': title,'address': address,'target_time':target_time_str,'max':max_participants,'min':min_participants,'content': content,'is_authenticated':is_authenticated,})