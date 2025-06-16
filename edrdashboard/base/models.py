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
    work_unit_id = models.BigIntegerField(primary_key=True)
    delivery_status = models.CharField(max_length=50)
    # Add other fields as needed

    class Meta:
        db_table = 'production_inputs'  # Change to your actual table name if different
        managed = False  # Prevent Django from creating or modifying this table
