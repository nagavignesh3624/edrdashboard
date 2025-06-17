from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from .models import WorkUnit
import json
import openpyxl
from django.db.models import Count
from django.shortcuts import render
from .models import Production_inputs
from datetime import datetime
from .models import DailyCompletionStatus
from django.db.models import Count, Q


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
def get_workunit_context():
    input_count = WorkUnit.objects.count()
    delivered_count = WorkUnit.objects.filter(delivery_status='Delivered').count()
    hold_count = WorkUnit.objects.filter(delivery_status='Hold').count()
    production_yts_count = WorkUnit.objects.filter(rfdb_production_status='Yts').count()
    production_ip_count = WorkUnit.objects.filter(rfdb_production_status='ip').count()
    production_comp_count = WorkUnit.objects.filter(rfdb_production_status='Completed').count()
    production_hold_count = WorkUnit.objects.filter(rfdb_production_status='Hold').count()
    production_qcrejected_count = WorkUnit.objects.filter(rfdb_production_status='Qc Rejected').count()
    production_reworkcomp_count = WorkUnit.objects.filter(rfdb_production_status='Rework Comp').count()
    production_doubt_count = WorkUnit.objects.filter(rfdb_production_status='Doubt').count()
    siloc_yts_count = WorkUnit.objects.filter(siloc_status='Yts').count()
    siloc_ip_count = WorkUnit.objects.filter(siloc_status='ip').count()
    siloc_comp_count = WorkUnit.objects.filter(siloc_status='Completed').count()
    siloc_hold_count = WorkUnit.objects.filter(siloc_status='Hold').count()
    siloc_qcrejected_count = WorkUnit.objects.filter(siloc_status='Qc Rejected').count()
    siloc_reworkcomp_count = WorkUnit.objects.filter(siloc_status='Rework Comp').count()
    siloc_doubt_count = WorkUnit.objects.filter(siloc_status='Doubt').count()
    qc_yts_count = WorkUnit.objects.filter(rfdb_qc_status='Yts').count()
    qc_ip_count = WorkUnit.objects.filter(rfdb_qc_status='ip').count()
    qc_comp_count = WorkUnit.objects.filter(rfdb_qc_status='Completed').count()
    qc_hold_count = WorkUnit.objects.filter(rfdb_qc_status='Hold').count()
    qc_qcrejected_count = WorkUnit.objects.filter(rfdb_qc_status='Qc Rejected').count()
    qc_reworkcomp_count = WorkUnit.objects.filter(rfdb_qc_status='Rework Comp').count()
    qc_doubt_count = WorkUnit.objects.filter(rfdb_qc_status='Doubt').count()

    undelivered_count = input_count - (delivered_count + hold_count)

    return {
        'input_count': input_count,
        'delivered_count': delivered_count,
        'hold_count': hold_count,
        'undelivered_count': undelivered_count,
        'production_yts_count': production_yts_count,
        'production_ip_count': production_ip_count, 
        'production_comp_count': production_comp_count,
        'production_hold_count': production_hold_count,
        'production_qcrejected_count': production_qcrejected_count,
        'production_reworkcomp_count': production_reworkcomp_count,
        'production_doubt_count': production_doubt_count,
        'siloc_yts_count': siloc_yts_count,
        'siloc_ip_count': siloc_ip_count, 
        'siloc_comp_count': siloc_comp_count,
        'siloc_hold_count': siloc_hold_count,
        'siloc_qcrejected_count': siloc_qcrejected_count,
        'siloc_reworkcomp_count': siloc_reworkcomp_count,
        'siloc_doubt_count': siloc_doubt_count,
        'qc_yts_count': qc_yts_count,
        'qc_ip_count': qc_ip_count, 
        'qc_comp_count': qc_comp_count,
        'qc_hold_count': qc_hold_count,
        'qc_qcrejected_count': qc_qcrejected_count,
        'qc_reworkcomp_count': qc_reworkcomp_count,
        'qc_doubt_count': qc_doubt_count
    }

# your two views can now reuse that data
def statustracking_page(request):
    context = get_workunit_context()
    return render(request, 'statustracking.html', context)

def tm_dmp(request):
    context = get_workunit_context()
    return render(request, 'tm_dmp.html', context)

def production_status_by_date(request):
    comp_records = (
        get_workunit_context.objects
        .filter(rfdb_production_status='comp')
        .values('rfdb_production_completion_date')
        .annotate(comp_count=Count('id'))
        .order_by('rfdb_production_completion_date')
    )

    context = {
        'records': comp_records
    }

    return render(request, 'your_template.html', context)




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
    ws.append(['wu_intersection_node_id', 'delivery_status'])

    # Data
    for wu in WorkUnit.objects.all():
        ws.append([wu.wu_intersection_node_id, wu.delivery_status])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=workunits.xlsx'
    wb.save(response)
    return response

def download_workunit_excel_hold(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'WorkUnits'

    # Header
    ws.append(['wu_intersection_node_id', 'delivery_status'])

    # Data
    for wu in WorkUnit.objects.all():
        ws.append([wu.wu_intersection_node_id, wu.delivery_status])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=workunits.xlsx'
    wb.save(response)
    return response


def production_report(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    records = Production_inputs.objects.all().order_by('production_completion_date')

    if from_date and to_date:
        records = records.filter(
            production_completion_date__range=[from_date, to_date]
        )

    # Manipulate data based on condition
    for record in records:
        if record.qc_output < 5:
            record.production_output += 10  # example adjustment

    return render(request, 'report_table.html', {
        'records': records,
        'from_date': from_date,
        'to_date': to_date,
    })


def daily_status_view(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    records = DailyCompletionStatus.objects.all()

    if from_date and to_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            # records = records.filter(date__range=(from_date_obj, to_date_obj))
        except ValueError:
            pass  # Invalid date input; ignore filtering

    context = {
        'records': records.order_by('-date'),
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, 'tm_dmp.html', context)


