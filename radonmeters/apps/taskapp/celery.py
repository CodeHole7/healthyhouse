# -*- coding: utf-8 -*-
import os
import datetime

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery('radonmeters')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, force=True)
app.conf.timezone = 'UTC'

app.conf.beat_schedule = {
    'remind-shipment-pickup': {
        'task': 'deliveries.tasks.delivery_remind_pickup',
        'schedule': crontab(minute=0, hour=11),
    },
    'update-shipment-status': {
        'task': 'deliveries.tasks.update_shipment_statuses',
        'schedule': crontab(minute=30, hour='*/8'),
    },
}
