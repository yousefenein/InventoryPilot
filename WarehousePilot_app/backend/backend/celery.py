from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings

import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')
app.conf.enable_utc = False

#app.config_from_object('django.conf:settings', namespace='CELERY')
app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks()


logger = logging.getLogger(__name__)

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
    
@app.task(bind=True)
def task_test(self):
    logger.info('testing out celery beat tasks')
 
@app.task(bind=True)
def one_off_manu_task_generate(self):
    from django.db.models import Q
    from django.db.models import Sum
    from orders.models import Orders
    from manufacturingLists.models import ManufacturingLists, ManufacturingListItem, ManufacturingTask
    from parts.models import Part
    from datetime import date
    from dateutil import relativedelta
    logger.info('inside one_off_manu_task_generate')
    today = date.today()
    logger.info(f'today\'s date: '+str(today))
    
    #retrieve the orders that are overdue or have a null due date
    overdueOrders = list(Orders.objects.filter(Q(due_date__lte=today) | Q(due_date=None)).values_list('order_id', flat=True))
    
    #retrieve the manufacturing lists associated with any overdue or null due date orders
    overdueManuLists = list(ManufacturingLists.objects.filter(order_id__in=overdueOrders))
    
    #retrieve the manufacturing lists associated with any overdue or null due date orders
    overdueManuListItems = ManufacturingListItem.objects.filter(manufacturing_list_id__in = overdueManuLists)
    
    skuColorsUnique = list(set(overdueManuListItems.values_list('sku_color', flat=True)))
    manuTasks = []
    for s in skuColorsUnique:
        totalQty = overdueManuListItems.filter(sku_color=Part.objects.get(sku_color=s)).aggregate(totalQTY = Sum('amount'))['totalQTY']
        manuTasks.append(ManufacturingTask(sku_color = Part.objects.get(sku_color=s), qty = totalQty, due_date = (today + relativedelta.relativedelta(month=1)), status = 'cutting'))
        
    ManufacturingTask.objects.bulk_create(manuTasks)

    