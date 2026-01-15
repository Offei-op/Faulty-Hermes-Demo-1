from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

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





from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'chat/dashboard.html')