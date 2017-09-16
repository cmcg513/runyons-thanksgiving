# from django.contrib.auth import authenticate
from django.shortcuts import render

def index(request):
    return render(request, 'basic/index.html', {})

# def login(request):
#     user = authenticate(
#         username=request.POST['username'], 
#         password=request.POST['password']
#         )
#     if user is not None:
#         return render(request, 'meals/index.html', {})
    
#     return render(
#         request, 
#         'website/login.html', 
#         {'error_message': "Invalid username or password."}
#         )
        