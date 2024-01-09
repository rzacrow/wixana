from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from .models import User as um, Team, TeamDetail, Alt, Realm, Wallet, Notifications
from django.db import models
from unfold.admin import ModelAdmin,TabularInline, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.forms import UserCreationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

# Register your models here.
from django.forms.models import BaseInlineFormSet


admin.site.unregister(Group)
@admin.register(Realm)
class Realm(ModelAdmin):
    # Preprocess content of readonly fields before render
    readonly_preprocess_fields = {
        "model_field_name": "html.unescape",
        "other_field_name": lambda content: content.strip(),
    }

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }

class WalletInline(StackedInline):
    model = Wallet

    readonly_fields = ['card_number', 'IR', 'card_full_name']
    # Preprocess content of readonly fields before render
    readonly_preprocess_fields = {
        "model_field_name": "html.unescape",
        "other_field_name": lambda content: content.strip(),
    }


class AltInline(StackedInline):
    model = Alt
    # Preprocess content of readonly fields before render
    readonly_preprocess_fields = {
        "model_field_name": "html.unescape",
        "other_field_name": lambda content: content.strip(),
    }
    extra = 1

@admin.register(Alt)
class AltAdmin(ModelAdmin):
    list_display = ['name','player', 'status']
    ordered = ['status']

    actions = [
        'change_alts_verified',
        'change_alts_rejected'
    ]
    @admin.action(description="Change selected alts to 'Verified'")
    def change_alts_verified(self, request, queryset):
        queryset.update(status='Verified')

    @admin.action(description="Change selected alts to 'Rejected'")
    def change_alts_rejected(self, request, queryset):
        queryset.update(status='Rejected')


    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            Notifications.objects.create(send_to=obj.player, title="Alt status", caption=f"Your Alt {obj.name} status changed by admin")
        super().save_model(request, obj, form, change)




def get_user_permission(user):
    if user.is_superuser:
        return Permission.objects.all()
    return user.user_permissions.all() | Permission.objects.filter(group__user=user)

def add_user_permission():
    admin_perm = Permission.objects.exclude(content_type__app_label='accounts', codename='add_user')
    admin_perm = admin_perm.exclude(content_type__app_label='accounts', codename='change_user')
    admin_perm = admin_perm.exclude(content_type__app_label='accounts', codename='delete_user')

    admin_perm = admin_perm.exclude(content_type=ContentType.objects.get(model='session'))
    return admin_perm


@admin.register(um)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    add_form = UserCreationForm

    def changeform_view(self, request, obj, form, change):
        if request.user.user_type != 'O':
            raise PermissionDenied()
        
        user = um.objects.get(id=obj)
        if user:
            if user.user_type != 'U':
                self.inlines = [
                    AltInline,
                    WalletInline
                ]
            else:
                self.inlines = [
                ]

        ONE_MONTH = 30 * 24 * 60 * 60
        expiry = getattr(settings, "KEEP_LOGGED_DURATION", ONE_MONTH)
        request.session.set_expiry(expiry)
        return super().changeform_view(request, obj, form, change)



    list_display = ['username', 'user_type', 'last_login']
    fieldsets = [
        (
            "User info",
            {
                'fields' : [('username', 'user_type'), 'avatar', ('email', 'discord_id'), ('last_login', 'date_joined'), ]
            }
        )
    ]
    search_fields = ["username"]
    search_help_text = ["Search in username"]
    
    readonly_fields = ['last_login', 'date_joined']
    # Preprocess content of readonly fields before render
    readonly_preprocess_fields = {
        "model_field_name": "html.unescape",
        "other_field_name": lambda content: content.strip(),
    }


    # Display submit button in filters
    list_filter_submit = True
    list_filter = ['user_type']
    actions = ['change_user_to_booster']
    actions_selection_counter = True
    
    # Custom actions
    actions_list = []  # Displayed above the results list
    actions_row = []  # Displayed in a table row in results list
    actions_detail = []  # Displayed at the top of for in object detail
    actions_submit_line = []  # Displayed near save in object detail

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }

    @admin.action(description="Change access to booster level")
    def change_user_to_booster(self, request, queryset):
        queryset.update(user_type="B")

    def get_ordering(self, request):
        return ["username"]
    
    def save_model(self, request, obj, form, change):        
        if obj.user_type == 'B':
            try:
                get_wallet = Wallet.objects.get(player__username=obj.username)
            except:
                Wallet.objects.create(player=obj, card_full_name='---')
        if 'user_type' in form.changed_data:
            if request.user.user_type == 'O':
                if obj.user_type == 'A':
                    obj.is_staff = True
                    obj.save()
                elif (obj.user_type == 'B') or (obj.user_type == 'U'):
                    obj.is_staff = False
                    obj.is_superuser = False
                    obj.save()
                elif obj.user_type == 'O':
                    obj.is_staff = True
                    obj.is_superuser = True
                    obj.save()
            else:
                raise PermissionDenied()
            Notifications.objects.create(send_to=obj, title="Change User Permission", caption=f"your profile permission changed to the '{obj.user_type}' level by Owner")
        super().save_model(request, obj, form, change)


class TeamDetailInline(TabularInline):
    model = TeamDetail
    extra = 1
    
@admin.register(Team)
class TeamAdmin(ModelAdmin):
    list_display = ['name', 'status']

    inlines = [
        TeamDetailInline
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.status == 'Rejected':
            leader = TeamDetail.objects.filter(team=obj).first()
            Team.objects.get(id=obj.id).delete()
            Notifications.objects.create(send_to=leader.player, title="Your team has been deleted by the admin")
