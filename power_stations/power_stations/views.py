# power_stations/views.py
from django.shortcuts import render

def page_not_found(request, exception):
    return render(request, 'errors/404.html', status=404)

def server_error(request):
    return render(request, 'errors/500.html', status=500)

def csrf_failure(request, reason=''):
    return render(request, 'errors/403csrf.html', status=403)