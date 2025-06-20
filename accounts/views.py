from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import logging
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import json
from accounts.models import Webhook
from accounts.helpers import handle_employee_assigner

# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class HousecallProWebhookView(View):
    
    def post(self, request):
        try:
            # Parse webhook data
            webhook_data = json.loads(request.body)
            print("Webhook Data: ", webhook_data)

            Webhook.objects.create(
                payload=webhook_data
            )
            handle_employee_assigner(webhook_data)
                        
            return JsonResponse(status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:           
            return JsonResponse({"error": "Internal server error"}, status=500)