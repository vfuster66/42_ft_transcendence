from django.shortcuts import render
from django.conf import settings

def environment_variables_view(request):
    context = {
        'POSTGRES_USER': settings.POSTGRES_USER,
        'POSTGRES_PASSWORD': settings.POSTGRES_PASSWORD,
    }
    return render(request, 'base.html', context)
