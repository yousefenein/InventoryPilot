from django.db import models
from parts.models import Part
from orders.models import Orders
from auth_app.models import users
# Create your models here.

class ManufacturingLists(models.Model):
    manufacturing_list_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)

class ManufacturingTask(models.Model):
    MANUFACTURING_PROCESSES={
        "cutting" : "cutting",
        "bending" : "bending",
        "painting" :  "painting",
        "completed" : "completed",
        "cutting QA": "cuttingQA",
        "bending QA" : "bendingQA",
        "painting QA" :  "paintingQA"
    }
    manufacturing_task_id = models.AutoField(primary_key=True)
    sku_color = models.ForeignKey(Part, on_delete=models.CASCADE)
    qty = models.IntegerField()
    due_date = models.DateField()
    status = models.CharField(max_length=25, choices=MANUFACTURING_PROCESSES)
    
    cut_start_time = models.DateField(null=True)
    cut_end_time = models.DateField(null=True)
    bend_start_time = models.DateField(null=True)
    bend_end_time = models.DateField(null=True)
    paint_start_time = models.DateField(null=True)
    paint_end_time = models.DateField(null=True)
    
    cut_qa = models.BooleanField(default=False)
    bend_qa = models.BooleanField(default=False)
    paint_qa = models.BooleanField(default=False)
    
    cut_employee = models.ForeignKey(users, null=True, on_delete=models.SET_NULL, related_name="cut_employee", related_query_name="cut_employee")
    cut_qa_employee = models.ForeignKey(users, null=True, on_delete=models.SET_NULL, related_name="cut_qa_employee", related_query_name="cut_qa_employee")
    bend_employee = models.ForeignKey(users, null=True, on_delete=models.SET_NULL, related_name="bend_employee", related_query_name="bend_employee")
    bend_qa_employee = models.ForeignKey(users, null=True, on_delete=models.SET_NULL, related_name="bend_qa_employee", related_query_name="bend_qa_employee")
    paint_employee = models.ForeignKey(users, null=True, on_delete=models.SET_NULL, related_name="paint_employee", related_query_name="paint_employee")
    paint_qa_employee = models.ForeignKey(users, null=True, on_delete=models.SET_NULL, related_name="paint_qa_employee", related_query_name="paint_qa_employee")
    
class ManufacturingListItem(models.Model):
    MANUFACTURING_PROCESSES={
        "cutting" : "cutting",
        "bending" : "bending",
        "painting" :  "painting",
        "completed" : "completed",
        "cutting QA": "cuttingQA",
        "bending QA" : "bendingQA",
        "painting QA" :  "paintingQA"
    }
    PROGRESS_STAGES={
        "ToDo" : "To Do",
        "In Progress" : "In Progress",
        "Completed" : "Completed"
    }
    manufacturing_list_item_id = models.AutoField(primary_key=True)
    manufacturing_list_id = models.ForeignKey(ManufacturingLists, on_delete=models.CASCADE)
    sku_color = models.ForeignKey(Part, on_delete=models.CASCADE)
    amount = models.IntegerField()
    manufacturing_process=models.CharField(null=True, max_length=25, choices=MANUFACTURING_PROCESSES)
    process_progress = models.CharField(null=True, max_length=25, choices=PROGRESS_STAGES)
    manufacturing_task = models.ForeignKey(ManufacturingTask, null=True, on_delete=models.SET_NULL)


    