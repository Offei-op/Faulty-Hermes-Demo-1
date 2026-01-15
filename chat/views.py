from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Message, Profile

from django.contrib.auth.decorators import login_required



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile and set target language from the form
            lang = request.POST.get('target_language', 'en')
            Profile.objects.create(user=user, target_language=lang)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'chat/register.html', {'form': form})






@login_required
def dashboard(request):
    return render(request, 'chat/dashboard.html')

@login_required
def room(request, username):
    friend = User.objects.get(username=username)
    # Fetch messages between David and Jack
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=friend)) |
        (Q(sender=friend) & Q(receiver=request.user))
    ).order_by('timestamp')[:50]

    return render(request, 'chat/room.html', {
        'friend_username': username,
        'chat_messages': messages,
    })


@login_required
def add_friend(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            friend_user = User.objects.get(username=username)
            friend_profile = friend_user.profile
            
            # Prevent adding yourself
            if friend_user == request.user:
                messages.error(request, "You cannot add yourself!")
            else:
                request.user.profile.friends.add(friend_profile)
                messages.success(request, f"Added {username} as a friend!")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            
    return redirect('dashboard')