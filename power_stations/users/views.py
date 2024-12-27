# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import CreationForm, ProfileEditForm
from substations.models import Substation
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        form = CreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('substations:substation_list')
    else:
        form = CreationForm()
    return render(request, 'users/signup.html', {'form': form})

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    substations = Substation.objects.filter(
        author=profile_user
    ).select_related(
        'substation_type',
        'group'
    ).order_by('-created_at')
    
    context = {
        'profile_user': profile_user,
        'substations': substations,
        'is_owner': request.user == profile_user,
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Ваш пароль был успешно изменен!')
            return render(request, 'users/password_change_done.html')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'users/password_change.html', {'form': form})