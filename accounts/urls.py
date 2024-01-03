from django.urls import path
from .views import SignupDiscord, Signup, Dashboard, Login, Logout, CreateTeam, LeftTheTeam, TeamDetailLink, JoinTeamResponse, SeenNotif, WalletUpdateDetail, AskingMoney


urlpatterns = [
    path('signup/', Signup.as_view(), name='signup'),
    path('signup/discord/response/', SignupDiscord.as_view(), name='discord_response'),
    path('', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),

    #Team urls
    path('dashboard/team/create/', CreateTeam.as_view(), name='create_team'),
    path('dashboard/team/left/<int:team_pk>/', LeftTheTeam.as_view(), name='left_the_team'),
    path('dashboard/team/<str:team_name>/<int:team_pk>/', TeamDetailLink.as_view(), name='team_detail'),
    path('dashboard/team/join/response/', JoinTeamResponse.as_view(), name='join_team_response'),
    path('dashboard/notifications/seen/', SeenNotif.as_view(), name="seen_notifications"),

    #wallet url
    path('dashboard/wallet/update/', WalletUpdateDetail.as_view(), name="card_detail_update"),
    path('dashboard/wallet/askink/money/', AskingMoney.as_view(), name="asking_money"),
]