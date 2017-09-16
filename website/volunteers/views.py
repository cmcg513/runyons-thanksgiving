from django.shortcuts import render, redirect
from . import forms


def index(request):
    return redirect('volunteers:about', permanent=True)

def about(request):
    return render(request, 'volunteers/about.html', {})

def contact(request):
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            print(request.POST)
            return redirect('volunteers:thanks')
    else:
        form = forms.ContactForm()
    return render(request, 'volunteers/contact.html', {'form': form})

def thanks(request):
    return render(request, 'volunteers/thanks.html', {})
