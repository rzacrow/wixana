from django.contrib import admin
from .models import Attendance, AttendanceDetail, Role, RunType, Guild, CutInIR, CutDistributaion, CurrentRealm
from django.db import models
from django.conf import settings
from django.db.models import Sum
from accounts.models import Wallet, Transaction, Notifications, Team, TeamDetail, Realm, Alt as booster_alt

from django.utils import timezone
from django import forms
from unfold.admin import ModelAdmin,TabularInline, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.forms import UserCreationForm


class GuildInline(StackedInline):
    model = Guild
    readonly_fields = ['total', 'booster', 'gold_collector', 'guild_bank']
    extra = 1
    fieldsets = [(
            "",
            {
                'fields' : [('in_house_customer_pot', 'refunds'), ('total', 'booster'), ('gold_collector', 'guild_bank')]
            }
        )
    ]

    def save_model(self, request, obj, form, change):
        obj.total += obj.in_house_customer_pot
        obj.total -= obj.refunds
        obj.save()
        super().save_model(request, obj, form, change)



@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    @admin.display(description="Date Time")
    def created_show(self, obj):
        return obj.created.strftime("%Y-%m-%d %H:%M")
    
    @admin.display(description="User")
    def user_requester(self, obj):
        if obj.alt:
            return obj.alt
        return obj.requester
    
    list_display = ['user_requester', 'status', 'created_show', 'currency', 'amount']
    readonly_fields = ['created_show']
    fieldsets = [(
            None,
            {
                'fields' : [('requester', 'created_show'), ('currency', 'amount'), ('status', 'caption'), ('card_detail', 'alt'), 'paid_date']
            }
        )
    ]

    ordering = ['status', '-created']
    search_fields = ["id"]
    search_help_text = ["Search in id"]


    list_filter_submit = True
    list_filter = ['status', 'created']

    @admin.action(description="Change selected transactions status to 'Paid'")
    def change_to_paid(self, request, queryset):
        queryset.update(status='PAID')

    actions = ['change_to_paid']



    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            Notifications.objects.create(send_to=obj.requester, title="Payment status changed", caption=f"Your payment request was changed to {obj.status} with code {obj.id}. This may take some time")
            if 'paid_date' not in form.changed_data:
                obj.paid_date = timezone.now()
                obj.save()
        super().save_model(request, obj, form, change)


class CutDistributaionInline(StackedInline):
    model = CutDistributaion
    list_display = ['total_guild', 'community']
    readonly_fields = ['total_guild', 'community']

class AttendanceDetailInline(TabularInline):
    model = AttendanceDetail
    extra = 2


    fieldsets = (
        (None, {
            "fields": [
                ('role', 'alt'), 'player', 'missing_boss', 'cut'   
            ],
        }),
    )

class CurrentRealmInline(TabularInline):
    model = CurrentRealm
    extra = 1


@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(AttendanceAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['run_notes', 'characters_name']:
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield
    
    @admin.display(description="Date Created")
    def date_time_show(self, obj):
        return obj.date_time.strftime("%Y-%m-%d %H:%M")

    list_display = ["date_time_show", 'status', 'run_notes', 'total_pot']
    list_filter = ['status', 'date_time']

    ordering = ('status', '-date_time')

    inlines = [
        CutDistributaionInline,
        GuildInline,
        AttendanceDetailInline,
        CurrentRealmInline,
    ]

    fieldsets = [(
            "Attendance",
            {
                'fields' : [('date_time'), ('run_type', 'status'), ('total_pot', 'boss_kill'), 'characters_name', 'run_notes']
            }
        )
    ]

    readonly_preprocess_fields = {
        "model_field_name": "html.unescape",
        "other_field_name": lambda content: content.strip(),
    }


    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    """def add_team_member()
    actions = list()
    teams = Team.objects.filter()
    if teams:
        for team in teams:
            actions.append('add_team_to_attendance')
            @admin.action(description=f"Add team {team.name} to selected attendance")
            def add_team_to_attendance(self, request, queryset, team=team):
                team_details = TeamDetail.objects.filter(team=team)
                role = Role.objects.get(name="Booster")
                for td in team_details:
                    for query in queryset:
                        AttendanceDetail.objects.create(attendane=query, player=td.player, role=role)"""


    def change_view(self, request, object_id, form_url="", extra_context=None):
        try:
            obj = Attendance.objects.get(id=object_id)
            a_rt = obj.run_type
            gd = Guild.objects.get_or_create(attendance=obj)
            gd = gd[0]
            total = (((int(a_rt.guild * obj.total_pot)) // 100) + gd.in_house_customer_pot) - gd.refunds
            gd.total = total
            gd.booster = (int(95 * total)) // 100
            gd.gold_collector = (int(2 * total)) // 100
            gd.guild_bank = (int(3 * total)) // 100
            gd.save()

            boosters = AttendanceDetail.objects.filter(attendane=obj)
            if boosters:
                for booster in boosters:
                    booster.multiplier = (((obj.boss_kill - booster.missing_boss) / obj.boss_kill) * booster.role.ratio)
                    booster.save()


                sum_multiplier = boosters.aggregate(Sum('multiplier'))['multiplier__sum']
                cut_per_booster = gd.booster // sum_multiplier
                for booster in boosters:
                    booster.cut = int(cut_per_booster * booster.multiplier)
                    booster.save()
                
        except:
            pass

        else:
            cutdist = CutDistributaion.objects.get_or_create(attendance=obj, total_guild=gd)
            cutdist = cutdist[0]
            cutdist.community = ((int(a_rt.community * obj.total_pot)) // 100)
            cutdist.save()

        finally:
            return super().change_view(request, object_id, form_url, extra_context)



    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if not isinstance(inline, (CutDistributaionInline,GuildInline)) or obj is not None:
                yield inline.get_formset(request, obj), inline

    def save_model(self, request, obj, form, change):
        try:
            a_rt = obj.run_type
            gd = Guild.objects.get_or_create(attendance=obj)
            gd = gd[0]
            total = (((int(a_rt.guild * obj.total_pot)) // 100) + gd.in_house_customer_pot) - gd.refunds
            gd.total = total
            gd.booster = (int(95 * total)) // 100
            gd.gold_collector = (int(2 * total)) // 100
            gd.guild_bank = (int(3 * total)) // 100
            gd.save()
        except:
            pass

        else:
            cutdist = CutDistributaion.objects.get_or_create(attendance=obj, total_guild=gd)
            cutdist = cutdist[0]
            cutdist.community = ((int(a_rt.community * obj.total_pot)) // 100)
            cutdist.save()

        finally:
            try:
                characters = obj.characters_name
                if characters:
                    characters = characters.split('\r\n')

                    if characters:
                            for car in characters:
                                car = car.split(',')
                                realm = Realm.objects.get(name=car[1])
                                alt = booster_alt.objects.get(name=car[0], realm=realm)
                                
                                if alt.status == 'Verified':
                                    is_alt_exist = AttendanceDetail.objects.filter(attendane=obj, player=alt.player, alt=alt)
                                    if not is_alt_exist:
                                        AttendanceDetail.objects.create(attendane=obj, player=alt.player, alt=alt)
                else:
                    a_d = AttendanceDetail.objects.filter(attendane=obj)
                    if a_d:
                        for ad in a_d:
                            if ad.alt:
                                ad.delete()
            except:
                    a_d = AttendanceDetail.objects.filter(attendane=obj)
                    if a_d:
                        for ad in a_d:
                            if ad.alt:
                                ad.delete()
                    pass

            if obj.status == 'C':
                if obj.paid_status == False:
                    boosters = AttendanceDetail.objects.filter(attendane=obj)
                    if boosters:
                        for b in boosters:
                            wallet = Wallet.objects.get_or_create(player=b.player)
                            wallet[0].amount += b.cut
                            wallet[0].save()
                    obj.paid_status = True
                    obj.save()
                    super().save_model(request, obj, form, change)

            else:
                super().save_model(request, obj, form, change)

                boosters = AttendanceDetail.objects.filter(attendane=obj)
                if boosters:
                    for booster in boosters:
                        booster.multiplier = (((obj.boss_kill - booster.missing_boss) / obj.boss_kill) * booster.role.ratio)
                        print(booster.player.username, booster.multiplier)
                        booster.save()


                    sum_multiplier = boosters.aggregate(Sum('multiplier'))['multiplier__sum']
                    cut_per_booster = gd.booster // sum_multiplier
                    for booster in boosters:
                        booster.cut = int(cut_per_booster * booster.multiplier)
                        booster.save()


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ['name', 'ratio']

@admin.register(RunType)
class RunTypeAdmin(ModelAdmin):
    list_display = ['name', 'guild', 'community']
    fieldsets = (
        (None, {
            "fields": (
                'name',
                'guild',
                'community',
            ),
        }),
    )
    

@admin.register(CutInIR)
class CutInIR(ModelAdmin):
    list_display = ['amount', 'date_time']