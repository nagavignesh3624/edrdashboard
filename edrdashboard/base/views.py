from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from .models import WorkUnit
import json


# Create your views here.
# def login_page(request):
#     return render(request, 'auth-login-basic.html')
def register_page(request):
    return render(request, 'auth-register-basic.html')
def forgot_password_page(request):
    return render(request, 'auth-forgot-password-basic.html')
def account_page(request):
    return render(request, 'pages-account-settings-account.html')
def dashboard_page(request):
    return render(request, 'index.html')
def statustracking_page(request):
    yts_count = WorkUnit.objects.count()
    return render(request, 'statustracking.html', {'yts_count': yts_count})
def tm_dmp(request):
    return render(request, 'tm_dmp.html')




@csrf_exempt  # For development only! Use CSRF token in production.
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"LOGIN DEBUG: username={username}, password={password}")  # Debug print
        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                login(request, user)
                return JsonResponse({'status': 'success', 'message': 'Login successful'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=400)
    return render(request, 'auth-login-basic.html')
