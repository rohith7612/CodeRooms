from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Room, Participant, Problem
from .forms import CreateRoomForm, SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# Protected Routes - Redirect to Login if illegal access
@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def create_room(request):
    if request.method == 'POST':
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            
            # Add host as participant
            Participant.objects.create(user=request.user, room=room)
            
            return redirect('room_lobby', room_id=room.room_id)
    else:
        form = CreateRoomForm()
    
    return render(request, 'create_room.html', {'form': form})

@login_required
def room_lobby(request, room_id):
    room = get_object_or_404(Room, room_id=room_id)
    
    # Handle joining: Only join if game is NOT active, or if already a participant
    participant = Participant.objects.filter(user=request.user, room=room).first()
    
    if not participant and not room.is_active:
         participant = Participant.objects.create(user=request.user, room=room)

    return render(request, 'room_lobby.html', {
        'room': room, 
        'participant': participant,
        'is_host': room.host == request.user
    })

@login_required
def arena(request, room_id):
    room = get_object_or_404(Room, room_id=room_id)
    
    # Check if existing participant
    participant = Participant.objects.filter(user=request.user, room=room).first()
    is_spectator = False

    if not participant:
        is_spectator = True
        # If room isn't active, spectators shouldn't really be here unless we allow pre-game spectating?
        # For now, keep the active check.
        if not room.is_active:
             return redirect('room_lobby', room_id=room_id)
             
    if not is_spectator and not room.is_active:
        return redirect('room_lobby', room_id=room_id)
    
    return render(request, 'arena.html', {
        'room': room,
        'participant': participant, # Can be None for spectators
        'problem': room.problem,
        'is_spectator': is_spectator
    })

@login_required
def game_over(request, room_id):
    room = get_object_or_404(Room, room_id=room_id)
    # Check if user was a participant? Maybe not strictly required but good for context
    
    # Get all participants sorted by score (desc) and then maybe execution time?
    # For now sort by score desc.
    participants = Participant.objects.filter(room=room).select_related('user__profile').order_by('-score', 'finished_at')
    
    return render(request, 'game_over.html', {
        'room': room,
        'participants': participants
    })

@login_required
def dashboard(request):
    from django.db.models import Sum
    user = request.user
    
    # Ensure profile exists
    if not hasattr(user, 'profile'):
        from .models import UserProfile
        UserProfile.objects.create(user=user)

    profile = user.profile
    
    # Fetch History
    participants = Participant.objects.filter(user=user).select_related('room', 'room__problem').order_by('-joined_at')
    
    # Aggregates
    total_points = participants.aggregate(Sum('score'))['score__sum'] or 0
    
    # Topic Analysis
    topic_map = {} # {'Array': {'total': 5, 'passed': 3}}
    
    for p in participants:
        if p.room.problem and p.room.problem.topic:
            t = p.room.problem.topic
            if t not in topic_map:
                topic_map[t] = {'total': 0, 'passed': 0}
            
            topic_map[t]['total'] += 1
            # Assuming score > 0 means passed (since we give 100 for pass) or check completed cases
            if p.score >= 100: 
                topic_map[t]['passed'] += 1
    
    topic_stats = []
    for name, data in topic_map.items():
        win_rate = (data['passed'] / data['total']) * 100 if data['total'] > 0 else 0
        topic_stats.append({
            'name': name,
            'total': data['total'],
            'passed': data['passed'],
            'win_rate': win_rate
        })
    
    # Sort by Win Rate desc
    topic_stats.sort(key=lambda x: x['win_rate'], reverse=True)
    
    strongest_topic = topic_stats[0] if topic_stats else None
    weakest_topic = topic_stats[-1] if topic_stats else None # Simple logic, maybe filter for min attempts
    
    return render(request, 'dashboard.html', {
        'profile': profile,
        'total_points': total_points,
        'recent_matches': participants[:10], # Show last 10
        'topic_stats': topic_stats,
        'strongest_topic': strongest_topic,
        'weakest_topic': weakest_topic
    })
