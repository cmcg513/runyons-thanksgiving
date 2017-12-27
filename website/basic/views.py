# from django.contrib.auth import authenticate
from django.shortcuts import render
from website.settings import EVENT_YEAR, DONE_FOR_THE_YEAR

def index(request):
    return render(request, 'basic/index.html', {
        'EVENT_YEAR': EVENT_YEAR,
        'next_year': EVENT_YEAR + 1,
        'DONE_FOR_THE_YEAR': DONE_FOR_THE_YEAR
    })

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
        