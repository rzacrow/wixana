from django.urls import path
from .views import SignupDiscord, Signup, Dashboard, Login
urlpatterns = [
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('signup/discord/response/', SignupDiscord.as_view(), name='discord_response'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
]

#https://discord.com/api/oauth2/authorize?client_id=1187671686179467285&response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fdiscord%2Fresponse%2F&scope=identify+email