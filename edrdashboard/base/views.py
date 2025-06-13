from django.shortcuts import render

# Create your views here.
def login_page(request):
    return render(request, 'auth-login-basic.html')
def register_page(request):
    return render(request, 'auth-register-basic.html')
def forgot_password_page(request):
    return render(request, 'auth-forgot-password-basic.html')
def account_page(request):
    return render(request, 'pages-account-settings-account.html')
def dashboard_page(request):
    return render(request, 'index.html')
def statustracking_page(request):
    return render(request, 'statustracking.html')
def blank(request):
    return render(request, 'blank.html')
