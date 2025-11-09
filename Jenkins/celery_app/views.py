from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from celery_demo.tasks import add, sub, revert_to_original_role
from celery_app.simplejwt_tokens import create_simplejwt_token_for_user
from celery_app.models import SellerProfile
from celery_app.serializers import RoleAssignmentSerializer, LoginSerializer
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from celery.result import AsyncResult
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
import json
import requests


# Enqueue tasks using delay()
def home_add(request):
    # result = add(10, 20) # Without delay() add method will wait for 5 second
    result = add.delay(10, 20)  # will return async object
    print("Result: ", result)
    template = "home.html"
    return render(request, template, {"result": result})


def home_sub(request):
    # result = sub(30, 10) # Without apply_async() sub method will wait for 5 second
    result = sub.apply_async(args=[30, 10])  # will return async object
    print("Result: ", result)
    template = "home_sub.html"
    return render(request, template, {"result": result})


def check_result(request, task_id):
    # Retrive the result using task id
    result = AsyncResult(task_id)  # will return async object
    print("Ready: ", result.ready())
    print("Successful: ", result.successful())
    print("Failed: ", result.failed())
    template = "result.html"
    return render(request, template, {"result": result})


def contact(request):
    template = "contact.html"
    return render(request, template)

class GetAccessTokenFromStaging(viewsets.ViewSet):
    def list(self, request):
        url = 'https://staging.api.ubaky.com/accounts/login/'
        data = {
            "email": "mdsagorluc@gmail.com",
            "password": "1234"
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            token = response.json().get('access')
            print("Access token: ", token)
            return Response({"access_token": token}, status=status.HTTP_200_OK)
        
        print("Failed: ", response.json())
        return Response({"error": response.json().get({"details": "Login faild"})}, status=response.status_code)
        

class CheckAccess(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        get_seller = SellerProfile.objects.get(user=request.user)
        get_role = get_seller.role
        
        if get_role == "manager":
            msg = {"message:":"You are employee now in manager role"}
            return Response(msg, status=status.HTTP_200_OK)
        
        return Response({"message": "Only manager can access this feature"}, status=status.HTTP_404_NOT_FOUND)
        


# ================================ ROLE ASSIGNMENT VIEW ===============================
class RoleAssignmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_classes = RoleAssignmentSerializer

    def create(self, request):
        serializer = self.serializer_classes(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            role = serializer.validated_data["role"]
            duration_minutes = serializer.validated_data["duration_minutes"]

            user = get_object_or_404(User, username=username)
            profile = get_object_or_404(SellerProfile, user=user)

            # Store the original role to revert later
            original_role = profile.role
            profile.role = role
            profile.save()

            # Schedule task to revert role after duration_minutes
            revert_to_original_role.apply_async(
                args=[profile.id, original_role],
                countdown=duration_minutes * 60,  # Convert minutes to seconds
            )

            return Response(
                {
                    "message": f"{username} assigned {role} role for {duration_minutes} minutes."
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# ==================================== LOGIN VIEW =====================================  
class LoginView(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data
        username = data.get("username")
        password = data.get("password")
        print(username, "line 99")
        if not username:
            return Response(
                {"error": "Username should not be empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not password:
            return Response(
                {"error": "Password should not be empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            e_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "Username not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if not e_user.check_password(password):
            return Response(
                {"error": "Password not match"}, status=status.HTTP_400_BAD_REQUEST
            )

        auth_user = authenticate(username=username, password=password)

        if auth_user is not None:
            user = User.objects.get(username=username)
            tokens = create_simplejwt_token_for_user(user)
            serializer = LoginSerializer(user)
            msg = {
                "message": "User login successfull",
                "data": serializer.data,
            }
            
            msg["token"] = tokens

            return Response(msg, status=status.HTTP_200_OK)
        else:
            msg = {"error": "Auth user is none"}
            return Response(msg, status=status.HTTP_401_UNAUTHORIZED) 
        
        
# ================================== LOGOUT VIEW ==================================
        
# class LogoutView(APIView):
#     permission_classes = [
#         IsAuthenticated,
#     ]
#     @csrf_exempt
#     def post(self, request):
#         token = Token.objects.get(user=request.user)
#         if token:
#             token.delete()
#             msg = {
#                 "message": "User logout successfully",
#             }
#             return Response(msg, status=status.HTTP_200_OK)
#         else:
#             msg = {"error": "Token not found"}
#             return Response(msg, status=status.HTTP_404_NOT_FOUND)
    
    
    
# ================================== WILL WORK LETER ====================================

# class RoleAssignmentViewSet(viewsets.ViewSet):
#     def create(self, request):
#         serializer = RoleAssignmentSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.validated_data['username']
#             role = serializer.validated_data['role']
#             duration_minutes = serializer.validated_data['duration_minutes']

#             user = get_object_or_404(User, username=username)
#             profile = get_object_or_404(SellerProfile, user=user)

#             # Store the original role to revert later
#             original_role = profile.role
#             profile.role = role
#             profile.save()

#             # Schedule task to revert role after `duration_minutes`
#             schedule, _ = IntervalSchedule.objects.get_or_create(
#                 every=duration_minutes,
#                 period=IntervalSchedule.MINUTES,
#             )

#             PeriodicTask.objects.create(
#                 interval=schedule,
#                 name=f"Revert role of {username} to {original_role} in {duration_minutes} minutes",
#                 task='celery_demo.tasks.revert_role',
#                 args=json.dumps([profile.id, original_role])
#             )

#             return Response({"message": f"{username} assigned {role} role for {duration_minutes} minutes."}, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
