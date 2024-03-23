from django.http import JsonResponse, HttpResponse
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404

from ..models import User
from .session_datas import fill_session_with_user_info, get_user_from_request


def registerNewUser(request):
    # Get the user's information from the request
    login = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    firstname = request.POST.get('firstname')

    # Check if the user already exists in the database
    user = User.objects.filter(login=login).first()
    if user:
        return JsonResponse({'error': 'username'}, status=200)

    # Check if the email already exists in the database
    user = User.objects.filter(email=email).first()
    if user:
        return JsonResponse({'error': 'email'}, status=200)

    # Create a new user in the database
    user = User.objects.create(
        login=login,
        email=email,
        password=password,
        first_name=firstname,
        loginWithApi=False,
        image_link='./assets/anonymous-icon.png',
    )
    user.save()

    # Save the user's information in the session
    # fill_session_with_user_info(request, user)

    return JsonResponse({'status': 'success'}, status=200)


def changeUserInfo(request):
    # Récupérer l'utilisateur à modifier
    # user = get_object_or_404(User, login='mabdali')
    user = get_user_from_request(request)

    if request.method == 'POST':
        # Récupérer les nouvelles informations de l'utilisateur depuis la requête
        pseudo = request.POST.get('first_name')
        email = request.POST.get('email')
        print("Nouveau pseudo:", pseudo)
        print("Nouvel email:", email)
        # Mettre à jour les champs de l'utilisateur
        user.first_name = pseudo
        user.email = email

        fill_session_with_user_info(request, user)

        # Sauvegarder les modifications dans la base de données
        user.save()

        return JsonResponse({'status': 'success'}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def changeUserImg(request):
    # Récupérer l'utilisateur à modifier
    # user = get_object_or_404(User, login='mabdali')
    user = get_user_from_request(request)

    if request.method == 'POST':
        # Récupérer les nouvelles informations de l'utilisateur depuis la requête
        img = request.POST.get('img')
        # Mettre à jour les champs de l'utilisateur
        user.image_link = img

        fill_session_with_user_info(request, user)

        # Sauvegarder les modifications dans la base de données
        user.save()

        return JsonResponse({'status': 'success'}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def changePassword(request):
    # Récupérer l'utilisateur à modifier
    user = get_user_from_request(request)

    if request.method == 'POST':
        # Récupérer les nouvelles informations de l'utilisateur depuis la requête
        password = request.POST.get('password')
        # Mettre à jour les champs de l'utilisateur
        user.password = password

        fill_session_with_user_info(request, user)

        # Sauvegarder les modifications dans la base de données
        user.save()

        return JsonResponse({'status': 'success'}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def normal_login(request):
    # Get the user's login and password from the request
    login = request.POST.get('username')
    password = request.POST.get('password')
    # Check if the user exists in the database
    user = User.objects.filter(login=login).first()
    if user:
        if user.loginWithApi and not user.password :
            return JsonResponse({'error': 'api'}, status=200)
        if user.password == password:

            # Save the user's information in the session
            if not user.twoStepsActive:
                fill_session_with_user_info(request, user)

            return JsonResponse({'status': 'success',
                                 'user': user.login,
                                 'img': user.image_link,
                                 'f2a': user.twoStepsActive}, status=200)
        else:
            return JsonResponse({'error': 'password'}, status=200)
    # return an json message if the user does not exist
    else:
        return JsonResponse({'error': 'username'}, status=200)
