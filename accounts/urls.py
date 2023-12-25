from django.urls import path
from .views import SignupDiscord, Signup, Dashboard, Login, Logout


urlpatterns = [
    path('signup/', Signup.as_view(), name='signup'),
    path('signup/discord/response/', SignupDiscord.as_view(), name='discord_response'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
]