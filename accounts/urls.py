from django.urls import path
from accounts.views import HousecallProWebhookView

urlpatterns = [
    path('webhook/', HousecallProWebhookView.as_view(), name='hcp_webhook'),
]