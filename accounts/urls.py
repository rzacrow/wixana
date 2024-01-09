from django.urls import path
from .views import SignupDiscord, Signup, Dashboard, Login, Logout, CreateTeam, LeftTheTeam, TeamDetailLink, JoinTeamResponse, SeenNotif, WalletUpdateDetail
from .views import InviteUser, CheckPassword, ResetPassword, RemoveTeamMember, AskingMoney, ForgetPassword, InviteUserResponse, PositionMemberTeam, RemoveAlts, RemoveAltsResponse


urlpatterns = [
    path('signup/', Signup.as_view(), name='signup'),
    path('signup/discord/response/', SignupDiscord.as_view(), name='discord_response'),
    path('', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),

    path('forgetpassword/', ForgetPassword.as_view(), name='forgetpassword'),
    path('checkpassword/', CheckPassword.as_view(), name='checkpassword'),
    path('resetpassword/', ResetPassword.as_view(), name='resetpassword'),

    #Team urls
    path('dashboard/team/create/', CreateTeam.as_view(), name='create_team'),
    path('dashboard/team/left/<int:team_pk>/', LeftTheTeam.as_view(), name='left_the_team'),
    path('dashboard/team/<str:team_name>/<int:team_pk>/', TeamDetailLink.as_view(), name='team_detail'),
    path('dashboard/team/join/response/', JoinTeamResponse.as_view(), name='join_team_response'),
    path('dashboard/team/member/remove/<int:team_pk>/<int:member_pk>/', RemoveTeamMember.as_view(), name='remove_team_member'),
    path('dashboard/team/invite/<int:team_pk>/<int:user_pk>/', InviteUser.as_view(), name="invite_member"),
    path('dashboard/team/invite/<int:team_pk>/<int:user_pk>/response/<str:response>/', InviteUserResponse.as_view(), name="invite_member_response"),
    path('dashboard/team/role/<int:team_pk>/<int:user_pk>/', PositionMemberTeam.as_view(), name="position_team_member"),

    #Remove Alts
    path('dashboard/alts/remove/<int:pk>/', RemoveAlts.as_view(), name="remove_alt"),
    path('dashboard/alts/remove/response/<int:pk>/', RemoveAltsResponse.as_view(), name="delete_alt_response"),


    #wallet url
    path('dashboard/wallet/update/', WalletUpdateDetail.as_view(), name="card_detail_update"),
    path('dashboard/wallet/askink/money/', AskingMoney.as_view(), name="asking_money"),

    #Notifications
    path('dashboard/notifications/seen/', SeenNotif.as_view(), name="seen_notifications"),
]