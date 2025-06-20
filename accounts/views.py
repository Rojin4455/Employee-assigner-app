from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import logging
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import json
import traceback
from accounts.models import Webhook
from accounts.helpers import handle_employee_assigner
import employee_assigner.settings

# Set up logging
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class HousecallProWebhookView(View):
    
    def post(self, request):
        try:
            # Parse webhook data
            webhook_data = json.loads(request.body)
            print("Webhook Data: ", webhook_data)
            
            # Save webhook data first
            webhook_record = Webhook.objects.create(
                payload=webhook_data
            )
            print(f"Webhook record created with ID: {webhook_record.id}")
            
            # Handle employee assignment
            result = handle_employee_assigner(webhook_data)
            
            if result.get('success'):
                print(f"Employee assignment successful: {result}")
                return JsonResponse({
                    "message": "Webhook processed successfully",
                    "records_created": result.get('records_created', [])
                }, status=200)
            else:
                print(f"Employee assignment failed: {result}")
                logger.error(f"Employee assignment failed: {result}")
                return JsonResponse({
                    "error": "Employee assignment failed",
                    "details": result.get('error', 'Unknown error')
                }, status=500)
                        
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON: {str(e)}"
            print(error_msg)
            logger.error(error_msg)
            return JsonResponse({"error": "Invalid JSON"}, status=400)
            
        except Exception as e:
            error_msg = f"Internal server error: {str(e)}"
            error_traceback = traceback.format_exc()
            print(f"Error: {error_msg}")
            print(f"Traceback: {error_traceback}")
            logger.error(f"Webhook processing error: {error_msg}")
            logger.error(f"Traceback: {error_traceback}")
            
            return JsonResponse({
                "error": "Internal server error",
                "message": str(e) if employee_assigner.settings.DEBUG else "An error occurred"
            }, status=500)