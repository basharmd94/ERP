from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView, CreateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import User

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from .forms import ZidLoginForm, UserBusinessForm, RegisterUserForm
from .models import UserBusinessAccess, Business


class AuthView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Update the context
        context.update(
            {
                "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
            }
        )

        return context


class ZidLoginView(LoginView):
    form_class = ZidLoginForm
    template_name = 'auth_login_basic.html'
    success_url = reverse_lazy('index')
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({
            "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
        })
        return context

    def form_valid(self, form):
        """Process the form submission."""
        # Get credentials
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        zid = form.cleaned_data.get('zid')

        # Authenticate with custom backend
        user = authenticate(self.request, username=username, password=password, zid=zid)

        if user is None:
            # Authentication failed
            messages.error(self.request, "Invalid Business ID, username, or password.")
            return self.form_invalid(form)

        # Log in the user
        login(self.request, user)

        # Store ZID in session for global access
        self.request.session['current_zid'] = zid

        # Try to get business name for better UX
        try:
            business = Business.objects.get(zid=zid)
            self.request.session['current_business'] = business.name
        except Business.DoesNotExist:
            pass

        # Redirect superusers to the admin dashboard
        if user.is_superuser:
            return redirect('admin-dashboard')

        return redirect(self.get_success_url())


class UserBusinessManagementView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'user_business_management.html'
    form_class = UserBusinessForm
    success_url = reverse_lazy('manage-user-business')

    def test_func(self):
        # Only allow superusers to access this view
        return self.request.user.is_superuser

    def form_valid(self, form):
        user = form.cleaned_data['user']
        selected_businesses = form.cleaned_data['businesses']

        # Remove all existing access first
        UserBusinessAccess.objects.filter(user=user).delete()

        # Create new access for selected businesses
        for business in selected_businesses:
            UserBusinessAccess.objects.create(user=user, business=business)

        messages.success(self.request, f"Business access updated for {user.username}")
        return super().form_valid(form)

    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

    def get_initial(self):
        initial = super().get_initial()
        user_id = self.request.GET.get('user')

        if user_id:
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(id=user_id)
                initial['user'] = user

                # Pre-select businesses the user has access to
                initial['businesses'] = Business.objects.filter(
                    userbusinessaccess__user=user
                )
            except User.DoesNotExist:
                pass

        return initial


class RegisterUserView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = RegisterUserForm
    template_name = 'register_user.html'
    success_url = reverse_lazy('register-user')

    def test_func(self):
        # Only allow superusers to register users
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['businesses'] = Business.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        # Create the user
        user = form.save(commit=False)

        # Set additional attributes from form
        user.is_staff = 'is_staff' in self.request.POST
        user.is_superuser = 'is_superuser' in self.request.POST
        user.save()

        # Assign businesses
        business_ids = self.request.POST.getlist('businesses')
        if business_ids:
            for business_id in business_ids:
                try:
                    business = Business.objects.get(id=business_id)
                    UserBusinessAccess.objects.create(user=user, business=business)
                except Business.DoesNotExist:
                    pass

        messages.success(self.request, f"User {user.username} created successfully with access to selected businesses.")
        return super().form_valid(form)


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin_dashboard.html'

    def test_func(self):
        # Only allow superusers to access this view
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context
