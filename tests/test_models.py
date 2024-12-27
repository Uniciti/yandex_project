# tests/test_models.py
import pytest
from django.utils import timezone
from datetime import timedelta
from substations.models import (
    Substation, 
    SubstationType,
    SubstationGroup,
    MaintenanceStatus,
    MaintenanceRecord
)

# Базовые фикстуры для моделей
@pytest.fixture
def substation_type(db):
    """Фикстура для создания типа подстанции"""
    return SubstationType.objects.create(
        name="Тестовый тип",
        description="Описание тестового типа"
    )

@pytest.fixture
def maintenance_status(db):
    """Фикстура для создания статуса обслуживания"""
    return MaintenanceStatus.objects.create(
        name="Плановое",
        description="Плановое обслуживание"
    )

@pytest.fixture
def substation_group(db):
    """Фикстура для создания группы подстанций"""
    return SubstationGroup.objects.create(
        name="Тестовая группа",
        description="Описание тестовой группы",
        responsible_person="Иванов И.И."
    )

@pytest.fixture
def substation(db):
    """Фикстура для создания подстанции"""
    return Substation.objects.create(
        name="ПС-110 Тестовая",
        power=100,
        voltage=110,
        city="Москва",
        address="ул. Тестовая, 1"
    )

@pytest.mark.django_db
class TestSubstationModel:
    """Тесты для модели подстанции"""
    
    def test_create_substation(self):
        """Тест создания подстанции с минимальными данными"""
        substation = Substation.objects.create(
            name="ПС-110 Тестовая",
            power=100,
            voltage=110,
            city="Москва",
            address="ул. Тестовая, 1"
        )
        assert substation.pk is not None
        assert str(substation) == "ПС-110 Тестовая (110 кВ)"
        
    def test_city_normalization(self):
        """Тест нормализации названия города"""
        substation = Substation.objects.create(
            name="ПС-110 Тестовая",
            power=100,
            voltage=110,
            city="мОсКвА",
            address="ул. Тестовая, 1"
        )
        assert substation.city == "Москва"
        
    def test_substation_with_type(self, substation_type):
        """Тест создания подстанции с типом"""
        substation = Substation.objects.create(
            name="ПС-110 Тестовая",
            substation_type=substation_type,
            power=100,
            voltage=110,
            city="Москва",
            address="ул. Тестовая, 1"
        )
        assert substation.substation_type == substation_type
        
    def test_get_active_substations(self):
        """Тест получения активных подстанций"""
        # Создаем активную подстанцию с актуальным обслуживанием
        now = timezone.now()
        active_substation = Substation.objects.create(
            name="Активная ПС",
            power=100,
            voltage=110,
            city="Москва",
            address="ул. Тестовая, 1",
            is_active=True,
            last_maintenance=now - timedelta(days=30),
            next_maintenance=now + timedelta(days=30)
        )
        
        # Создаем неактивную подстанцию
        inactive_substation = Substation.objects.create(
            name="Неактивная ПС",
            power=100,
            voltage=110,
            city="Москва",
            address="ул. Тестовая, 2",
            is_active=False,
            last_maintenance=now - timedelta(days=30),
            next_maintenance=now + timedelta(days=30)
        )
        
        active_substations = Substation.get_active_substations()
        assert active_substation in active_substations
        assert inactive_substation not in active_substations

@pytest.mark.django_db
class TestMaintenanceRecord:
    """Тесты для записей об обслуживании"""
    
    def test_create_maintenance_record(self, substation, maintenance_status):
        """Тест создания записи об обслуживании"""
        scheduled_date = timezone.now() + timedelta(days=1)
        record = MaintenanceRecord.objects.create(
            substation=substation,
            status=maintenance_status,
            scheduled_date=scheduled_date,
            description="Тестовое обслуживание"
        )
        assert record.pk is not None
        assert record.completed_date is None
        
    def test_complete_maintenance(self, substation, maintenance_status):
        """Тест завершения обслуживания"""
        scheduled_date = timezone.now() + timedelta(days=1)
        record = MaintenanceRecord.objects.create(
            substation=substation,
            status=maintenance_status,
            scheduled_date=scheduled_date,
            description="Тестовое обслуживание"
        )
        
        completed_date = timezone.now() + timedelta(days=2)
        record.completed_date = completed_date
        record.save()
        
        assert record.completed_date is not None

@pytest.mark.django_db
class TestSubstationGroup:
    """Тесты для групп подстанций"""
    
    def test_create_group(self):
        """Тест создания группы подстанций"""
        group = SubstationGroup.objects.create(
            name="Тестовая группа",
            description="Описание тестовой группы",
            responsible_person="Иванов И.И.",
            contact_info="test@example.com"
        )
        assert group.pk is not None
        assert str(group) == "Тестовая группа"
        
    def test_add_substation_to_group(self, substation):
        """Тест добавления подстанции в группу"""
        group = SubstationGroup.objects.create(
            name="Тестовая группа"
        )
        substation.group = group
        substation.save()
        
        assert group.substations.count() == 1
        assert group.substations.first() == substation