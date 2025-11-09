from celery import Celery
from celery import shared_task
from .celery import app
from celery_app.models import Restaurant, SellerProfile, TemporaryRole
from time import sleep
from django_celery_results.models import TaskResult
from django.utils import timezone
from datetime import timedelta

# app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task(name="Addition task")
def add(x, y):
    return x + y


@app.task(name="Subtruction task")
def sub(x, y):
    return x - y


@shared_task
def clear_session_cache(id):
    print(f"clear session cache: {id}")
    return id

@shared_task
def clear_old_task_result_every_5_minute(text):
    expire_time = timezone.now() - timedelta(minutes=1)
    deleted_count, _ = TaskResult.objects.filter(date_done__lt=expire_time).delete()
    # deleted_count, _ = TaskResult.objects.all().delete()
    print(f"Deleted {deleted_count} old task results. Message: {text}")
    
    return {"deleted_count": deleted_count, "message": text}


# ================================= Seller Profile Task ===============================

@shared_task
def revert_to_original_role(profile_id, original_role):
    try:
        profile = SellerProfile.objects.get(id=profile_id)
        profile.role = original_role
        profile.save()
        print(f"Reverted profile {profile_id} back to {original_role}")
    except SellerProfile.DoesNotExist:
        print(f"Profile {profile_id} does not exist")
        

@shared_task(name="celery_demo.tasks.revert_role")
def revert_role(profile_id, original_role):
    profile = SellerProfile.objects.filter(id=profile_id).first()
    if profile:
        profile.role = original_role
        profile.save()

# @shared_task
# def expire_temporary_roles():
#     expired_roles = TemporaryRole.objects.filter(expires_at__lt=timezone.now())
#     for temp_role in expired_roles:
#         # Restore the original role
#         seller_profile = temp_role.seller_profile
#         seller_profile.role = "manager"  # Reverting to the manager role
#         seller_profile.save()
#         temp_role.delete()  
        
# @shared_task
# def grant_temporary_role(user_id, restaurant_id, target_role, duration_minutes):
#     profile = SellerProfile.objects.get(user_id=user_id, restaurant_id=restaurant_id)
#     original_role = profile.role

#     # Assign the temporary role
#     profile.role = target_role
#     profile.save()

#     # Schedule the role to revert after `duration_minutes`
#     revert_time = timezone.now() + timedelta(minutes=duration_minutes)
#     revert_temporary_role.apply_async(
#         args=[user_id, restaurant_id, original_role], 
#         eta=revert_time
#     )

# @shared_task
# def revert_temporary_role(user_id, restaurant_id, original_role):
#     profile = SellerProfile.objects.get(user_id=user_id, restaurant_id=restaurant_id)
#     profile.role = original_role
#     profile.save()
