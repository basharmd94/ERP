from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib import messages
from apps.opord.models import Opord
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from django import forms

class OpordForm(forms.ModelForm):
    class Meta:
        model = Opord
        fields = ['xordernum', 'xdate', 'xcus', 'xstatusord', 'xdisc', 'xdtwotax', 'xsltype']
        widgets = {
            'xdate': forms.DateInput(attrs={'type': 'date'}),
        }

class OpordListView(TemplateView):
    template_name = 'opord/opord.html'

    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Set vertical layout
        context.update({
            'layout': 'vertical',
            'navbar_full': False,
            'layout_path': TemplateHelper.set_layout('layout_vertical.html', context),
            'opords': Opord.objects.all()[:30],
            'segment': 'opord',
            'page_title': 'Operation Orders',
            'parent': 'Apps',
            'form': OpordForm()
        })

        # Map context variables
        TemplateHelper.map_context(context)

        return context

    def post(self, request, *args, **kwargs):
        form = OpordForm(request.POST)
        context = self.get_context_data(**kwargs)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Operation Order created successfully!')
                return redirect('opord:list')
            except Exception as e:
                messages.error(request, f'Error creating Operation Order: {str(e)}')
        else:
            context['form'] = form

        return self.render_to_response(context)

# Function-based view alternative
def opord_list(request):
    # For the function-based view, we need a different approach
    # This view is kept for reference but we'll use the class-based view instead
    pass
