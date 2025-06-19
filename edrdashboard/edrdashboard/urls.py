from django.contrib import admin
from django.urls import path
from base import views  # Import the views from the base app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_page, name='login'),  # This makes it the default page
    path('register/', views.register_page, name='register'),
    path('forgot-password/', views.forgot_password_page, name='forgot_password'),
    path('account/', views.account_page, name='account'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('statustracking/', views.statustracking_page, name='statustracking'),
    path('tm_dmp/', views.tm_dmp, name='tm_dmp'),
    path('download_workunit_excel/', views.download_workunit_excel, name='download_workunit_excel'),
    path('production-report/', views.production_report, name='production_report'),
   
    
    
]



