import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Notify others
        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'player_join',
                    'username': user.username,
                    'is_host': await self.is_host(user)
                }
            )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'start_game':
            # Verify host
            if await self.is_host(self.scope["user"]):
                # Start game logic
                await self.start_game_logic()
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_start',
                        'room_id': self.room_id
                    }
                )

        elif action == 'run_code':
            await self.handle_run_code(data.get('code'))
            
        elif action == 'submit_code':
            await self.handle_submit_code(data.get('code'))
            
        elif action == 'chat_message':
            message = data.get('message')
            if message:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'username': self.scope["user"].username,
                        'message': message,
                        'timestamp': str(__import__('datetime').datetime.now().strftime('%H:%M'))
                    }
                )
            
        elif action == 'chat_message':
            message = data.get('message')
            if message:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'username': self.scope["user"].username,
                        'message': message,
                        'timestamp': str(__import__('datetime').datetime.now().strftime('%H:%M'))
                    }
                )
        
        elif action == 'cheat_alert':
            from .models import Participant
            cheat_type = data.get('type')
            if cheat_type == 'tab_switch':
                # Increment Tab Switch Count
                user = self.scope["user"]
                try:
                    participant = await database_sync_to_async(lambda: Participant.objects.get(user=user, room__room_id=self.room_id))()
                    participant.tab_switches += 1
                    await database_sync_to_async(participant.save)()
                except Participant.DoesNotExist:
                    pass

                # Broadcast public shaming
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'username': 'SYSTEM',
                        'message': f"⚠ {self.scope['user'].username} switched tabs!",
                        'timestamp': str(__import__('datetime').datetime.now().strftime('%H:%M'))
                    }
                )
        
        elif action == 'get_submission_code':
            await self.handle_get_submission_code(data.get('target_username'))

    async def handle_run_code(self, code):
        from .execution import execute_python_code
        from .models import Room
        
        # Use select_related to fetch problem in the same query
        try:
            get_room = database_sync_to_async(lambda: Room.objects.select_related('problem').get(room_id=self.room_id))
            room = await get_room()
        except Room.DoesNotExist:
            return

        if not room.problem:
            return

        test_cases = room.problem.test_cases[:1] # Run only first case for 'Run'
        
        # Run in thread to not block
        result = await database_sync_to_async(execute_python_code)(code, test_cases)
        
        await self.send(text_data=json.dumps({
            'type': 'run_result',
            'result': result
        }))

    async def handle_submit_code(self, code):
        from .execution import execute_python_code
        from .models import Room, Participant, Submission
        
        # Use select_related here too
        try:
            get_room = database_sync_to_async(lambda: Room.objects.select_related('problem').get(room_id=self.room_id))
            room = await get_room()
        except Room.DoesNotExist:
            return

        if not room.problem:
            return
            
        user = self.scope["user"]
        get_participant = database_sync_to_async(lambda: Participant.objects.get(user=user, room=room))
        try:
            participant = await get_participant()
        except Participant.DoesNotExist:
            return
            
        # --- Check Submission Limit ---
        submission_count = await database_sync_to_async(lambda: participant.submissions.count())()
        if submission_count >= 3:
             await self.send(text_data=json.dumps({
                'type': 'submit_result',
                'passed': False,
                'error': 'MAX_LIMIT_REACHED',
                'message': 'You have exhausted your 3 attempts!'
            }))
             return

        test_cases = room.problem.test_cases
        result = await database_sync_to_async(execute_python_code)(code, test_cases)
        
        is_passed = result['passed'] == result['total']
        execution_time = result.get('execution_time', 0.0)
        
        await database_sync_to_async(Submission.objects.create)(
            participant=participant,
            code=code,
            passed=is_passed,
            output_log=str(result['results']),
            execution_time=execution_time
        )
        
        # Update Participant State (Always update completed_test_cases)
        participant.completed_test_cases = result['passed']
        
        if is_passed:
            # Only award points if this is the FIRST time they passed (i.e., not finished yet)
            if not participant.finished_at:
                participant.score += 100
                participant.finished_at = await database_sync_to_async(lambda: __import__('django.utils.timezone').utils.timezone.now())()
            
                # --- Rating Logic ---
                # Simple reward: +10 rating for solving a problem
                def update_rating(u):
                    from .models import UserProfile
                    # Robustly get or create profile to avoid errors for legacy users
                    profile, created = UserProfile.objects.get_or_create(user=u)
                    if not created and profile.wins > 0:
                         # Double check to prevent spamming rating? 
                         # Actually checking finished_at above is enough for this session.
                         pass
                    
                    profile.wins += 1
                    profile.matches_played += 1
                    profile.rating += 10
                    profile.save()
                
                await database_sync_to_async(update_rating)(user)
        
        # If this was the 3rd fail, maybe mark as finished?
        # User request: "limit is 3 after the last submission the coding game ends"
        # Since we incremented submission count implicitly by creating one, 
        # checking new count might be complex async. But current was < 3.
        # This is the (submission_count + 1)th submission.
        if (submission_count + 1) >= 3 and not is_passed:
            # Mark as finished (failed)
             if not participant.finished_at:
                 # We mark finished_at so they can't submit more (logic elsewhere verifies status too?)
                 # Actually finished_at implies they are done.
                 participant.finished_at = await database_sync_to_async(lambda: __import__('django.utils.timezone').utils.timezone.now())()
        
        await database_sync_to_async(participant.save)()
        
        # Send result to user
        await self.send(text_data=json.dumps({
            'type': 'submit_result',
            'result': result,
            'passed': is_passed,
            'is_limit_reached': (submission_count + 1) >= 3
        }))

        # Broadcast Leaderboard Update
        await self.broadcast_leaderboard()
        
        # Check if ALL participants are finished
        # check_all_finished is already decorated with @database_sync_to_async
        all_finished = await self.check_all_finished()
        if all_finished:
            # Broadcast Game Over
            leaderboard_data = await self.get_leaderboard_data()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_over_event', # distinctive name
                    'data': leaderboard_data
                }
            )

    @database_sync_to_async
    def check_all_finished(self):
        from .models import Participant
        # Debugging: Print who is not finished
        unfinished = Participant.objects.filter(room__room_id=self.room_id, finished_at__isnull=True)
        if unfinished.exists():
            print(f"DEBUG: Unfinished participants in {self.room_id}: {[p.user.username for p in unfinished]}")
            return False
        print(f"DEBUG: All participants finished in {self.room_id}")
        return True

    async def broadcast_leaderboard(self):
        leaderboard_data = await self.get_leaderboard_data()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'leaderboard_update',
                'data': leaderboard_data
            }
        )

    async def leaderboard_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def game_over_event(self, event):
         print(f"DEBUG: Processing game_over_event for {self.scope['user'].username}")
         await self.send(text_data=json.dumps({
            'type': 'game_over',
            'leaderboard': event['data']
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_leaderboard_data(self):
        from .models import Participant
        participants = Participant.objects.filter(room__room_id=self.room_id).select_related('user', 'user__profile', 'room', 'room__problem').order_by('-score', 'finished_at')
        data = []
        for p in participants:
            status = 'Finished' if p.finished_at else 'Coding'
            
            # Calculate total test cases for the problem if available
            total_cases = 0
            if p.room.problem:
                total_cases = len(p.room.problem.test_cases)
            
            # Safe access to profile (signal should have created it, but good to be safe)
            rating = 1200
            if hasattr(p.user, 'profile'):
                rating = p.user.profile.rating

            data.append({
                'username': p.user.username,
                'score': p.score,
                'status': status,
                'cases_passed': p.completed_test_cases,
                'total_cases': total_cases,
                'rating': rating,
                'is_host': p.user == p.room.host
            })
        return data

    async def player_join(self, event):
        # When player joins, send them the current leaderboard
        # Also notify others of join (already done), but let's also update leaderboard for everyone
        await self.broadcast_leaderboard()
        
        await self.send(text_data=json.dumps({
            'type': 'player_join',
            'username': event['username'],
            'is_host': event['is_host']
        }))
    
    async def game_start(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_start',
            'room_id': event['room_id']
        }))

    @database_sync_to_async
    def start_game_logic(self):
        from .models import Room, Problem
        room = Room.objects.get(room_id=self.room_id)
        if not room.is_active:
            # Select problem if not set
            if not room.problem:
                from .ai import generate_problem_via_ai
                
                # Try AI Generation first
                print(f"Attempting AI generation for {room.topic} - {room.difficulty}")
                ai_problem = generate_problem_via_ai(room.topic, room.difficulty)
                
                if ai_problem:
                    room.problem = ai_problem
                else:
                    # Fallback to local DB
                    problems = Problem.objects.all()
                    if room.topic != 'Random':
                        problems = problems.filter(topic=room.topic)
                    if room.difficulty:
                        problems = problems.filter(difficulty=room.difficulty)
                    
                    if problems.exists():
                        room.problem = problems.order_by('?').first()
                    else:
                        # Final Fallback
                        room.problem = Problem.objects.order_by('?').first()
            
            room.is_active = True
            room.save()

    async def handle_get_submission_code(self, target_username):
        from .models import Participant, Submission, User
        
        user = self.scope["user"]
        
        # Security: You can only view others if YOU have finished the game (or are finished due to limit) OR room is inactive
        # check_can_view_solutions is already decorated with @database_sync_to_async, so it is awaitable
        can_view = await self.check_can_view_solutions(user)
        
        if not can_view:
             await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'You must complete the game to view solutions.'
            }))
             return

        # Fetch target's code
        try:
            target_user = await database_sync_to_async(User.objects.get)(username=target_username)
            # Fetch last submission (or best passed one?) - let's get last
            # get_latest_submission is also decorated
            target_submission = await self.get_latest_submission(target_user)
            
            if target_submission:
                await self.send(text_data=json.dumps({
                    'type': 'submission_code',
                    'username': target_username,
                    'code': target_submission.code,
                    'passed': target_submission.passed,
                    'execution_time': target_submission.execution_time
                }))
            else:
                 await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'No submission found for user.'
                }))

        except User.DoesNotExist:
             pass

    @database_sync_to_async
    def check_can_view_solutions(self, user):
        from .models import Room, Participant
        try:
            room = Room.objects.get(room_id=self.room_id)
            if not room.is_active: return True
            
            p = Participant.objects.get(user=user, room=room)
            return p.finished_at is not None
        except:
            return False

    @database_sync_to_async
    def get_latest_submission(self, target_user):
        from .models import Participant, Submission
        try:
            p = Participant.objects.get(user=target_user, room__room_id=self.room_id)
            return p.submissions.order_by('-timestamp').first()
        except:
            return None

    @database_sync_to_async
    def is_host(self, user):
        from .models import Room
        try:
            room = Room.objects.get(room_id=self.room_id)
            return room.host == user
        except Room.DoesNotExist:
            return False
