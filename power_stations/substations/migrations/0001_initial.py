# Generated by Django 5.1.4 on 2024-12-26 22:02

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MaintenanceStatus",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Название статуса"),
                ),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
            ],
            options={
                "verbose_name": "Статус обслуживания",
                "verbose_name_plural": "Статусы обслуживания",
            },
        ),
        migrations.CreateModel(
            name="SubstationGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
                ),
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Название группы"),
                ),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                (
                    "responsible_person",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Ответственное лицо"
                    ),
                ),
                (
                    "contact_info",
                    models.TextField(blank=True, verbose_name="Контактная информация"),
                ),
            ],
            options={
                "verbose_name": "Группа подстанций",
                "verbose_name_plural": "Группы подстанций",
            },
        ),
        migrations.CreateModel(
            name="SubstationType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
                ),
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Название типа"),
                ),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
            ],
            options={
                "verbose_name": "Тип подстанции",
                "verbose_name_plural": "Типы подстанций",
            },
        ),
        migrations.CreateModel(
            name="Substation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Наименование")),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="substations/",
                        verbose_name="Изображение",
                    ),
                ),
                (
                    "published_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Дата публикации",
                    ),
                ),
                ("power", models.FloatField(verbose_name="Мощность (МВА)")),
                ("voltage", models.FloatField(verbose_name="Напряжение (кВ)")),
                ("city", models.CharField(max_length=100, verbose_name="Город")),
                ("address", models.TextField(verbose_name="Адрес")),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Активна"),
                ),
                (
                    "last_maintenance",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Последнее обслуживание"
                    ),
                ),
                (
                    "next_maintenance",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Следующее обслуживание"
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="Примечания")),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="substations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
                (
                    "connected_substations",
                    models.ManyToManyField(
                        blank=True,
                        to="substations.substation",
                        verbose_name="Соединённые подстанции",
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="substations",
                        to="substations.substationgroup",
                        verbose_name="Группа подстанций",
                    ),
                ),
                (
                    "substation_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="substations.substationtype",
                        verbose_name="Тип подстанции",
                    ),
                ),
            ],
            options={
                "verbose_name": "Подстанция",
                "verbose_name_plural": "Подстанции",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="MaintenanceRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
                ),
                (
                    "scheduled_date",
                    models.DateTimeField(verbose_name="Запланированная дата"),
                ),
                (
                    "completed_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Дата выполнения"
                    ),
                ),
                ("description", models.TextField(verbose_name="Описание работ")),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Активна"),
                ),
                (
                    "status",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="substations.maintenancestatus",
                        verbose_name="Статус",
                    ),
                ),
                (
                    "substation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="maintenance_records",
                        to="substations.substation",
                        verbose_name="Подстанция",
                    ),
                ),
            ],
            options={
                "verbose_name": "Запись об обслуживании",
                "verbose_name_plural": "Записи об обслуживании",
                "ordering": ["-scheduled_date"],
            },
        ),
    ]
