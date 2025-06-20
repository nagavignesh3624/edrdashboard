from django.db import models
from datetime import date
from collections import defaultdict

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
    rfdb_completed_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=50)
    rfdb_production_team_leader_emp_name = models.CharField(max_length=150, null=True, blank=True)
    rfdb_production_status= models.CharField(max_length=50, null=True, blank=True)

    # Add other fields as needed

    class Meta:
        db_table = 'tm_production_inputs'  # Change to your actual table name if different
        managed = False  # Prevent Django from creating or modifying this table

        
class Production_inputs(models.Model):
    rfdb_completed_date = models.DateField(primary_key=True, unique=True)
    wu_received_date = models.DateField(null=True, blank=True)
    rfdb_production_status = models.CharField(max_length=50)  # Example: "Completed"
    rfdb_qc_status = models.CharField(max_length=50)  # Example: "Completed"
    rfdb_qc_completed_date = models.DateField(null=True, blank=True)
    siloc_status = models.CharField(max_length=50)  # Example: "Completed"
    siloc_completed_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_status = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'tm_production_inputs'
        ordering = ['rfdb_completed_date']  # oldest to newest
        verbose_name = "Daily Production Input"
        verbose_name_plural = "Daily Production Inputs"

    def __str__(self):
        return f"{self.rfdb_completed_date} - {self.rfdb_production_status}"













