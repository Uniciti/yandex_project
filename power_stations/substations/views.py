# substations/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Case, When, Value, CharField, Q
from django.db.models.functions import Upper
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from .models import Substation, SubstationGroup, SubstationType, MaintenanceStatus, MaintenanceRecord
from .forms import SubstationForm, MaintenanceRecordForm, SubstationGroupForm, SubstationTypeForm, MaintenanceStatusForm
import os
import logging

logger = logging.getLogger(__name__)

def get_filtered_substations(request):
    substations = Substation.objects.select_related(
        'substation_type', 
        'group',
        'author'
    ).prefetch_related(
        'maintenance_records'
    )
    
    selected_city = request.GET.get('city')
    selected_group = request.GET.get('group')
    selected_type = request.GET.get('type')
    status = request.GET.get('status')
    search_query = request.GET.get('search')
    
    if not request.user.is_authenticated:
        substations = substations.filter(published_at__lte=timezone.now())
    
    if selected_city:
        substations = substations.filter(city__iexact=selected_city)
    
    if selected_group:
        substations = substations.filter(group_id=selected_group)
        
    if selected_type:
        substations = substations.filter(substation_type_id=selected_type)
        
    if status:
        if status == 'active':
            substations = substations.filter(is_active=True)
        elif status == 'inactive':
            substations = substations.filter(is_active=False)
        elif status == 'maintenance_needed':
            now = timezone.now()
            substations = substations.filter(
                Q(next_maintenance__lte=now) | Q(next_maintenance__isnull=True)
            )
            
    if search_query:
        substations = substations.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(city__icontains=search_query)
        )
    
    return substations

def substation_list(request):
    substations = get_filtered_substations(request)
    cities = (Substation.objects
             .annotate(city_upper=Upper('city'))
             .values_list('city_upper', 'city')
             .distinct()
             .order_by('city_upper'))
    
    cities = list({city[1] for city in cities})
    cities.sort()
    
    groups = SubstationGroup.objects.all()
    types = SubstationType.objects.all()
    
    sort_by = request.GET.get('sort', 'name')
    sort_order = request.GET.get('order', 'asc')
    
    if sort_by == 'name':
        sort_field = Upper('name')
    elif sort_by == 'city':
        sort_field = Upper('city')
    elif sort_by == 'power':
        sort_field = 'power'
    elif sort_by == 'voltage':
        sort_field = 'voltage'
    else:
        sort_field = 'name'
    
    if sort_order == 'desc':
        sort_field = f'-{sort_field}' if isinstance(sort_field, str) else sort_field.desc()
    
    substations = substations.order_by(sort_field)
    
    paginator = Paginator(substations, settings.SUBSTATIONS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'cities': cities,
        'groups': groups,
        'types': types,
        'selected_city': request.GET.get('city'),
        'selected_group': request.GET.get('group'),
        'selected_type': request.GET.get('type'),
        'status': request.GET.get('status'),
        'search_query': request.GET.get('search'),
        'sort_by': sort_by,
        'sort_order': sort_order,
    }
    return render(request, 'substations/substation_list.html', context)

@login_required
def substation_detail(request, substation_id):
    substation = get_object_or_404(Substation.objects.select_related(
        'substation_type',
        'group',
        'author'
    ).prefetch_related(
        'maintenance_records',
        'connected_substations'
    ), id=substation_id)

    if not substation.published_at <= timezone.now() and not (
        request.user.is_authenticated and (
            request.user == substation.author or 
            request.user.is_staff
        )
    ):
        return redirect('substations:substation_list')
    
    maintenance_records = substation.maintenance_records.select_related('status').order_by('-scheduled_date')
    
    now = timezone.now()
    maintenance_needed = (
        substation.next_maintenance is None or 
        substation.next_maintenance <= now
    )
    
    context = {
        'substation': substation,
        'maintenance_records': maintenance_records,
        'maintenance_needed': maintenance_needed,
        'is_owner': request.user == substation.author if request.user.is_authenticated else False,
    }
    return render(request, 'substations/substation_detail.html', context)

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(SubstationGroup, id=group_id)
    substations = group.substations.select_related(
        'substation_type',
        'author'
    ).all()
    
    paginator = Paginator(substations, settings.SUBSTATIONS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'substations/group_detail.html', context)

@login_required
def substation_create(request):
    if request.method == 'POST':
        form = SubstationForm(request.POST, request.FILES)
        if form.is_valid():
            substation = form.save(commit=False)
            substation.author = request.user
            substation.save()
            return redirect('substations:substation_detail', substation_id=substation.id)
    else:
        form = SubstationForm()
    
    context = {
        'form': form,
        'title': 'Создание новой подстанции',
        'is_edit': False,
    }
    return render(request, 'substations/substation_form.html', context)

@login_required
def substation_edit(request, substation_id):
   substation = get_object_or_404(Substation.objects.select_related(
       'substation_type', 
       'group'
   ).prefetch_related(
       'maintenance_records',
       'maintenance_records__status'
   ), id=substation_id)
   
   if request.user != substation.author and not request.user.is_staff:
       return redirect('substations:substation_detail', substation_id=substation_id)

   initial_data = {
       'last_maintenance': substation.last_maintenance.strftime('%Y-%m-%dT%H:%M') if substation.last_maintenance else None,
       'next_maintenance': substation.next_maintenance.strftime('%Y-%m-%dT%H:%M') if substation.next_maintenance else None,
   }
   form = SubstationForm(instance=substation, initial=initial_data)
   maintenance_form = MaintenanceRecordForm()
   group_form = SubstationGroupForm()
   type_form = SubstationTypeForm()
   status_form = MaintenanceStatusForm()

   if request.method == 'POST':
       form_type = request.POST.get('form_type')
       
       if form_type == 'substation':
           form = SubstationForm(request.POST, request.FILES, instance=substation)
           if form.is_valid():
               last_maintenance = form.cleaned_data.get('last_maintenance')
               next_maintenance = form.cleaned_data.get('next_maintenance')

               substation = form.save(commit=False)

               if last_maintenance:
                   substation.last_maintenance = last_maintenance
               if next_maintenance:
                   substation.next_maintenance = next_maintenance

               substation.save()
               form.save_m2m()

               if last_maintenance:
                   status, _ = MaintenanceStatus.objects.get_or_create(
                       name='Выполнено',
                       defaults={'description': 'Плановое обслуживание выполнено'}
                   )
                   MaintenanceRecord.objects.get_or_create(
                       substation=substation,
                       status=status,
                       scheduled_date=last_maintenance,
                       completed_date=last_maintenance,
                       defaults={
                           'description': 'Плановое техническое обслуживание',
                           'is_active': False
                       }
                   )

               if next_maintenance:
                   status, _ = MaintenanceStatus.objects.get_or_create(
                       name='Запланировано',
                       defaults={'description': 'Плановое обслуживание запланировано'}
                   )
                   MaintenanceRecord.objects.get_or_create(
                       substation=substation,
                       status=status,
                       scheduled_date=next_maintenance,
                       completed_date=None,
                       defaults={
                           'description': 'Плановое техническое обслуживание',
                           'is_active': True
                       }
                   )

               return redirect('substations:substation_detail', substation_id=substation_id)

       elif form_type == 'maintenance':
        maintenance_form = MaintenanceRecordForm(request.POST)
        if maintenance_form.is_valid():
            maintenance = maintenance_form.save(commit=False)
            maintenance.substation = substation
            maintenance.is_active = True if not maintenance.completed_date else False
            maintenance.save()

            # Обновляем даты обслуживания подстанции
            if maintenance.completed_date:
                if not substation.last_maintenance or maintenance.completed_date > substation.last_maintenance:
                    substation.last_maintenance = maintenance.completed_date
            if maintenance.scheduled_date and not maintenance.completed_date:
                if not substation.next_maintenance or maintenance.scheduled_date < substation.next_maintenance:
                    substation.next_maintenance = maintenance.scheduled_date
            substation.save()
            
            return redirect('substations:substation_detail', substation_id=substation_id)
       
       elif form_type == 'group':
           group_form = SubstationGroupForm(request.POST)
           if group_form.is_valid():
               group = group_form.save()
               substation.group = group
               substation.save()
               return redirect('substations:substation_detail', substation_id=substation_id)
       
       elif form_type == 'type':
           type_form = SubstationTypeForm(request.POST)
           if type_form.is_valid():
               substation_type = type_form.save()
               substation.substation_type = substation_type
               substation.save()
               return redirect('substations:substation_detail', substation_id=substation_id)

       elif form_type == 'status':
           status_form = MaintenanceStatusForm(request.POST)
           if status_form.is_valid():
               status_form.save()
               return redirect('substations:substation_edit', substation_id=substation_id)

   context = {
       'form': form,
       'maintenance_form': maintenance_form,
       'group_form': group_form,
       'type_form': type_form,
       'status_form': status_form,
       'title': f'Редактирование подстанции: {substation.name}',
       'is_edit': True,
       'substation': substation,
       'maintenance_records': substation.maintenance_records.select_related('status').order_by('-scheduled_date'),
       'maintenance_needed': substation.next_maintenance is None or substation.next_maintenance <= timezone.now(),
       'maintenance_statuses': MaintenanceStatus.objects.all(),
       'groups': SubstationGroup.objects.all(),
       'types': SubstationType.objects.all(),
   }

   return render(request, 'substations/substation_form.html', context)

@login_required
def maintenance_record_detail(request, record_id):
    record = get_object_or_404(MaintenanceRecord.objects.select_related(
        'substation',
        'status'
    ), id=record_id)
    
    if request.user != record.substation.author and not request.user.is_staff:
        return redirect('substations:substation_detail', substation_id=record.substation.id)
    
    context = {
        'record': record,
        'substation': record.substation,
    }
    return render(request, 'substations/maintenance_record_detail.html', context)

@login_required
def maintenance_status_detail(request, status_id):
    status = get_object_or_404(MaintenanceStatus, id=status_id)
    records = MaintenanceRecord.objects.filter(status=status).select_related('substation')
    
    context = {
        'status': status,
        'records': records,
    }
    return render(request, 'substations/maintenance_status_detail.html', context)

@login_required
def substation_type_detail(request, type_id):
    substation_type = get_object_or_404(SubstationType, id=type_id)
    substations = Substation.objects.filter(substation_type=substation_type).select_related(
        'group',
        'substation_type'
    ).order_by('name')
    
    context = {
        'substation_type': substation_type,
        'substations': substations,
    }
    return render(request, 'substations/substation_type_detail.html', context)

@login_required
def maintenance_status_detail(request, status_id):
    status = get_object_or_404(MaintenanceStatus, id=status_id)
    maintenance_records = MaintenanceRecord.objects.filter(
        status=status
    ).select_related(
        'substation'
    ).order_by('-scheduled_date')
    
    maintenance_records_completed = maintenance_records.filter(completed_date__isnull=False)
    maintenance_records_in_progress = maintenance_records.filter(completed_date__isnull=True)
    
    context = {
        'status': status,
        'maintenance_records': maintenance_records,
        'maintenance_records_completed': maintenance_records_completed,
        'maintenance_records_in_progress': maintenance_records_in_progress,
    }
    return render(request, 'substations/maintenance_status_detail.html', context)

@login_required
def substation_delete(request, substation_id):
    substation = get_object_or_404(Substation.objects.select_related(
        'substation_type',
        'group',
        'author'
    ), id=substation_id)

    if request.user != substation.author and not request.user.is_staff:
        return redirect('substations:substation_detail', substation_id=substation_id)
    
    if request.method == 'POST':
        # Сохраняем информацию перед удалением
        substation_info = {
            'name': substation.name,
            'type': str(substation.substation_type) if substation.substation_type else 'Не указан',
            'group': str(substation.group) if substation.group else 'Не указана',
            'maintenance_count': substation.maintenance_records.count()
        }
        
        substation.delete()
        
        try:
            if not os.path.exists(settings.EMAIL_FILE_PATH):
                os.makedirs(settings.EMAIL_FILE_PATH)
                
            send_mail(
                f"{settings.EMAIL_SUBJECT_PREFIX}Удалена подстанция: {substation_info['name']}",
                f"""Была удалена подстанция:
                Название: {substation_info['name']}
                Тип: {substation_info['type']}
                Группа: {substation_info['group']}
                Количество записей обслуживания: {substation_info['maintenance_count']}
                
                Удалено пользователем: {request.user}
                """,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False
            )
            logger.info(f"Email об удалении подстанции {substation_info['name']} успешно отправлен")
        except Exception as e:
            logger.error(f"Ошибка при отправке email об удалении подстанции: {str(e)}")
        
        return redirect('substations:substation_list')
    
    context = {
        'substation': substation,
        'title': f'Удаление подстанции: {substation.name}',
        'maintenance_records_count': substation.maintenance_records.count(),
    }
    return render(request, 'substations/substation_confirm_delete.html', context)

@login_required
def substation_type_delete(request, type_id):
    substation_type = get_object_or_404(SubstationType, id=type_id)
    
    if not request.user.is_staff:
        return redirect('substations:substation_type_detail', type_id=type_id)
    
    substations_count = Substation.objects.filter(substation_type=substation_type).count()
    
    if request.method == 'POST':
        type_info = {
            'name': substation_type.name,
            'description': substation_type.description,
            'substations_count': substations_count
        }
        
        substation_type.delete()
        
        try:
            if not os.path.exists(settings.EMAIL_FILE_PATH):
                os.makedirs(settings.EMAIL_FILE_PATH)
                
            send_mail(
                f"{settings.EMAIL_SUBJECT_PREFIX}Удален тип подстанции: {type_info['name']}",
                f"""Был удален тип подстанции:
                Название: {type_info['name']}
                Описание: {type_info['description']}
                Количество связанных подстанций: {type_info['substations_count']}
                
                Удалено пользователем: {request.user}
                """,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False
            )
            logger.info(f"Email об удалении типа подстанции {type_info['name']} успешно отправлен")
        except Exception as e:
            logger.error(f"Ошибка при отправке email об удалении типа подстанции: {str(e)}")
        
        return redirect('substations:substation_list')
    
    context = {
        'substation_type': substation_type,
        'substations_count': substations_count,
        'title': f'Удаление типа подстанции: {substation_type.name}',
    }
    return render(request, 'substations/substation_type_confirm_delete.html', context)

@login_required
def substation_group_delete(request, group_id):
    group = get_object_or_404(SubstationGroup.objects.prefetch_related(
        'substations'
    ), id=group_id)
    
    if not request.user.is_staff:
        return redirect('substations:group_detail', group_id=group_id)
    
    substations_count = group.substations.count()
    
    if request.method == 'POST':
        group_info = {
            'name': group.name,
            'description': group.description,
            'responsible_person': group.responsible_person,
            'substations_count': substations_count
        }
        
        group.delete()
        
        try:
            if not os.path.exists(settings.EMAIL_FILE_PATH):
                os.makedirs(settings.EMAIL_FILE_PATH)
                
            send_mail(
                f"{settings.EMAIL_SUBJECT_PREFIX}Удалена группа подстанций: {group_info['name']}",
                f"""Была удалена группа подстанций:
                Название: {group_info['name']}
                Описание: {group_info['description']}
                Ответственное лицо: {group_info['responsible_person']}
                Количество подстанций в группе: {group_info['substations_count']}
                
                Удалено пользователем: {request.user}
                """,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False
            )
            logger.info(f"Email об удалении группы подстанций {group_info['name']} успешно отправлен")
        except Exception as e:
            logger.error(f"Ошибка при отправке email об удалении группы подстанций: {str(e)}")
        
        return redirect('substations:substation_list')
    
    context = {
        'group': group,
        'substations_count': substations_count,
        'title': f'Удаление группы подстанций: {group.name}',
    }
    return render(request, 'substations/substation_group_confirm_delete.html', context)

@login_required
def maintenance_record_delete(request, record_id):
    record = get_object_or_404(MaintenanceRecord.objects.select_related(
        'substation',
        'status',
        'substation__author'
    ), id=record_id)
    
    if request.user != record.substation.author and not request.user.is_staff:
        return redirect('substations:maintenance_record_detail', record_id=record_id)
    
    substation = record.substation
    
    if request.method == 'POST':
        record_info = {
            'substation_name': substation.name,
            'status': str(record.status),
            'scheduled_date': record.scheduled_date.strftime('%Y-%m-%d %H:%M:%S'),
            'completed_date': record.completed_date.strftime('%Y-%m-%d %H:%M:%S') if record.completed_date else 'Не выполнено',
            'description': record.description
        }
        
        record.delete()
        
        # Обновляем даты обслуживания
        last_completed = MaintenanceRecord.objects.filter(
            substation=substation,
            completed_date__isnull=False
        ).order_by('-completed_date').first()
        
        next_scheduled = MaintenanceRecord.objects.filter(
            substation=substation,
            completed_date__isnull=True,
            scheduled_date__gt=timezone.now()
        ).order_by('scheduled_date').first()
        
        substation.last_maintenance = last_completed.completed_date if last_completed else None
        substation.next_maintenance = next_scheduled.scheduled_date if next_scheduled else None
        substation.save()

        try:
            if not os.path.exists(settings.EMAIL_FILE_PATH):
                os.makedirs(settings.EMAIL_FILE_PATH)
                
            send_mail(
                f"{settings.EMAIL_SUBJECT_PREFIX}Удалена запись об обслуживании подстанции: {record_info['substation_name']}",
                f"""Была удалена запись об обслуживании:
                Подстанция: {record_info['substation_name']}
                Статус: {record_info['status']}
                Запланированная дата: {record_info['scheduled_date']}
                Дата выполнения: {record_info['completed_date']}
                Описание: {record_info['description']}
                
                Удалено пользователем: {request.user}
                """,
                settings.DEFAULT_FROM_EMAIL,
                [substation.author.email],
                fail_silently=False
            )
            logger.info(f"Email об удалении записи обслуживания для {record_info['substation_name']} успешно отправлен")
        except Exception as e:
            logger.error(f"Ошибка при отправке email об удалении записи обслуживания: {str(e)}")
        
        return redirect('substations:substation_detail', substation_id=substation.id)
    
    context = {
        'record': record,
        'title': f'Удаление записи об обслуживании: {substation.name}',
    }
    return render(request, 'substations/maintenance_record_confirm_delete.html', context)