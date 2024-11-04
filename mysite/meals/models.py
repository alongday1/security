from django.db import models
from django.utils import timezone

class Meal(models.Model):
    name = models.CharField(max_length=100)
    meal_type = models.CharField(max_length=10, choices=[
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
        ('more', '加餐'),
    ])
    calories = models.PositiveIntegerField()
    created_at = models.DateField(default=timezone.now)  # 存储日期
    comment = models.TextField(null=True, blank=True) 
    image = models.ImageField(upload_to='meal_images/', null=True, blank=True) 

    def __str__(self):
        return self.name

    def get_meal_type_display(self):
        return dict(self._meta.get_field('meal_type').choices).get(self.meal_type)
