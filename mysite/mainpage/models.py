from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Canteen(models.Model):
    name = models.CharField(max_length=40)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField(max_length=40)
    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE, related_name='dishes')
    description = models.TextField(blank=True)  # 菜品描述
    tags = models.ManyToManyField(Tag, related_name='dishes')  # 多对多字段，关联多个标签

    def __str__(self):
        return self.name


class DishImage(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='images')  # 关联的菜品
    image = models.ImageField(upload_to='dish_images/')  # 图片文件,upload_to参数定义了图片存储的文件夹路径


class Comment(models.Model):
    user = models.CharField(max_length=40) # 待改，后续关联到user的模型中
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=1000)
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),  # 最小值为1
            MaxValueValidator(5)  # 最大值为5
        ],
        default=5
    )
    datetime = models.DateTimeField(default=timezone.now)  # 设置默认值为当前日期和时间


class CommentImage(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='images')  # 关联的评论
    image = models.ImageField(upload_to='comment_images/')  # 图片文件,upload_to参数定义了图片存储的文件夹路径