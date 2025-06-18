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
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.db.models import Sum
from collections import defaultdict
# import sys



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
    production_yts_count = WorkUnit.objects.filter(rfdb_production_status='Yet to start').count()
    production_ip_count = WorkUnit.objects.filter(rfdb_production_status='inprogress').count()
    production_comp_count = WorkUnit.objects.filter(rfdb_production_status='Completed').count()
    production_hold_count = WorkUnit.objects.filter(rfdb_production_status='Hold').count()
    production_qcrejected_count = WorkUnit.objects.filter(rfdb_production_status='Qc Rejected').count()
    production_reworkcomp_count = WorkUnit.objects.filter(rfdb_production_status='Rework Comp').count()
    production_doubt_count = WorkUnit.objects.filter(rfdb_production_status='Doubt_Case').count()
    siloc_yts_count = WorkUnit.objects.filter(siloc_status='Yet to start').count()
    siloc_ip_count = WorkUnit.objects.filter(siloc_status='inprogress').count()
    siloc_comp_count = WorkUnit.objects.filter(siloc_status='Completed').count()
    siloc_hold_count = WorkUnit.objects.filter(siloc_status='Hold').count()
    siloc_qcrejected_count = WorkUnit.objects.filter(siloc_status='Qc Rejected').count()
    siloc_reworkcomp_count = WorkUnit.objects.filter(siloc_status='Rework Comp').count()
    siloc_doubt_count = WorkUnit.objects.filter(siloc_status='Doubt').count()
    qc_yts_count = WorkUnit.objects.filter(rfdb_qc_status='Yts').count()
    qc_ip_count = WorkUnit.objects.filter(rfdb_qc_status='inprogres').count()
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



def production_report(request):
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')

    records_by_day = []

    if from_date_str and to_date_str:
        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            # Ensure from_date is before to_date
            # print("From:", from_date_str, "| To:", to_date_str)

            if from_date > to_date:
                return JsonResponse({'error': 'From date must be before To date'}, status=400)
            # Initialize records_by_day with dates in the range
            current_date = from_date
            while current_date <= to_date:
                production_count = Production_inputs.objects.filter(
                    rfdb_production_status='Completed',
                    rfdb_completed_date=current_date
                ).count()

                qc_count = Production_inputs.objects.filter(
                    rfdb_qc_status='Completed',
                    rfdb_qc_completed_date=current_date
                ).count()
                
                siloc_count = Production_inputs.objects.filter(
                    siloc_status ='Completed',
                    siloc_completed_date =current_date
                ).count()
                
                input_received_count = Production_inputs.objects.filter(
                    wu_received_date=current_date
                ).count()



                # 🔍 Add this line for debugging
                # print(f"Date: {current_date} | Production: {production_count} | QC: {qc_count}", file=sys.stdout)
                # sys.stdout.flush()

                

                records_by_day.append({
                    'date': current_date,                    
                    'input_received_count': input_received_count,
                    'production_output': production_count,
                    'siloc_output': siloc_count,
                    'qc_output': qc_count,
                    'path_association_output': 0,
                    'delivery': 0
                })
                current_date += timedelta(days=1)
    
          
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    return render(request, 'tm_dmp.html', {
        'records': sorted(records_by_day, key=lambda x: x['date']),
        'from_date': from_date_str,
        'to_date': to_date_str,
    })





