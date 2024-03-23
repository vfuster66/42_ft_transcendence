from django.http import JsonResponse, HttpResponse
from django.contrib.sessions.models import Session
from ..models import User
from .session_datas import get_user_from_request

def add_friend(request):
	# Get the user's information from the request
	login = request.POST.get('username')
	friend_login = request.POST.get('friend')

	# Check if the user already exists in the database
	user = User.objects.filter(login=login).first()
	if not user:
		return JsonResponse({'error': 'username'}, status=200)

	# Check if the friend already exists in the database
	friend = User.objects.filter(login=friend_login).first()
	if not friend:
		return JsonResponse({'error': 'not_found'}, status=200)

	# Check if the friend is not already in the user's friends list
	if friend in user.friends.all():
		return JsonResponse({'error': 'already_friend'}, status=200)

	# Add the friend to the user's friends list
	user.friends.add(friend)
	user.save()

	# update session data
	session = request.session
	session['friends'] = list(user.friends.all().values())

	return JsonResponse({'status': 'success'}, status=200)

def remove_friend(request):
	# Get the user's information from the request
	friend_login = request.POST.get('friend')

	# Check if the user already exists in the database
	user = get_user_from_request(request)
	if not user:
		return JsonResponse({'error': 'username'}, status=200)

	# Check if the friend already exists in the database
	friend = User.objects.filter(login=friend_login).first()
	if not friend:
		return JsonResponse({'error': 'friend'}, status=200)

	# Check if the friend is in the user's friends list
	if friend not in user.friends.all():
		return JsonResponse({'error': 'not_friend'}, status=200)

	# Remove the friend from the user's friends list
	user.friends.remove(friend)
	user.save()

	# update session data
	session = request.session
	session['friends'] = list(user.friends.all().values())

	return JsonResponse({'status': 'success'}, status=200)
