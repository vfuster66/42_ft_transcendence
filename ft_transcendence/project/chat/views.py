
# chat/views.py

#########################################################################################################

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Invitation, Message, Block
from .forms import RoomForm
from django.contrib.auth import get_user_model
from django.http import HttpResponse
import logging
from django.http import JsonResponse

#########################################################################################################

logger = logging.getLogger(__name__)

#########################################################################################################

User = get_user_model()

#########################################################################################################

@login_required
def room_detail(request, room_name):
    room = get_object_or_404(Room, name=room_name)
    if not room.is_member(request.user):
        logger.warning(f"Unauthorized access attempt to room: {room_name} by user: {request.user.username}")
        return redirect('access_denied_view')
    
    avatar_url = request.user.profile.avatar.url if request.user.profile.avatar else '/static/images/avatars/avatar_0.png'

    context = {
        'room_name': room.name,
        'room_is_private': room.is_private,
        'avatar_url': avatar_url,
        'username': request.user.username,
        'status': getattr(request.user.profile, 'status', 'Non disponible'),
        'bio': getattr(request.user.profile, 'bio', 'Aucune biographie disponible.')
    }
    return render(request, 'chat/chat.html', context)


def room(request, room_name):
    room_details = Room.objects.get(name=room_name)
    messages = Message.objects.filter(room=room_details).order_by('-timestamp')
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'messages': messages
    })


@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            try:
                new_room = form.save(commit=False)
                new_room.save()
                new_room.members.add(request.user)
                logger.info(f"Room created: {new_room.name} by user: {request.user.username}")
                return redirect('room_detail', room_name=new_room.name)
            except Exception as e:
                logger.error(f"Error creating room: {e}")
                return HttpResponse(f"Erreur lors de la création de la salle : {str(e)}", status=500)
        else:
            logger.debug("Form data is invalid")
            return render(request, 'chat/create_room.html', {'form': form})
    else:
        form = RoomForm()
    return render(request, 'chat/create_room.html', {'form': form})


@login_required
def room_list(request):
    rooms = Room.objects.all()
    logger.info(f"{request.user.username} accessed the room list")
    return render(request, 'chat/room_list.html', {'rooms': rooms})


def access_denied_view(request):
    logger.warning(f"Access denied for user: {request.user.username}")
    return HttpResponse("Accès refusé", status=403)


@login_required
def block_user(request, user_id):
    try:
        user_to_block = User.objects.get(pk=user_id)
        room_name = request.GET.get('room')
        room = Room.objects.get(name=room_name)
        Block.objects.create(blocker=request.user, blocked=user_to_block, room=room)
        return HttpResponse("User successfully blocked.")
    except (User.DoesNotExist, Room.DoesNotExist):
        return HttpResponse("User or Room not found.", status=404)


@login_required
def unblock_user(request, user_id):
    try:
        user_to_unblock = User.objects.get(pk=user_id)
        room_name = request.GET.get('room')
        room = Room.objects.get(name=room_name)
        Block.objects.get(blocker=request.user, blocked=user_to_unblock, room=room).delete()
        return HttpResponse("User successfully unblocked.")
    except (Block.DoesNotExist, User.DoesNotExist, Room.DoesNotExist):
        return HttpResponse("Block, User, or Room not found.", status=404)


def get_user_profile(request):
    username = request.GET.get('username')
    if request.user.is_authenticated:
        user = get_object_or_404(User, username=username)
        data = {
            'username': user.username,
            'avatarUrl': user.profile.avatar.url if user.profile.avatar else '/static/images/avatars/avatar_0.png',
            'status': getattr(user.profile, 'status', 'Non disponible'),
            'bio': getattr(user.profile, 'bio', 'Aucune biographie disponible.')
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
#########################################################################################################