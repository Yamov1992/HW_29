from django.db import models

import users


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

class Ads(models.Model):
    name = models.CharField(max_length=250)
    author_id = models.ForeignKey('users.User', null = True, on_delete=models.CASCADE) #ссылка на файл и модель
    price = models.PositiveIntegerField()
    description = models.TextField()
    is_published = models.BooleanField()
    category_id = models.ForeignKey(Category, null = True, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="ads/", null=True, blank=True)


    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"

    def __str__(self):
        return self.name

class Selection(models.Model):
    name = models.CharField(max_length=250)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE)
    items = models.ManyToManyField(Ads)

    class Meta:
        verbose_name = "Подборка"
        verbose_name_plural = "Подборки"

    def __str__(self):
        return self.name


