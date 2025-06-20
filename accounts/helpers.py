from decimal import Decimal
from django.utils.dateparse import parse_datetime
from .models import Lead

def handle_employee_assigner(data):
    """
    Creates handler and worker records based on webhook data.
    
    Args:
        data (dict): Webhook payload containing lead and assignment information
    
    Returns:
        dict: Summary of created records
    """
    try:
        # Extract basic information
        custom_data = data.get('customData', {})
        handler = custom_data.get('Handler', '').strip()
        workers_assigned = custom_data.get('Workers Assigned', '').strip()
        value_str = custom_data.get('Value', '0')
        
        # Convert value to Decimal for calculations
        try:
            total_value = Decimal(str(value_str))
        except (ValueError, TypeError):
            total_value = Decimal('0.00')
        
        # Parse date_created
        date_created = parse_datetime(data.get('date_created'))
        
        # Common fields for all records
        common_fields = {
            'contact_id': data.get('contact_id'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'full_name': data.get('full_name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'address1': data.get('address1'),
            'city': data.get('city'),
            'state': data.get('state'),
            'country': data.get('country'),
            'timezone': data.get('timezone'),
            'opportunity_id': data.get('id'),
            'opportunity_name': data.get('opportunity_name'),
            'status': data.get('status', 'open'),
            'lead_value': Decimal(str(data.get('lead_value', 0))),
            'opportunity_source': data.get('opportunity_source'),
            'source': data.get('source'),
            'pipeline_stage': data.get('pipleline_stage'),  # Note: keeping the typo from original data
            'pipeline_name': data.get('pipeline_name'),
            'quote_link': data.get('Quote Link'),
            'value': value_str,
            'date_created': date_created,
        }
        
        created_records = []
        
        # Create Handler Record (15% of value)
        if handler:
            handler_price = total_value * Decimal('0.15')  # 15% of total value
            
            handler_record = Lead.objects.create(
                **common_fields,
                user_name=handler,
                employee_price=handler_price,
                user_type='handler'
            )
            created_records.append({
                'type': 'handler',
                'name': handler,
                'price': float(handler_price)
            })
        
        # Create Worker Records (35% split among all workers)
        if workers_assigned:
            # Split workers by comma and clean up names
            worker_list = [worker.strip() for worker in workers_assigned.split(',') if worker.strip()]
            
            if worker_list:
                # Calculate 35% of total value
                workers_total = total_value * Decimal('0.35')
                # Split evenly among workers
                worker_price = workers_total / len(worker_list)
                
                for worker in worker_list:
                    worker_record = Lead.objects.create(
                        **common_fields,
                        user_name=worker,
                        employee_price=worker_price,
                        user_type='Worker Assigned',
                        status='employee assigned'
                    )
                    created_records.append({
                        'type': 'worker',
                        'name': worker,
                        'price': float(worker_price)
                    })
        
        return {
            'success': True,
            'message': f'Successfully created {len(created_records)} records',
            'records_created': created_records,
            'total_value': float(total_value),
            'handler_percentage': 15,
            'workers_percentage': 35
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to create records'
        }