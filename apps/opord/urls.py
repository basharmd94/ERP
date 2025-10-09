from django.urls import path
from apps.opord.views import OpordListView

app_name = 'opord'

urlpatterns = [
    path('', OpordListView.as_view(), name='list'),
]
