
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from .forms import SignUpForm, UserForm, ProfileForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib import messages
from apps.userprofile.models import Profile, Emails
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail

from django.views.generic import ListView,FormView
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class HomeView(TemplateView):
    template_name = 'common/home.html'

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'common/dashboard.html'
    login_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        print(self.request.user.id)
        context['book_list'] = self.request.user
        return context
    
class SignUpView(SuccessMessageMixin, CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'common/register.html'
    success_message = "Account created successfully!"

    def form_valid(self, form): #sends an email to newly created users
        my_subject = "Email from our Django App"
        my_recipient = form.cleaned_data['email']
                
        print(my_recipient)
        html_message = render_to_string("common/email.html")
        plain_message = strip_tags(html_message)

        message = EmailMultiAlternatives(
            subject = my_subject, 
            body = plain_message,
            from_email = None ,
            to= [my_recipient]
        )

        message.attach_alternative(html_message, "text/html")
        message.send()

        return super().form_valid(form)

    # was supposed to login a user after creating an account
    # def form_valid(self, form):
    #     valid = super().form_valid(form)  # Call the parent's form_valid first
    #     username = form.cleaned_data.get('username')
    #     password = form.cleaned_data.get('password1')  # Assuming your form has 'password1'
    #     user = authenticate(username=username, password=password)

    #     if user is not None:
    #         login(self.request, user)  
    #     return valid


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'common/profile.html'

class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    user_form = UserForm
    profile_form = ProfileForm
    template_name = 'common/profile-update.html'

    def post(self, request):

        post_data = request.POST or None
        file_data = request.FILES or None

        user_form = UserForm(post_data, instance=request.user)
        profile_form = ProfileForm(post_data, file_data, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully!')
            return HttpResponseRedirect(reverse_lazy('profile'))

        context = self.get_context_data(
                                        user_form=user_form,
                                        profile_form=profile_form
                                    )

        return self.render_to_response(context)     

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)