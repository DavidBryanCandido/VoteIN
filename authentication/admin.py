from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Position, PartyList, Election, PartyRequest, Candidate, AuditLog, Vote

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('student_id', 'email', 'first_name', 'last_name', 'role', 'status')
    search_fields = ('student_id', 'email', 'first_name', 'last_name')
    ordering = ('student_id',)
    
    fieldsets = (
        (None, {'fields': ('student_id', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'photo_url', 'course', 'program', 'year_level')}),
        ('Party Info', {'fields': ('partylist',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role', 'status')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('student_id', 'email', 'password1', 'password2'),
        }),
    )

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('position_name', 'program', 'rank', 'created_at')
    search_fields = ('position_name', 'description')
    list_filter = ('program',)

@admin.register(PartyList)
class PartyListAdmin(admin.ModelAdmin):
    list_display = ('party_name', 'party_leader_name', 'election', 'status', 'is_finalized')
    search_fields = ('party_name', 'party_leader_name', 'description')
    list_filter = ('status', 'is_finalized', 'election')

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'status', 'created_by')
    search_fields = ('title', 'description')
    list_filter = ('status',)

@admin.register(PartyRequest)
class PartyRequestAdmin(admin.ModelAdmin):
    list_display = ('party', 'requester', 'requested_member', 'position', 'status')
    list_filter = ('status', 'party', 'position')
    search_fields = ('requester__email', 'requested_member__email', 'party__party_name')

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('user', 'election', 'position', 'partylist', 'status')
    list_filter = ('status', 'election', 'position', 'partylist')
    search_fields = ('user__email', 'student_id', 'platform')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    list_filter = ('action',)
    search_fields = ('user__email', 'action', 'details')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('election', 'candidate', 'position', 'user', 'timestamp')
    list_filter = ('election', 'position')
    search_fields = ('user__email', 'candidate__user__email')
