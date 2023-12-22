from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import SignupForm

class Signup(View):
    def get(self, request):
        if request.user.is_authenticated():
            return redirect('dashboard')
        
        form = SignupForm()
        
        context = {
            'form' : form
        }

        return render(request, 'accounts/signup.html', context)


class SignupDiscord(View):
    def get(self, request):
        ...

class Login(View):
    def get(self, request):
        ...

        
class Dashboard(View):
    def get(self, request):
        ...

