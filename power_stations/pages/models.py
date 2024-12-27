# pages/models.py
from django.db import models
from django.urls import reverse

class StaticPage(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="URL"
    )
    content = models.TextField(
        verbose_name="Содержание"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликована"
    )

    class Meta:
        verbose_name = "Статическая страница"
        verbose_name_plural = "Статические страницы"
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('pages:page_detail', kwargs={'slug': self.slug})