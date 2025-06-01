from django.shortcuts import render, redirect
from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser, Position, PartyList, Election, Vote, Candidate, PartyRequest
from .serializers import RegisterSerializer, PositionSerializer, PartyListSerializer, ElectionSerializer, LoginSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from typing import Any
from .rate_limit import rate_limit
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.db.models import F, Sum
from django.core import exceptions as models
from django.db import IntegrityError # Added for handling potential errors
import logging # Added for logging errors
from django.utils import timezone # Import timezone
from django.core.exceptions import ObjectDoesNotExist
import json
from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from rest_framework.routers import DefaultRouter
from .forms import PositionForm # Import the form

# Create your views here.

def student_register(request):
    if request.method == 'POST':
        try:
            # Create a dictionary with the form data
            data = {
                'student_id': request.POST.get('student_id'),
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'email': request.POST.get('email'),
                'password': request.POST.get('password'),
                'confirm_password': request.POST.get('confirm_password'),
                'photo_url': request.FILES.get('photo_url')
            }
            
            # Use the serializer to validate and create the user
            serializer = RegisterSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save() # Save the user object returned by serializer
                messages.success(request, 'Registration successful! Please login.')
                return redirect('student_login')
            else:
                return render(request, 'authentication/student_register.html', {
                    'error_message': serializer.errors
                })
        except Exception as e:
            return render(request, 'authentication/student_register.html', {
                'error_message': str(e)
            })
    
    return render(request, 'authentication/student_register.html')

def student_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('student_login')
    
    # Get recent votes for the user
    # pylint: disable=no-member
    recent_votes = Vote.objects.filter(user=request.user).select_related(
        'election', 'position', 'candidate__user'
    ).order_by('-timestamp')[:5]
    # pylint: enable=no-member
    
    # Format the votes for the template
    formatted_votes = []
    for vote in recent_votes:
        formatted_votes.append({
            'candidate_name': f"{vote.candidate.user.first_name} {vote.candidate.user.last_name}",
            'position': vote.position.position_name,
            'election_title': vote.election.title,
            'timestamp': vote.timestamp
        })
    
    return render(request, 'student_portal/student_dashboard.html', {
        'recent_votes': formatted_votes
    })

def student_login(request):
    if request.method == 'POST':
        student_id = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = CustomUser.objects.get(student_id=student_id)
            if user.check_password(password) and user.role == 'student':
                login(request, user)
                return redirect('student_dashboard')
            else:
                messages.error(request, 'Invalid credentials or not a student account.')
        except models.ObjectDoesNotExist:
            messages.error(request, 'Invalid credentials or not a student account.')
    
    return render(request, 'authentication/student_login.html')

def student_logout(request):
    logout(request)
    return redirect('student_login')

def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(f"Attempting login for email: {email}") # Debugging line

        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                print(f"User found: {user.email}, Role: {user.role}, Is Active: {user.is_active}") # Debugging line
                if user.role == 'admin':
                    login(request, user)
                    welcome_message = f"Welcome, {user.first_name} {user.last_name}!"
                    if not user.first_name and not user.last_name:
                        welcome_message = "Welcome, Administrator!"
                    request.session['admin_welcome_message'] = welcome_message
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Invalid credentials or not an admin account.')
            else:
                print("Authentication failed: Incorrect password") # Debugging line
                messages.error(request, 'Invalid credentials or not an admin account.')
        except ObjectDoesNotExist:
            print("Authentication failed: User not found with this email") # Debugging line
            messages.error(request, 'Invalid credentials or not an admin account.')
    return render(request, 'authentication/admin_login.html')

def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('admin_login') # Redirect to our custom admin login

    # Get current time for status updates
    current_time = timezone.now()

    # Update 'ongoing' to 'completed' if the end date has passed
    Election.objects.filter(status='ongoing', end_date__lte=current_time).update(status='completed') # pylint: disable=no-member

    # Update 'scheduled' to 'ongoing' if the start date has passed but the end date has not
    Election.objects.filter(status='scheduled', start_date__lte=current_time, end_date__gt=current_time).update(status='ongoing') # pylint: disable=no-member
    # pylint: enable=no-member

    # Debugging: Print user details
    # print(f"DEBUG: User (admin_dashboard): {request.user.username}")
    # print(f"DEBUG: First Name: {request.user.first_name}")
    # print(f"DEBUG: Last Name: {request.user.last_name}")
    # print(f"DEBUG: Email: {request.user.email}")
    # print(f"DEBUG: Role: {request.user.role}")

    # Fetch dashboard data using Django ORM
    # pylint: disable=no-member
    total_students = CustomUser.objects.filter(role='student').count() # type: ignore
    active_elections_count = Election.objects.filter(status__in=['scheduled', 'ongoing']).count() # type: ignore
    total_candidates = Candidate.objects.count() # type: ignore

    active_elections = Election.objects.filter(status__in=['scheduled', 'ongoing']).order_by('-start_date') # type: ignore
    completed_elections = Election.objects.filter(status='completed').order_by('-end_date') # type: ignore
    # pylint: enable=no-member

    context = {
        'total_students': total_students,
        'active_elections_count': active_elections_count,
        'total_candidates': total_candidates,
        'active_elections': active_elections,
        'completed_elections': completed_elections,
        # 'user_name': request.user.get_full_name() or request.user.email, # Use get_full_name or email
        # Messages are handled automatically by Django's messages middleware
    }

    # Retrieve and clear welcome message from session if it exists
    welcome_message = request.session.pop('admin_welcome_message', None)
    if welcome_message:
        context['admin_welcome_message'] = welcome_message

    return render(request, 'admin_portal/admin_dashboard.html', context)

@csrf_exempt
@require_POST
def clear_admin_welcome_message(request):
    if request.session.get('admin_welcome_message'):
        del request.session['admin_welcome_message']
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

def admin_logout(request):
    logout(request)
    return redirect('admin_login_custom')

def admin_create_election(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('admin_login_custom')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'election':
            title = request.POST.get('title')
            description = request.POST.get('description')
            start_date_str = request.POST.get('start_date')
            start_time_str = request.POST.get('start_time')
            end_date_str = request.POST.get('end_date')
            end_time_str = request.POST.get('end_time')

            try:
                start_datetime = timezone.datetime.strptime(f"{start_date_str} {start_time_str}", '%Y-%m-%d %H:%M')
                end_datetime = timezone.datetime.strptime(f"{end_date_str} {end_time_str}", '%Y-%m-%d %H:%M')

                # Make datetimes timezone aware, assuming TIME_ZONE is set in settings.py
                start_datetime = timezone.make_aware(start_datetime)
                end_datetime = timezone.make_aware(end_datetime)

                if start_datetime >= end_datetime:
                    messages.error(request, "Start date and time must be earlier than end date and time.")
                else:
                    Election.objects.create( # pylint: disable=no-member
                        title=title,
                        description=description,
                        start_date=start_datetime,
                        end_date=end_datetime,
                        status='scheduled',  # Default status
                        created_by=request.user
                    )
                    messages.success(request, 'Election created successfully!')
                    return redirect('admin_dashboard')

            except ValueError:
                messages.error(request, "Invalid date or time format. Please use YYYY-MM-DD and HH:MM.")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        elif form_type == 'position':
            # Handle position form submission
            form = PositionForm(request.POST)
            if form.is_valid():
                new_position = form.save(commit=False)
                # Set rank automatically
                # pylint: disable=no-member
                max_rank = Position.objects.all().order_by('-rank').first().rank if Position.objects.exists() else 0 # type: ignore
                # pylint: enable=no-member
                new_position.rank = max_rank + 1
                new_position.save()
                messages.success(request, 'Position added successfully!')
            else:
                messages.error(request, f"Error adding position: {form.errors}")
        else:
            messages.error(request, "Invalid form type.")

    # For GET request or failed POST, initialize forms
    election_form = None # We are not using forms.Form for election creation directly
    position_form = PositionForm()

    context = {
        'position_form': position_form,
    }
    return render(request, 'admin_portal/admin_create_election.html', context)

def admin_manage_party(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('admin_login_custom')

    if request.method == 'POST':
        approve_party_id = request.POST.get('approve_party_id')
        election_id = request.POST.get('election_id')
        party_members_json = request.POST.get('party_members')

        if approve_party_id and election_id and party_members_json:
            try:
                # pylint: disable=no-member
                party = PartyList.objects.get(id=approve_party_id) # type: ignore
                # pylint: enable=no-member
                if party.is_finalized and party.status != 'approved':
                    party.status = 'approved'
                    party.save()

                    members = json.loads(party_members_json)

                    for member in members:
                        # Create Candidate entry
                        # pylint: disable=no-member
                        Candidate.objects.create(
                            election_id=election_id,
                            user_id=member['user_id'],
                            student_id=member['student_id'], # Assuming student_id is passed
                            position_id=member['position_id'],
                            partylist_id=approve_party_id,
                            status='approved'
                        ) # type: ignore
                        # pylint: enable=no-member
                    messages.success(request, f"Party '{party.party_name}' approved and members added as candidates!")
                elif party.status == 'approved':
                    messages.info(request, f"Party '{party.party_name}' is already approved.")
                else:
                    messages.error(request, f"Party '{party.party_name}' is not finalized yet.")

            except PartyList.DoesNotExist: # type: ignore
                messages.error(request, "Party not found.")
            except Election.DoesNotExist: # type: ignore
                messages.error(request, "Election not found for the approved party.")
            except Exception as e:
                messages.error(request, f"Error approving party: {e}")
        else:
            messages.error(request, "Missing data for party approval.")

        return redirect('admin_manage_party')

    # Fetch finalized parties for display
    parties_queryset = PartyList.objects.filter(is_finalized=True).select_related( # pylint: disable=no-member
        'election', 'created_by'
    ).prefetch_related(
        Prefetch(
            'partyrequest_set', # This is the related_name from PartyRequest to PartyList
            queryset=PartyRequest.objects.filter(status='accepted').select_related('requested_member', 'position'), # pylint: disable=no-member
            to_attr='accepted_requests'
        )
    ) # type: ignore

    parties = {}
    for party in parties_queryset:
        members_data = []
        for req in party.accepted_requests:
            members_data.append({
                'user_id': str(req.requested_member.id), # UUID needs to be stringified
                'student_id': req.requested_member.student_id,
                'first_name': req.requested_member.first_name,
                'last_name': req.requested_member.last_name,
                'position_id': str(req.position.id) if req.position else None, # UUID needs to be stringified
                'position_name': req.position.position_name if req.position else 'N/A',
                'photo_url': req.requested_member.photo_url.url if req.requested_member.photo_url else None,
            })

        parties[str(party.id)] = {
            'party_name': party.party_name,
            'election_title': party.election.title if party.election else 'N/A',
            'election_id': str(party.election.id) if party.election else None,
            'members': members_data,
            'vision': party.vision,
            'mission': party.mission,
            'status': party.status,
        }

    return render(request, 'admin_portal/admin_manage_party.html', {'parties': parties})

def admin_manage_student(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('admin_login_custom')

    search_query = request.GET.get('search', '').strip()
    students = CustomUser.objects.filter(role='student') # type: ignore

    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        ) # type: ignore

    students = students.order_by('student_id')

    context = {
        'students': students,
        'search_query': search_query
    }
    return render(request, 'admin_portal/admin_manage_student.html', context)

@csrf_exempt
@require_POST
def admin_update_student_status(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
        user_id = data.get('id')
        new_status = data.get('status')

        if not user_id or not new_status:
            return JsonResponse({'success': False, 'error': 'Missing user ID or status'}, status=400)

        # pylint: disable=no-member
        user = CustomUser.objects.get(id=user_id, role='student') # type: ignore
        # pylint: enable=no-member
        user.status = new_status
        user.save()
        return JsonResponse({'success': True})
    except CustomUser.DoesNotExist: # pylint: disable=no-member
        return JsonResponse({'success': False, 'error': 'Student not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def admin_manage_result(request, election_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('admin_login_custom')

    election = None
    positions = []
    candidates_by_position = {}
    total_votes_by_position = {}

    try:
        # Fetch election details
        # pylint: disable=no-member
        election = Election.objects.get(id=election_id) # type: ignore
        # pylint: enable=no-member

        # Fetch positions
        # pylint: disable=no-member
        positions = Position.objects.all().order_by('rank') # type: ignore
        # pylint: enable=no-member

        # Fetch candidates and their votes for the current election
        # Using annotate to get total votes for each candidate
        # pylint: disable=no-member
        candidates_queryset = Candidate.objects.filter(election=election).select_related(
            'user', 'partylist', 'position'
        ).annotate(
            total_votes=Sum('vote__count')
        ).order_by('position__rank', '-total_votes') # type: ignore
        # pylint: enable=no-member

        # Organize candidates by position and calculate total votes per position
        for position in positions:
            candidates_for_this_position = []
            position_total_votes = 0
            for candidate in candidates_queryset:
                if candidate.position == position:
                    candidates_for_this_position.append({
                        'candidate_name': f"{candidate.user.first_name} {candidate.user.last_name}",
                        'party_name': candidate.partylist.party_name if candidate.partylist else 'N/A',
                        'total_votes': candidate.total_votes if candidate.total_votes is not None else 0,
                        'photo_url': candidate.user.photo_url.url if candidate.user.photo_url else None,
                        'vote_percentage': 0 # Placeholder, will calculate after total_votes_for_position is known
                    })
                    position_total_votes += (candidate.total_votes if candidate.total_votes is not None else 0)
            
            # After collecting all candidates for the position, calculate percentages
            for cand_data in candidates_for_this_position:
                if position_total_votes > 0:
                    cand_data['vote_percentage'] = (cand_data['total_votes'] / position_total_votes) * 100
                else:
                    cand_data['vote_percentage'] = 0

            candidates_by_position[position.id] = candidates_for_this_position
            total_votes_by_position[position.id] = position_total_votes

    except Election.DoesNotExist: # type: ignore
        messages.error(request, "Election not found.")
    except Exception as e:
        messages.error(request, f"An error occurred while fetching results: {e}")
        logging.error("Error in admin_manage_result: %s", e)

    context = {
        'election': election,
        'positions': positions,
        'candidates_by_position': candidates_by_position,
        'total_votes_by_position': total_votes_by_position,
    }
    return render(request, 'admin_portal/admin_manage_result.html', context)

def admin_update_election(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('admin_login_custom')
    
    if request.method == 'POST':
        election_id = request.POST.get('id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date_str = request.POST.get('start_date')
        start_time_str = request.POST.get('start_time')
        end_date_str = request.POST.get('end_date')
        end_time_str = request.POST.get('end_time')

        print(f"DEBUG: start_date_str = {start_date_str}, start_time_str = {start_time_str}")
        print(f"DEBUG: end_date_str = {end_date_str}, end_time_str = {end_time_str}")

        try:
            # Combine date and time strings and parse without seconds format
            start_datetime = timezone.datetime.strptime(f"{start_date_str} {start_time_str}", '%Y-%m-%d %H:%M')
            end_datetime = timezone.datetime.strptime(f"{end_date_str} {end_time_str}", '%Y-%m-%d %H:%M')
            
            # Make datetimes timezone aware
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            election = Election.objects.get(id=election_id) # pylint: disable=no-member
            election.title = title
            election.description = description
            election.start_date = start_datetime
            election.end_date = end_datetime
            election.status = request.POST.get('status')
            election.save()
            messages.success(request, 'Election updated successfully!')
        except Election.DoesNotExist: # pylint: disable=no-member
            messages.error(request, 'Election not found.')
        except ValueError as ve: # Catch ValueError specifically for parsing errors
            messages.error(request, f"Invalid date or time format: {ve}. Please use YYYY-MM-DD and HH:MM.")
        except Exception as e:
            messages.error(request, f'Error updating election: {e}')

    return redirect('admin_dashboard')

# def admin_add_position(request):
#     if not request.user.is_authenticated or request.user.role != 'admin':
#         return redirect('admin_login_custom')

#     if request.method == 'POST':
#         form = PositionForm(request.POST)
#         if form.is_valid():
#             new_position = form.save(commit=False)
#             # Set rank automatically
#             # pylint: disable=no-member
#             max_rank = Position.objects.all().order_by('-rank').first().rank if Position.objects.exists() else 0 # type: ignore
#             # pylint: enable=no-member
#             new_position.rank = max_rank + 1
#             new_position.save()
#             messages.success(request, 'Position added successfully!')
#             return redirect('admin_dashboard') # Redirect to dashboard or a specific manage positions page
#         else:
#             messages.error(request, "Error adding position. Please check the form.")
#     else:
#         form = PositionForm() # Empty form for GET request
    
#     return render(request, 'admin_portal/admin_add_position.html', {'form': form})

def student_profile(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('student_login')
    
    # Handle party requests (GET for display, POST for actions)
    party_members = []
    party_requests = []
    party_name = "No party assigned"

    # Fetch party members if the user is a party leader
    if request.user.partylist:
        # Only accepted members for this party, including the logged-in user
        accepted_requests = PartyRequest.objects.filter(
            party=request.user.partylist,
            status='accepted'
        ).select_related('requested_member', 'position')
        party_members = [
            {
                'member': req.requested_member,
                'position': req.position.position_name if req.position else 'N/A'
            }
            for req in accepted_requests
        ]
        party_name = request.user.partylist.party_name
    else:
        # Fetch party requests if the user is not part of a party
        party_requests = PartyRequest.objects.filter( # pylint: disable=no-member
            requested_member=request.user,
            status='pending'
        ).select_related('requester', 'party')
        # pylint: enable=no-member

    return render(request, 'student_portal/student_profile.html', {
        'user': request.user,
        'party_members': party_members,
        'party_requests': party_requests,
        'party_name': party_name
    })

def student_all_elections(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('student_login')

    # pylint: disable=no-member
    active_elections = Election.objects.filter(status='ongoing') # type: ignore
    return render(request, 'student_portal/student_all_elections.html', {
        'elections': active_elections
    })
    # pylint: enable=no-member

def student_my_vote(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('student_login')
    
    # pylint: disable=no-member
    my_votes = Vote.objects.filter(user=request.user).select_related( # type: ignore
        'election', 'position', 'candidate__user'
    ).order_by('-timestamp')
    # pylint: enable=no-member

    formatted_my_votes = []
    for vote in my_votes:
        formatted_my_votes.append({
            'candidate_name': f"{vote.candidate.user.first_name} {vote.candidate.user.last_name}",
            'position': vote.position.position_name,
            'election_title': vote.election.title,
            'timestamp': vote.timestamp
        })

    return render(request, 'student_portal/student_my_vote.html', {
        'my_votes': formatted_my_votes
    })

def student_update_profile(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('student_login')

    if request.method == 'POST':
        user = request.user
        
        try:
            # Handle profile picture upload via ImageField
            if 'profilePhoto' in request.FILES:
                user.photo_url = request.FILES['profilePhoto']

            # Update basic profile fields
            user.first_name = request.POST.get('firstname', user.first_name)
            user.last_name = request.POST.get('lastname', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.program = request.POST.get('program', user.program)
            
            # Handle year_level conversion to integer
            year_level_str = request.POST.get('year_level')
            if year_level_str:
                try:
                    user.year_level = int(year_level_str)
                except ValueError:
                    return JsonResponse({'success': False, 'message': "Year Level must be a valid number."}, status=400)
            else:
                user.year_level = None # Allow saving as NULL if blank
            
            # Handle password change
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password and password == confirm_password:
                user.set_password(password)
            elif password and password != confirm_password:
                return JsonResponse({'success': False, 'message': "Passwords do not match."}, status=400)

            user.save()
            
            # Return success JSON response
            return JsonResponse({
                'success': True,
                'message': "Profile updated successfully!",
                'photo_url': user.photo_url.url if user.photo_url else None
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'}, status=500)

    # For any non-POST requests, or if it falls through (which it shouldn't for a POST-only view),
    # return a 405 Method Not Allowed response.
    return JsonResponse({'success': False, 'message': "Method Not Allowed"}, status=405)

def handle_party_request(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        messages.error(request, 'Unauthorized. Please log in as a student.')
        return redirect('student_login')

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')

        # Debugging: Print received data
        # print(f"DEBUG: handle_party_request - request_id: {request_id}")
        # print(f"DEBUG: handle_party_request - action: {action}")
        # print(f"DEBUG: handle_party_request - CSRF_TOKEN: {request.POST.get('csrfmiddlewaretoken')}")

        try:
            party_request = PartyRequest.objects.get(id=request_id, requested_member=request.user) # pylint: disable=no-member
            if action == 'accept':
                party_request.status = 'accepted'
                party_request.save()
                request.user.partylist = party_request.party
                request.user.save()
                messages.success(request, 'Party request accepted!')
            elif action == 'reject':
                party_request.status = 'rejected'
                party_request.save()
                messages.info(request, 'Party request rejected.')
            else:
                messages.error(request, 'Invalid action.')
        except models.ObjectDoesNotExist: # type: ignore
            messages.error(request, 'Party request not found.')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    return redirect('student_profile') # Redirect back to the profile page

def student_party_request(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('student_login')
    
    party_exists = False
    party_data = None
    requested_party_members = []
    positions = []
    election_title = 'Unknown Election'
    is_finalized = False
    assigned_position_ids = []
    requested_member_ids = []
    all_members_accepted = False
    existing_requests_tuples = [] # New list to store (requested_member_id, position_id) tuples

    try:
        # Check if the user already has a party
        # pylint: disable=no-member
        party_data = PartyList.objects.filter(created_by=request.user).first() # type: ignore
        # pylint: enable=no-member

        # Fetch all positions for the forms and finalization check
        # pylint: disable=no-member
        positions = Position.objects.all().order_by('rank') # type: ignore
        # pylint: enable=no-member
        
        if party_data:
            party_exists = True
            is_finalized = party_data.is_finalized

            # Fetch requested party members if a party exists
            # pylint: disable=no-member
            requested_party_members = PartyRequest.objects.filter(party=party_data).select_related( # type: ignore
                'requested_member', 'position'
            ).order_by('-created_at')
            print(f"DEBUG: requested_party_members after fetch: {requested_party_members}") # Debugging
            # pylint: enable=no-member
            
            # Prepare data for template
            for req in requested_party_members:
                if req.position: # Ensure position is not None
                    assigned_position_ids.append(req.position.id)
                requested_member_ids.append(req.requested_member.id)

            # Check if all members are assigned and accepted for finalization
            all_members_accepted = True
            if positions: # Only check if positions exist
                for position in positions:
                    found_member = False
                    for member_req in requested_party_members:
                        if member_req.position == position and member_req.status == 'accepted':
                            found_member = True
                            break
                    if not found_member:
                        all_members_accepted = False
                        break
            else: # If no positions are defined, a party with no members can be finalized (e.g. for testing)
                all_members_accepted = True
                
            # Fetch election title
            if party_data.election:
                election_title = party_data.election.title

            # Fetch all existing requests by this party
            # pylint: disable=no-member
            all_party_requests = PartyRequest.objects.filter(party=party_data).values_list('requested_member__id', 'position__id') # type: ignore
            # pylint: enable=no-member
            existing_requests_tuples = [(str(req[0]), str(req[1])) for req in all_party_requests]
            
            # Automatically assign the logged-in user as President if they are the party creator
            # (This logic might need to be refined based on your `Position` model and election rules)
            # pylint: disable=no-member
            president_position = Position.objects.filter(position_name='President').first() # type: ignore
            if president_position and not PartyRequest.objects.filter( # type: ignore
                party=party_data, requested_member=request.user, position=president_position
            ).exists():
                try:
                    # pylint: disable=no-member
                    PartyRequest.objects.create( # type: ignore
                        party=party_data,
                        requester=request.user,
                        requested_member=request.user,
                        status='accepted',
                        position=president_position
                    )
                    # pylint: enable=no-member
                    # Refresh requested_party_members after adding President
                    # pylint: disable=no-member
                    requested_party_members = PartyRequest.objects.filter(party=party_data).select_related( # type: ignore
                        'requested_member', 'position'
                    ).order_by('-created_at')
                    # pylint: enable=no-member
                    # Update assigned_position_ids and requested_member_ids as well
                    assigned_position_ids.append(president_position.id)
                    requested_member_ids.append(request.user.id)
                    messages.success(request, "You have been automatically assigned as President of your party.")
                except IntegrityError:
                    # Handle cases where the President might already be assigned by other means
                    pass
            
            # Attach assigned member to each position for display in finalize party section
            for position in positions:
                position.assigned_member = None
                for member_req in requested_party_members:
                    if member_req.position == position:
                        position.assigned_member = member_req.requested_member
                        position.assigned_member.status = member_req.status # Attach status for template
                        print(f"DEBUG: Assigned {position.position_name} to {position.assigned_member.first_name}") # Debugging
                        break
                    else:
                        print(f"DEBUG: No match for position {position.position_name} with member_req position {member_req.position}") # Debugging

    except Exception as e:
        messages.error(request, f"Error fetching party data: {e}")
        # Log the error for debugging
        logger = logging.getLogger(__name__)
        logger.error("Error in student_party_request: %s", e)
    
    # Fetch available elections for creating a party
    # pylint: disable=no-member
    available_elections = Election.objects.filter(status__in=['scheduled', 'ongoing']) # type: ignore
    # pylint: enable=no-member

    context = {
        'party_exists': party_exists,
        'party_data': party_data,
        'requested_party_members': requested_party_members,
        'positions': positions,
        'election_title': election_title,
        'is_finalized': is_finalized,
        'assigned_position_ids': assigned_position_ids,
        'requested_member_ids': requested_member_ids,
        'all_members_accepted': all_members_accepted,
        'search_results': request.session.get('search_results', []),
        'available_elections': available_elections,
        'existing_requests_tuples': existing_requests_tuples, # Pass to template
    }
    # Clear search results from session after displaying
    if 'search_results' in request.session:
        del request.session['search_results']
    
    return render(request, 'student_portal/student_party_request.html', context)

def student_create_party(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('student_login')
    
    if request.method == 'POST':
        party_name = request.POST.get('party_name')
        election_id = request.POST.get('election_id')
        mission = request.POST.get('mission')
        vision = request.POST.get('vision')
        description = request.POST.get('description')
        
        try:
            # Check if the user already has a party
            # pylint: disable=no-member
            existing_party = PartyList.objects.filter(created_by=request.user).first() # type: ignore
            # pylint: enable=no-member
            if existing_party:
                messages.error(request, "You have already created a party.")
                return redirect('student_party_request')
            
            # pylint: disable=no-member
            election = Election.objects.get(id=election_id) # type: ignore
            # pylint: enable=no-member

            # Create the party
            # pylint: disable=no-member
            new_party = PartyList.objects.create(
                party_name=party_name,
                description=description,
                mission=mission,
                vision=vision,
                created_by=request.user,
                election=election,
                status='pending' # Initial status
            ) # type: ignore
            # pylint: enable=no-member
            
            # Automatically assign the creator as President
            # pylint: disable=no-member
            president_position = Position.objects.filter(position_name='President').first() # type: ignore
            if president_position:
                PartyRequest.objects.create( # type: ignore
                    party=new_party,
                    requester=request.user,
                    requested_member=request.user,
                    status='accepted',
                    position=president_position
                )
                # Update the user's partylist field
                request.user.partylist = new_party # type: ignore
                request.user.save()
                messages.success(request, "You have been automatically assigned as President of your party.")
            
            messages.success(request, 'Party created successfully!')
        except Exception as e:
            messages.error(request, f'Error creating party: {e}')
        
    return redirect('student_party_request')

def search_students(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('student_login')

    if request.method == 'POST':
        search_term = request.POST.get('search_term')
        if search_term:
            # pylint: disable=no-member
            results = CustomUser.objects.filter(
                role='student',
                student_id__icontains=search_term
            ) | CustomUser.objects.filter(
                role='student',
                first_name__icontains=search_term
            ) | CustomUser.objects.filter(
                role='student',
                last_name__icontains=search_term
            )
            # Exclude current user from search results
            results = results.exclude(id=request.user.id)
            # Exclude members already in this user's party
            if request.user.partylist:
                results = results.exclude(partylist=request.user.partylist) # type: ignore
            # Exclude members for whom a party request has already been sent by the current user's party
            if request.user.partylist:
                # pylint: disable=no-member
                existing_requested_member_ids = PartyRequest.objects.filter(
                    party=request.user.partylist
                ).values_list('requested_member__id', flat=True) # type: ignore
                # pylint: enable=no-member
                results = results.exclude(id__in=list(existing_requested_member_ids)) # type: ignore
            
            # pylint: enable=no-member

            # Store results in session
            request.session['search_results'] = list(results.values('id', 'first_name', 'last_name', 'program'))
            # Convert UUIDs to strings for JSON serialization
            for res in request.session['search_results']:
                res['id'] = str(res['id'])
        else:
            request.session['search_results'] = []
    
    return redirect('student_party_request')

def send_member_request(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('student_login')

    if request.method == 'POST':
        requested_member_id = request.POST.get('requested_member_id')
        position_id = request.POST.get('position_id')
        party_id = request.POST.get('party_id') # Get party_id from hidden input

        # Add print statements for debugging
        print(f"DEBUG: send_member_request - requested_member_id: {requested_member_id}")
        print(f"DEBUG: send_member_request - position_id: {position_id}")
        print(f"DEBUG: send_member_request - party_id: {party_id}")

        try:
            # pylint: disable=no-member
            party = PartyList.objects.get(id=party_id, created_by=request.user) # type: ignore
            requested_member = CustomUser.objects.get(id=requested_member_id) # type: ignore
            position = Position.objects.get(id=position_id) # type: ignore
            # pylint: enable=no-member

            # Check if a request already exists for this member and position in this party
            # pylint: disable=no-member
            existing_request = PartyRequest.objects.filter(
                party=party,
                requested_member=requested_member,
                position=position
            ).first() # type: ignore
            # pylint: enable=no-member
            
            if existing_request:
                messages.warning(request, f"{requested_member.first_name} is already requested for {position.position_name}.")
            else:
                # Create the party request
                PartyRequest.objects.create( # pylint: disable=no-member
                    party=party,
                    requester=request.user,
                    requested_member=requested_member,
                    position=position,
                    status='pending'
                )
                messages.success(request, f'Request sent to {requested_member.first_name} {requested_member.last_name} for {position.position_name}!')
        except PartyList.DoesNotExist: # type: ignore
            messages.error(request, "Party not found or you are not the creator.")
        except CustomUser.DoesNotExist: # type: ignore
            messages.error(request, "Requested member not found.")
        except Position.DoesNotExist: # type: ignore
            messages.error(request, "Position not found.")
        except Exception as e:
            messages.error(request, f'Error sending request: {e}')
        
    return redirect('student_party_request')

def finalize_party(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        return redirect('student_login')

    if request.method == 'POST':
        party_id = request.POST.get('party_id')
        try:
            # pylint: disable=no-member
            party = PartyList.objects.get(id=party_id, created_by=request.user) # type: ignore
            # pylint: enable=no-member

            # Check if all required positions are filled and accepted
            # Fetch all positions from the database
            # pylint: disable=no-member
            all_positions = Position.objects.all() # type: ignore
            # pylint: enable=no-member
            
            # Fetch all accepted requests for this party
            # pylint: disable=no-member
            accepted_requests = PartyRequest.objects.filter(party=party, status='accepted') # type: ignore
            # pylint: enable=no-member
            
            # Create a set of position IDs that are filled and accepted
            filled_positions = set(req.position.id for req in accepted_requests if req.position)
            
            all_required_filled = True
            for position in all_positions:
                # Assuming all positions are 'required' for party finalization
                if position.id not in filled_positions:
                    all_required_filled = False
                    break

            if all_required_filled:
                party.status = 'finalized'
                party.is_finalized = True
                party.save()
                messages.success(request, "Party finalized successfully! It will now be reviewed.")
            else:
                messages.error(request, "Cannot finalize: Not all positions have accepted members.")

        except PartyList.DoesNotExist: # type: ignore
            messages.error(request, "Party not found or you are not the creator.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
    
    return redirect('student_party_request')

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

    @rate_limit('register', limit=3, period=60)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ProtectedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({'message': f'Hello, {request.user.first_name}! This is a protected route.'})

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all() if hasattr(Position, 'objects') else None
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated]

class PartyListViewSet(viewsets.ModelViewSet):
    queryset = PartyList.objects.all() if hasattr(PartyList, 'objects') else None
    serializer_class = PartyListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class ElectionViewSet(viewsets.ModelViewSet):
    queryset = Election.objects.all() if hasattr(Election, 'objects') else None
    serializer_class = ElectionSerializer
    permission_classes = [permissions.IsAuthenticated]

router = DefaultRouter()
router.register(r'positions', PositionViewSet, basename='position')
