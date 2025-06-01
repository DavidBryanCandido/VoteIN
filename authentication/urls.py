from django.urls import path, include
from .views import (
    RegisterView, 
    ProtectedView, 
    PositionViewSet, 
    PartyListViewSet, 
    ElectionViewSet,
    student_register,
    student_login,
    student_dashboard,
    student_logout,
    student_profile,
    student_all_elections,
    student_my_vote,
    student_update_profile,
    handle_party_request,
    student_party_request,
    student_create_party,
    search_students,
    send_member_request,
    finalize_party,
    admin_login,
    admin_dashboard,
    admin_logout,
    admin_create_election,
    admin_manage_party,
    admin_manage_student,
    admin_manage_result,
    admin_update_election,
    admin_update_student_status,
    clear_admin_welcome_message
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'positions', PositionViewSet, basename='position')
router.register(r'partylists', PartyListViewSet, basename='partylist')
router.register(r'elections', ElectionViewSet, basename='election')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('', include(router.urls)),
    path('student/register/', student_register, name='student_register'),
    path('student/register/submit/', student_register, name='register_submit'),
    path('student/login/', student_login, name='student_login'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('student/logout/', student_logout, name='student_logout'),
    path('student/profile/', student_profile, name='student_profile'),
    path('student/elections/', student_all_elections, name='student_all_elections'),
    path('student/my-votes/', student_my_vote, name='student_my_vote'),
    path('student/profile/update/', student_update_profile, name='student_update_profile'),
    path('student/party-request/handle/', handle_party_request, name='handle_party_request'),
    path('student/party-request/', student_party_request, name='student_party_request'),
    path('student/party-request/create/', student_create_party, name='student_create_party'),
    path('student/party-request/search-students/', search_students, name='search_students'),
    path('student/party-request/send-request/', send_member_request, name='send_member_request'),
    path('student/party-request/finalize/', finalize_party, name='finalize_party'),
    path('admin-login/', admin_login, name='admin_login_custom'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/logout/', admin_logout, name='admin_logout'),
    path('admin/elections/create/', admin_create_election, name='admin_create_election'),
    path('admin/parties/manage/', admin_manage_party, name='admin_manage_party'),
    path('admin/students/manage/', admin_manage_student, name='admin_manage_student'),
    path('admin/students/update-status/', admin_update_student_status, name='admin_update_student_status'),
    path('admin/elections/<uuid:election_id>/manage-result/', admin_manage_result, name='admin_manage_result'),
    path('admin/elections/update/', admin_update_election, name='admin_update_election'),
    path('admin/clear-welcome-message/', clear_admin_welcome_message, name='clear_admin_welcome_message'),
]