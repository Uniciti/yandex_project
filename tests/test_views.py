# tests/test_views.py
import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from substations.models import (
    Substation,
    SubstationType,
    SubstationGroup,
    MaintenanceStatus,
    MaintenanceRecord
)

# Фикстуры для тестов представлений
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
def substation(db, substation_type, substation_group):
    """Фикстура для создания подстанции"""
    return Substation.objects.create(
        name="ПС-110 Тестовая",
        substation_type=substation_type,
        power=100,
        voltage=110,
        city="Москва",
        address="ул. Тестовая, 1",
        group=substation_group,
        is_active=True
    )

@pytest.fixture
def inactive_substation(db):
    """Фикстура для создания неактивной подстанции"""
    return Substation.objects.create(
        name="ПС-110 Неактивная",
        power=100,
        voltage=110,
        city="Санкт-Петербург",
        address="ул. Тестовая, 2",
        is_active=False
    )

@pytest.fixture
def maintenance_record(db, substation, maintenance_status):
    """Фикстура для создания записи об обслуживании"""
    return MaintenanceRecord.objects.create(
        substation=substation,
        status=maintenance_status,
        scheduled_date=timezone.now(),
        description="Тестовое обслуживание"
    )

@pytest.mark.django_db
class TestSubstationViews:
    """Тесты для представлений подстанций"""
    
    def test_substation_list_view(self, client, substation):
        """Тест списка подстанций"""
        url = reverse('substations:substation_list')
        response = client.get(url)
        assert response.status_code == 200
        assert 'substations' in response.context
        assert list(response.context['substations']) == [substation]
        
    def test_substation_list_filter_by_city(self, client, substation, inactive_substation):
        """Тест фильтрации по городу"""
        url = reverse('substations:substation_list')
        
        # Проверяем фильтр по Москве
        response = client.get(url, {'city': 'Москва'})
        assert response.status_code == 200
        assert list(response.context['substations']) == [substation]
        
        # Проверяем фильтр по Санкт-Петербургу
        response = client.get(url, {'city': 'Санкт-Петербург'})
        assert response.status_code == 200
        assert list(response.context['substations']) == [inactive_substation]
        
    def test_substation_list_filter_by_group(self, client, substation, substation_group):
        """Тест фильтрации по группе"""
        url = reverse('substations:substation_list')
        response = client.get(url, {'group': substation_group.id})
        assert response.status_code == 200
        assert list(response.context['substations']) == [substation]
        
    def test_substation_detail_view(self, client, substation):
        """Тест детального представления подстанции"""
        url = reverse('substations:substation_detail', args=[substation.id])
        response = client.get(url)
        assert response.status_code == 200
        assert response.context['substation'] == substation
        
    def test_substation_detail_404(self, client):
        """Тест несуществующей подстанции"""
        url = reverse('substations:substation_detail', args=[999])
        response = client.get(url)
        assert response.status_code == 404
        
    def test_substation_detail_maintenance_records(self, client, substation, maintenance_status):
        """Тест отображения записей об обслуживании"""
        # Создаем записи об обслуживании
        now = timezone.now()
        maintenance1 = MaintenanceRecord.objects.create(
            substation=substation,
            status=maintenance_status,
            scheduled_date=now + timedelta(days=1),
            description="Будущее обслуживание"
        )
        maintenance2 = MaintenanceRecord.objects.create(
            substation=substation,
            status=maintenance_status,
            scheduled_date=now - timedelta(days=1),
            completed_date=now,
            description="Прошедшее обслуживание"
        )
        
        url = reverse('substations:substation_detail', args=[substation.id])
        response = client.get(url)
        assert response.status_code == 200
        maintenance_records = response.context['maintenance_records']
        assert len(maintenance_records) == 2
        assert maintenance1 in maintenance_records
        assert maintenance2 in maintenance_records
