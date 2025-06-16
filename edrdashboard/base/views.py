from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from .models import WorkUnit
import json
import openpyxl


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
    input_count = WorkUnit.objects.count()
    delivered_count = WorkUnit.objects.filter(delivery_status='Delivered').count()  # Assuming work_unit_id > 0 means delivered
    hold_count = WorkUnit.objects.filter(delivery_status='Hold').count()  # Assuming work_unit_id < 0 means on hold
    
    undelivered_count= input_count - (delivered_count + hold_count)  # Calculate undelivered count
    context = {
        'input_count': input_count,
        'delivered_count': delivered_count,
        'hold_count': hold_count,
        'undelivered_count': undelivered_count
    }  

    return render(request, 'statustracking.html', context)
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

def download_workunit_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'WorkUnits'

    # Header
    ws.append(['work_unit_id', 'delivery_status'])

    # Data
    for wu in WorkUnit.objects.all():
        ws.append([wu.work_unit_id, wu.delivery_status])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=workunits.xlsx'
    wb.save(response)
    return response

def download_workunit_excel_hold(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'WorkUnits'

    # Header
    ws.append(['work_unit_id', 'delivery_status'])

    # Data
    for wu in WorkUnit.objects.all():
        ws.append([wu.work_unit_id, wu.delivery_status])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=workunits.xlsx'
    wb.save(response)
    return response
