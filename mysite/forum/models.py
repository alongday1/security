from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField(max_length=20,unique=True)

    def __str__(self):
        return self.name

class Forum(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)
    description = models.TextField(null=True,blank=True)
    notice = models.TextField(null=True,blank=True)
    icon = models.ImageField(upload_to='icons/', null=True, blank=True)
    creator = models.ForeignKey(User, related_name='created_forums',on_delete=models.SET_NULL,null=True)
    administrators = models.ManyToManyField(User)

    def __str__(self):
        return self.name

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100,blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    forum = models.ForeignKey(Forum,on_delete=models.CASCADE,blank=False)
    create_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    # restaurant = models.ForeignKey(to_be_determined,on_delete=models.SET_NULL,null=True)
    content = models.TextField(blank=False)
    images = models.ManyToManyField('PostImage', related_name='post_images', blank=True,null=True)
    tag = models.ManyToManyField(Tag)
    click = models.IntegerField(default=0,db_index=True)
    likes = models.IntegerField(default=0)  

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if 'update_fields' in kwargs and any(field in kwargs['update_fields'] for field in ['title', 'content','imaged']):
            self.last_modified = timezone.now() 
        super().save(*args, **kwargs)

class GroupPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100,blank=False)
    create_at = models.DateTimeField(auto_now_add=True)
    target_time = models.DateTimeField(db_index=True,blank=False)
    sponser = models.ForeignKey(User, related_name='sponsered_posts', on_delete=models.CASCADE)
    content = models.TextField(blank=True,null=True)
    address = models.CharField(max_length=40,blank=False)
    participants = models.ManyToManyField(User,related_name="joined_user")
    max_participants = models.IntegerField(default=2)
    min_participants = models.IntegerField(default=2)
    # restaurant = models.ForeignKey(to_be_determined,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return self.title

class JoinRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User,related_name='request_user',on_delete=models.CASCADE)
    sponser = models.ForeignKey(User,related_name='join_group_requested_user',on_delete=models.CASCADE)
    target_post = models.ForeignKey(GroupPost,related_name='join_group_request',on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateField(auto_now=True)
    is_confirmed = models.BooleanField(default=False)
    is_denied = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    state = models.IntegerField(default=0) # 0:created 1:sponser confirmed 2:user confirmed

    def __str__(self):
        return str(self.id)

    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['user', 'target_post'], name='unique_user_targetpost')
            ]

class PostImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.FileField(upload_to='illustrations/')