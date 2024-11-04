from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=15, unique=True)
    type = models.PositiveIntegerField(default=0)
    # 0：其他  1：类别  2：口味  3：风格  4：食材  5：价位

    def __str__(self):
        return self.name


class Canteen(models.Model):
    name = models.CharField(max_length=40)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField(max_length=40, default='')
    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE, related_name='dishes')
    description = models.TextField(blank=True)  # 菜品描述
    tags = models.ManyToManyField(Tag, related_name='dishes')  # 多对多字段，关联多个标签
    count_comment = models.IntegerField(
        validators=[
            MinValueValidator(0)  # 最小值为0
        ],
        default=0
    )
    rating = models.FloatField(
        null=True,  # 允许 NULL 值
        blank=True,  # 在表单中允许为空
        validators=[
            MinValueValidator(0.0),  # 最小值为 0.0
            MaxValueValidator(5.0)  # 最大值为 5.0
        ]
    )
    main_image = models.ForeignKey('DishImage', on_delete=models.CASCADE, related_name='main_dish', null=True, blank=True)
    count_like = models.IntegerField(
        validators=[
            MinValueValidator(0)  # 最小值为0
        ],
        default=0
    )
    count_unlike = models.IntegerField(
        validators=[
            MinValueValidator(0)  # 最小值为0
        ],
        default=0
    )

    def __str__(self):
        return self.name


class DishImage(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='images')  # 关联的菜品
    image = models.ImageField(upload_to='dish_images/')  # 图片文件,upload_to参数定义了图片存储的文件夹路径
    is_main = models.BooleanField(default=False) # 是否为该菜品的代表图


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', null=True)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=1000)
    datetime = models.DateTimeField(default=timezone.now)  # 设置默认值为当前日期和时间


class CommentImage(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='images')  # 关联的评论
    image = models.ImageField(upload_to='comment_images/')  # 图片文件,upload_to参数定义了图片存储的文件夹路径


class Rating(models.Model):
    value = models.IntegerField(
        validators=[
            MinValueValidator(1),  # 最小值为1
            MaxValueValidator(5)  # 最大值为5
        ],
        default=5
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='ratings', null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'dish'], name='unique_user_dish_rating')
        ]


