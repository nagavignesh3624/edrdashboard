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
def qc_summary(request):  
  
    return render(request, 'qc_summary.html')


def get_workunit_context():
    # Optimize by aggregating counts in fewer queries
    input_count = WorkUnit.objects.count()
    delivered_count = WorkUnit.objects.filter(delivery_status='Delivered').count()
    hold_count = WorkUnit.objects.filter(delivery_status='Hold').count()
    undelivered_count = input_count - (delivered_count + hold_count)

    # Use values and annotate for each status field, fix PK field
    prod_status_counts = dict(WorkUnit.objects.values_list('rfdb_production_status').annotate(c=Count('wu_intersection_node_id')))
    siloc_status_counts = dict(WorkUnit.objects.values_list('siloc_status').annotate(c=Count('wu_intersection_node_id')))
    qc_status_counts = dict(WorkUnit.objects.values_list('rfdb_qc_status').annotate(c=Count('wu_intersection_node_id')))

    def get_count(d, key):
        return d.get(key, 0)

    return {
        'input_count': input_count,
        'delivered_count': delivered_count,
        'hold_count': hold_count,
        'undelivered_count': undelivered_count,
        'production_yts_count': get_count(prod_status_counts, 'Yet to start'),
        'production_ip_count': get_count(prod_status_counts, 'Inprogress'),
        'production_comp_count': get_count(prod_status_counts, 'Completed'),
        'production_hold_count': get_count(prod_status_counts, 'Hold'),
        'production_qcrejected_count': get_count(prod_status_counts, 'QC_Rejected'),
        'production_reworkcomp_count': get_count(prod_status_counts, 'Rework_Completed'),
        'production_doubt_count': get_count(prod_status_counts, 'Doubt_Case'),
        'siloc_yts_count': get_count(siloc_status_counts, 'Yet to start'),
        'siloc_ip_count': get_count(siloc_status_counts, 'Inprogress'),
        'siloc_comp_count': get_count(siloc_status_counts, 'Completed'),
        'siloc_hold_count': get_count(siloc_status_counts, 'Hold'),
        'siloc_qcrejected_count': get_count(siloc_status_counts, 'QC_Rejected'),
        'siloc_reworkcomp_count': get_count(siloc_status_counts, 'Rework_Completed'),
        'siloc_doubt_count': get_count(siloc_status_counts, 'Doubt_Case'),
        'qc_yts_count': get_count(qc_status_counts, 'Yet to start'),
        'qc_ip_count': get_count(qc_status_counts, 'Inprogress'),
        'qc_comp_count': get_count(qc_status_counts, 'Completed'),
        'qc_hold_count': get_count(qc_status_counts, 'Hold'),
        'qc_qcrejected_count': get_count(qc_status_counts, 'QC_Rejected'),
        'qc_reworkcomp_count': get_count(qc_status_counts, 'Rework_Completed'),
        'qc_doubt_count': get_count(qc_status_counts, 'Doubt_Case'),
    }

# your two views can now reuse that data
def statustracking_page(request):
    context = get_workunit_context()
    priority = WorkUnit.objects.values_list('priority', flat=True).distinct().order_by('priority')

    context['priority'] = priority
  
    return render(request, 'statustracking.html', context)

def tm_dmp(request):
    context = get_workunit_context()
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    records_by_day = []
    if from_date_str and to_date_str:
        try:
            from datetime import datetime, timedelta
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            if from_date > to_date:
                context['records'] = []
                context['from_date'] = from_date_str
                context['to_date'] = to_date_str
                return render(request, 'tm_dmp.html', context)
            # Optimize: fetch all relevant Production_inputs in one query
            qs = Production_inputs.objects.filter(
                Q(wu_received_date__range=(from_date, to_date)) |
                Q(rfdb_completed_date__range=(from_date, to_date)) |
                Q(rfdb_qc_completed_date__range=(from_date, to_date)) |
                Q(siloc_completed_date__range=(from_date, to_date)) |
                Q(delivery_date__range=(from_date, to_date))
            )
            # Build a dict of days
            day_map = {}
            current_date = from_date
            while current_date <= to_date:
                day_map[current_date] = {
                    'date': current_date,
                    'input_received_count': 0,
                    'production_output': 0,
                    'siloc_output': 0,
                    'qc_output': 0,
                    'path_association_output': 0,
                    'delivery_count': 0
                }
                current_date += timedelta(days=1)
            for obj in qs:
                if obj.wu_received_date and from_date <= obj.wu_received_date <= to_date:
                    day_map[obj.wu_received_date]['input_received_count'] += 1
                if obj.rfdb_completed_date and from_date <= obj.rfdb_completed_date <= to_date and obj.rfdb_production_status == 'Completed':
                    day_map[obj.rfdb_completed_date]['production_output'] += 1
                if obj.siloc_completed_date and from_date <= obj.siloc_completed_date <= to_date and obj.siloc_status == 'Completed':
                    day_map[obj.siloc_completed_date]['siloc_output'] += 1
                if obj.rfdb_qc_completed_date and from_date <= obj.rfdb_qc_completed_date <= to_date and obj.rfdb_qc_status == 'Completed':
                    day_map[obj.rfdb_qc_completed_date]['qc_output'] += 1
                if obj.delivery_date and from_date <= obj.delivery_date <= to_date and obj.delivery_status == 'Delivered':
                    day_map[obj.delivery_date]['delivery_count'] += 1
            context['records'] = [day_map[d] for d in sorted(day_map)]
            context['from_date'] = from_date_str
            context['to_date'] = to_date_str
        except ValueError:
            context['records'] = []
            context['from_date'] = from_date_str
            context['to_date'] = to_date_str
            return render(request, 'tm_dmp.html', context)
    else:
        context['records'] = []
        context['from_date'] = ''
        context['to_date'] = ''
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



def statustracking(request):
    # ...existing code...
    production_inputs = WorkUnit.objects.all()
    tl_stats = {}
    print(production_tl_status)

    for inp in production_inputs:
        name = (inp.rfdb_production_team_leader_emp_name or '').strip()
        status = (inp.rfdb_production_status or '').strip().lower()
        if not name:
            continue
        if name not in tl_stats:
            tl_stats[name] = {
                'Yet to start': 0, 'Inprogress': 0, 'Completed': 0, 'Hold': 0, 'QC_Rejected': 0, 'Rework_Completed': 0, 'Doubt_Case': 0
            }
        if status == 'yet to start':
            tl_stats[name]['Yet to start'] += 1
        elif status == 'inprogress':
            tl_stats[name]['Inprogress'] += 1
        elif status == 'completed':
            tl_stats[name]['Completed'] += 1
        elif status == 'hold':
            tl_stats[name]['Hold'] += 1
        elif status == 'qc_rejected':
            tl_stats[name]['QC_Rejected'] += 1
        elif status == 'rework_completed':
            tl_stats[name]['Rework_Completed'] += 1
        elif status in ('doubt_case', 'doubt_case'):
            tl_stats[name]['Doubt_Case'] += 1

    production_tl_status = [
        {'name': name, **stats} for name, stats in tl_stats.items()
    ]
    print(production_tl_status)
    context = {
        # ...existing context...
        'production_tl_status': production_tl_status,
    }
    return render(request, 'statustracking.html', context)





