from django.shortcuts import render
from django.views.generic import TemplateView
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.authentication.mixins import ZidRequiredMixin

class HomeView(ZidRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        # Initialize the global layout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Add current business info to context
        context['current_zid'] = self.request.zid
        context['current_business_name'] = self.request.session.get('current_business', 'Unknown Business')

        return context

# Create your views here.
