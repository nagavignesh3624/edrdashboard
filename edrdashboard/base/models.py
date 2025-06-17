from django.db import models
from datetime import date
from django.db import models

class Employee(models.Model):
    # Update these fields to match your actual table columns
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    # Add other fields as needed

    class Meta:
        db_table = 'employee'
        managed = False  # Prevent Django from creating or modifying this table

class WorkUnit(models.Model):
    wu_intersection_node_id = models.BigIntegerField(primary_key=True)
    delivery_status = models.CharField(max_length=50)
    rfdb_production_status = models.CharField(max_length=50, null=True, blank=True)
    rfdb_qc_status = models.CharField(max_length=50, null=True, blank=True)
    siloc_status = models.CharField(max_length=50, null=True, blank=True)
    rfdb_completion_date = models.DateField(null=True, blank=True)

    # Add other fields as needed

    class Meta:
        db_table = 'tm_production_inputs'  # Change to your actual table name if different
        managed = False  # Prevent Django from creating or modifying this table

        
class Production_inputs(models.Model):
    production_completion_date = models.DateField()
    atdb_output = models.IntegerField(default=0)
    production_output = models.IntegerField(default=0)
    siloc_output = models.IntegerField(default=0)
    qc_output = models.IntegerField(default=0)
    path_association_output = models.IntegerField(default=0)
    delivery = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.production_completion_date}"
    

    
# class DailyCompletionStatus(models.Model):
#     start_date = models.DateField(default=date(2022, 1, 1))  # Replace with your fixed start
#     end_date = models.DateField(default=date.today)

#     production_completion_date = models.DateField()
#     atdb_output = models.IntegerField(default=0)
#     production_output = models.IntegerField(default=0)
#     siloc_output = models.IntegerField(default=0)
#     qc_output = models.IntegerField(default=0)
#     path_association_output = models.IntegerField(default=0)
#     delivery = models.IntegerField(default=0)
#     rfdb_production_status = models.CharField(max_length=50, null=True, blank=True)  # Include if needed for filtering

#     class Meta:
#         db_table = 'tm_production_inputs'  # Change to your actual table name if different
#         managed = False  # Prevent Django from creating or modifying this table
    

