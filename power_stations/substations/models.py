# substations/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class CreatedAtUpdatedAt(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        abstract = True

class MaintenanceStatus(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название статуса"
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True
    )

    class Meta:
        verbose_name = "Статус обслуживания"
        verbose_name_plural = "Статусы обслуживания"

    def __str__(self):
        return self.name

class SubstationType(CreatedAtUpdatedAt):
    name = models.CharField(
        max_length=100,
        verbose_name="Название типа"
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True
    )

    class Meta:
        verbose_name = "Тип подстанции"
        verbose_name_plural = "Типы подстанций"

    def __str__(self):
        return self.name

class SubstationGroup(CreatedAtUpdatedAt):
    name = models.CharField(
        max_length=100,
        verbose_name="Название группы"
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True
    )
    responsible_person = models.CharField(
        max_length=200,
        verbose_name="Ответственное лицо",
        blank=True
    )
    contact_info = models.TextField(
        verbose_name="Контактная информация",
        blank=True
    )

    class Meta:
        verbose_name = "Группа подстанций"
        verbose_name_plural = "Группы подстанций"

    def __str__(self):
        return self.name

class MaintenanceRecord(CreatedAtUpdatedAt):
    substation = models.ForeignKey(
        'Substation',
        on_delete=models.CASCADE,
        related_name='maintenance_records',
        verbose_name="Подстанция"
    )
    status = models.ForeignKey(
        MaintenanceStatus,
        on_delete=models.PROTECT,
        verbose_name="Статус"
    )
    scheduled_date = models.DateTimeField(
        verbose_name="Запланированная дата"
    )
    completed_date = models.DateTimeField(
        verbose_name="Дата выполнения",
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name="Описание работ"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна"
    )

    class Meta:
        verbose_name = "Запись об обслуживании"
        verbose_name_plural = "Записи об обслуживании"
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"Обслуживание {self.substation.name} - {self.scheduled_date.date()}"

class Substation(CreatedAtUpdatedAt):
    name = models.CharField(
        max_length=200,
        verbose_name="Наименование"
    )

    image = models.ImageField(
        upload_to='substations/',
        blank=True,
        null=True,
        verbose_name="Изображение"
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='substations',
        verbose_name="Автор"
    )
    published_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата публикации"
    )

    substation_type = models.ForeignKey(
        SubstationType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Тип подстанции"
    )
    power = models.FloatField(
        verbose_name="Мощность (МВА)"
    )
    voltage = models.FloatField(
        verbose_name="Напряжение (кВ)"
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Город"
    )
    address = models.TextField(
        verbose_name="Адрес"
    )
    group = models.ForeignKey(
        SubstationGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='substations',
        verbose_name="Группа подстанций"
    )
    connected_substations = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        verbose_name="Соединённые подстанции"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна"
    )
    last_maintenance = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Последнее обслуживание"
    )
    next_maintenance = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Следующее обслуживание"
    )
    notes = models.TextField(
        verbose_name="Примечания",
        blank=True
    )
    

    class Meta:
        verbose_name = "Подстанция"
        verbose_name_plural = "Подстанции"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.voltage} кВ)"

    def save(self, *args, **kwargs):
        if self.city:
            self.city = self.city.strip().title()
        super().save(*args, **kwargs)

    @staticmethod
    def get_active_substations():
        now = timezone.now()
        return Substation.objects.filter(
            is_active=True,
            last_maintenance__isnull=False,
            next_maintenance__gt=now
        )