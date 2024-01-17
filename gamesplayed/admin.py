from django.contrib import admin
from .models import Attendance, AttendanceDetail, Role, RunType, Guild, CutInIR, CutDistributaion, CurrentRealm, Cycle, Payment
from django.db import models
from django.conf import settings
from django.db.models import Sum
from accounts.models import Wallet, Transaction, Notifications, Realm, Alt as booster_alt
from django.contrib import messages
from django.utils import timezone
from django import forms
from unfold.admin import ModelAdmin,TabularInline, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.forms import UserCreationForm
from django.contrib.contenttypes.models import ContentType

from django.conf.urls.static import static

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
    
    @admin.display(description="Amount")
    def amount_if_cut(self, obj):
        if obj.currency == 'CUT':
            if obj.amount >= 1000:
                return f"{obj.amount // 1000} K"
        return obj.amount
    
    list_display = ['user_requester', 'status', 'created_show', 'currency', 'amount_if_cut']
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


    def change_paid(self, request, objects):
        for obj in objects:
            Notifications.objects.create(send_to=obj.requester, title="Payment status changed", caption=f"Your payment request was changed to {obj.status} with code {obj.id}. This may take some time")
            obj.paid_date = timezone.now().today()
            obj.save()

    @admin.action(description="Change selected transactions status to 'Paid'")
    def change_to_paid(self, request, queryset):
        list_ids = queryset.values_list('id', flat=True)
        objects = Transaction.objects.filter(id__in=list_ids)
        self.change_paid(request=request, objects=objects)
        queryset.update(status='PAID')

    actions = ['change_to_paid']



    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            if obj.status == 'PAID':
                self.change_paid(request=request, objects=[obj])
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
                ('role', 'player'), 'alt', 'missing_boss', 'cut'   
            ],
        }),
    )

class CurrentRealmInline(TabularInline):
    model = CurrentRealm
    extra = 1


@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['total_pot'].widget.attrs['placeholder'] = "Entered an integer"
        return form
    
    
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
                'fields' : [('date_time'), ('run_type', 'status'), 'cycle', ('total_pot', 'boss_kill'), 'characters_name', 'run_notes']
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

    def if_status_closed(self, request, objects):
        for obj in objects:
                try:
                    if obj.paid_status == False:
                        boosters = AttendanceDetail.objects.filter(attendane=obj)
                        if boosters:
                            for b in boosters:
                                wallet = Wallet.objects.get_or_create(player=b.player)
                                wallet[0].amount += b.cut
                                wallet[0].save()
                        obj.paid_status = True
                        obj.save()
                except:
                    pass

    @admin.action(description="change status to 'Closed'")
    def change_status_to_closed(self, request, queryset):
        list_ids = queryset.values_list('id', flat=True)
        objects = Attendance.objects.filter(id__in=list_ids)
        self.if_status_closed(request=request, objects=objects)
        queryset.update(status='C')

    actions = [
        'change_status_to_closed'
    ]

    """def add_team_member()
    actions = list()
    teams = Team.objects.filter()
    if teams:
        for team in teams:
            actions.append('add_team_to_attendance')
            @admin.action(description=f"Add team {team.name} to selected attendance")
            def add_team_to_attendance(self, request, queryset, team=team):
                team_detabjects.filter(team=team)
                role = Role.objects.get(name="Booster")
                for td in team_details:
                    for query in queryset:
                        AttendanceDetail.objects.create(attendane=query, player=td.player, role=role)"""


    def change_view(self, request, object_id, form_url="", extra_context=None):
            error_to_add_flag = False
            try:
                obj = Attendance.objects.get(id=object_id)
                characters = obj.characters_name
                if characters:
                    characters = characters.split(',')

                    if characters:
                            un_verified_alts_flag = False
                            un_verified_alts = list()
                            error_to_add_list = list()
                            for car in characters:
                                car = car.split('-')
                                try:
                                    realm = Realm.objects.get(name=car[1])
                                    alt = booster_alt.objects.get(name=car[0], realm=realm)
                                except:
                                    error_to_add_flag = True
                                    error_to_add_list.append(car)
                                else:
                                    if alt.status == 'Verified':
                                        is_alt_exist = AttendanceDetail.objects.filter(attendane=obj, player=alt.player, alt=alt)
                                        if not is_alt_exist:
                                            AttendanceDetail.objects.create(attendane=obj, player=alt.player, alt=alt)
                                    else:
                                        un_verified_alts_flag = True
                                        un_verified_alts.append(car)
                            if un_verified_alts_flag:
                                messages.add_message(request, messages.WARNING, message=f'Found "alts" that were not validated{un_verified_alts}')
            except:
                    pass
            
            if error_to_add_flag:
                messages.add_message(request, messages.WARNING, message=f'{len(error_to_add_list)} Users we could not add{error_to_add_list}')

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

            return super().change_view(request, object_id, form_url, extra_context)



    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if not isinstance(inline, (CutDistributaionInline,GuildInline)) or obj is not None:
                yield inline.get_formset(request, obj), inline

    def save_model(self, request, obj, form, change):
        if obj.cycle.status == 'C':
            if obj.status == "A":
                messages.add_message(request, messages.ERROR, "You can not add attendance in 'Closed' cycle ")
                return 
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
            if obj.status == 'C':
                self.if_status_closed(request=request, objects=[obj])
            else:
                super().save_model(request, obj, form, change)

                boosters = AttendanceDetail.objects.filter(attendane=obj).order_by('id')
                if boosters:
                    for booster in boosters:
                        booster.multiplier = (((obj.boss_kill - booster.missing_boss) / obj.boss_kill) * booster.role.ratio)
                        booster.save()


                    sum_multiplier = boosters.aggregate(Sum('multiplier'))['multiplier__sum']
                    cut_per_booster = gd.booster // sum_multiplier
                    for booster in boosters:
                        booster.cut = int(cut_per_booster * booster.multiplier)
                        booster.save()
                    
                    if boosters.count() >= 2: 
                        leader_role = Role.get_default_raidleader()
                        assistant_role = Role.get_default_assistant()
                        boosters[0].role = leader_role
                        boosters[1].role = assistant_role
                        boosters[0].save()
                        boosters[1].save()


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
    @admin.display(description="Defined in")
    def date_time_show(self, obj):
        return obj.date_time.strftime("%Y-%m-%d %H:%M")
    list_display = ['amount', 'date_time_show']

@admin.register(Cycle)
class CycleAdmin(ModelAdmin):
    @admin.display(description="Start Date")
    def start_date_display(self, obj):
        try:
            return obj.start_date.strftime('%Y-%m-%d %H:%M')
        except:
            return None
    
    @admin.display(description="End Date")
    def end_date_display(self, obj):
        try:
            return obj.end_date.strftime('%Y-%m-%d %H:%M')
        except:
            return None
        
    list_display = ['start_date_display', 'end_date_display', 'status']
    ordering = ['-start_date']

    list_filter = [
        'start_date',
        'end_date',
        'status',
    ]
    list_filter_submit = True  # Submit button at the bottom of the filter

    def closed_status(self, request, objects):
        for obj in objects:
                if obj.status == 'C':
                    continue
                attendances = Attendance.objects.filter(cycle=obj)
                if attendances:
                    for at in attendances:
                        boosters = AttendanceDetail.objects.filter(attendane=at)
                        if at.status == 'A':
                            at.status = 'C'
                            if at.paid_status == False:
                                if boosters:
                                    for b in boosters:
                                        wallet = Wallet.objects.get_or_create(player=b.player)
                                        wallet[0].amount += b.cut
                                        wallet[0].save()
                                    at.paid_status = True                                    
                            at.save()
                        if boosters:
                            for booster in boosters:
                                string = f"{booster.alt}:{booster.cut}:{booster.attendane.date_time.strftime("%Y-%m-%d %H %M")}"
                                Payment.objects.create(cycle=obj, detail=booster, string=string)

    @admin.action(description="Change to 'Close'")
    def change_status_to_close(self, request, queryset):
        list_ids = queryset.values_list('id', flat=True)
        objects = Cycle.objects.filter(id__in=list_ids)
        self.closed_status(request=request, objects=objects)
        queryset.update(status='C')

    actions = [
        'change_status_to_close'
    ]

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            if obj.status == 'C':
                self.closed_status(request=request, objects=[obj])
        super().save_model(request, obj, form, change)



@admin.register(Payment)
class PaymentAdmin(ModelAdmin):

    @admin.display(description="User")
    def user_display(self, obj):
        return obj.detail.player
    
    @admin.display(description="Payment character")
    def payment_character(self, obj):
        try:
            return obj.payment_character
        except:
            return "there aren't any payment character"
    
    @admin.display(description="Cut")
    def booster_cut(self, obj):
        if obj.detail.cut >= 1000:
            amount_per_thousand = obj.detail.cut // 1000
            return f"{amount_per_thousand} K"
        return obj.detail.cut
    
    list_display = ['user_display', 'payment_character', 'booster_cut', 'string','is_paid']
    ordering = ['cycle__end_date']

    def is_paid_change(self, objects, request):
        for obj in objects:
            try:
                wallet = Wallet.objects.get(player=obj.detail.player)
            except:
                messages.add_message(request, messages.ERROR, message=f"There was a problem in deducting the payment amount from user {obj.detail.player} wallet")
                obj.is_paid = False
                obj.save()
            else:
                wallet.amount -= int(obj.detail.cut)
                wallet.save()
                Transaction.objects.create(requester=obj.detail.player, status='PAID', paid_date=timezone.now().today(), amount=obj.detail.cut, currency='CUT', alt=obj.detail.payment_character)


    @admin.action(description="Paid status to 'True'")
    def change_to_ispaid(self, request, queryset):
        list_ids = queryset.values_list('id', flat=True)
        objects = Payment.objects.filter(id__in=list_ids)
        self.is_paid_change(objects=objects, request=request)
        queryset.update(is_paid=True)

    actions = [
        'change_to_ispaid'
    ]

    def save_model(self, request, obj, form, change):
        if 'is_paid' in form.changed_data:
            if obj.is_paid == True:
                self.is_paid_change(objects=[obj], request=request)

        super().save_model(request, obj, form, change)
                

