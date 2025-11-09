# from celery_demo.celery import app
# from celery.schedules import crontab, solar
# from datetime import timedelta
# from celery_demo.tasks import add, sub


# # ===================== USE SECOND METHOD TO CONFIG CELERY BEAT SCHEDULE =================
# # Method-2
# # Normal schedule
# app.conf.beat_schedule = {
#     "every-10-seconds": {
#         "task": "celery_demo.tasks.add",
#         "schedule": 10,  # every 10 seconds
#         "args": (
#             10,
#             20,
#         ),
#     }
# }

# # # Timedelta schedule
# # app.conf.beat_schedule = {
# #     'every-10-minute': {
# #         'task': 'celery_demo.tasks.add',
# #         'schedule': timedelta(seconds=10), # every 10 seconds
# #         'args': ("addition successfully", ),
# #     }
# # }

# # # Crontab schedule
# # app.conf.beat_schedule = {
# #     # Executes every Monday morning at 7:30 a.m.
# #     'add-every-monday-morning': {
# #         'task': 'celery_demo.tasks.add',
# #         'schedule': crontab(hour=7, minute=30, day_of_week=1),
# #         'args': ("addition successfully", ),
# #     }
# # }

# # # Solor schedule
# # app.conf.beat_schedule = {
# #     # Executes at sunset in Dhaka
# #     'add-at-dhaka-sunset': {
# #         'task': 'celery_demo.tasks.add',
# #         'schedule': solar('sunset', -37.81753, 144.96715),
# #         'args': ("addition successfully", ),
# #     }
# # }
