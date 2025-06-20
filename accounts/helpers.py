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
        print(f"Processing employee assignment for data: {data}")
        
        # Validate required fields
        required_fields = ['contact_id', 'id', 'customData']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Check if records already exist to avoid duplicates
        existing_records = Lead.objects.filter(
            contact_id=data.get('contact_id'),
            opportunity_id=data.get('id')
        ).exists()
        
        if existing_records:
            print(f"Records already exist for contact_id: {data.get('contact_id')}, opportunity_id: {data.get('id')}")
            return {
                'success': True,
                'message': 'Records already exist, skipping creation',
                'records_created': []
            }
        # Extract basic information
        custom_data = data.get('customData', {})
        handler = custom_data.get('Handler', '').strip()
        workers_assigned = custom_data.get('Workers Assigned', '').strip()
        value_str = custom_data.get('Value', '0')
        
        print(f"Handler: {handler}")
        print(f"Workers Assigned: {workers_assigned}")
        print(f"Value: {value_str}")
        
        # Convert value to Decimal for calculations
        try:
            total_value = Decimal(str(value_str))
        except (ValueError, TypeError) as e:
            print(f"Error converting value to Decimal: {e}")
            total_value = Decimal('0.00')
        
        # Parse date_created
        date_created_str = data.get('date_created')
        if date_created_str:
            date_created = parse_datetime(date_created_str)
            if not date_created:
                print(f"Failed to parse date: {date_created_str}")
                from django.utils import timezone
                date_created = timezone.now()
        else:
            from django.utils import timezone
            date_created = timezone.now()
        
        # Common fields for all records (excluding status to avoid conflicts)
        common_fields = {
            'contact_id': data.get('contact_id', ''),
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'full_name': data.get('full_name', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'address1': data.get('address1', ''),
            'city': data.get('city', ''),
            'state': data.get('state', ''),
            'country': data.get('country', ''),
            'timezone': data.get('timezone', ''),
            'opportunity_id': data.get('id', ''),
            'opportunity_name': data.get('opportunity_name', ''),
            'lead_value': Decimal(str(data.get('lead_value', 0))),
            'opportunity_source': data.get('opportunity_source', ''),
            'source': data.get('source', ''),
            'pipeline_stage': data.get('pipleline_stage', ''),  # Note: keeping the typo from original data
            'pipeline_name': data.get('pipeline_name', ''),
            'quote_link': data.get('Quote Link', ''),
            'value': value_str,
            'date_created': date_created,
            "status":data.get('status', 'open')
        }
        
        print(f"Common fields prepared: {common_fields}")
        
        created_records = []
        
        # Create Handler Record (15% of value)
        if handler:
            handler_price = total_value * Decimal('0.15')  # 15% of total value
            print(f"Creating handler record for: {handler} with price: {handler_price}")
            
            try:
                handler_record = Lead.objects.create(
                    **common_fields,
                    user_name=handler,
                    employee_price=handler_price,
                    user_type='handler',
                    
                )
                print(f"Handler record created successfully: {handler_record.id}")
                created_records.append({
                    'type': 'handler',
                    'name': handler,
                    'price': float(handler_price)
                })
            except Exception as e:
                print(f"Error creating handler record: {e}")
                raise e
        
        # Create Worker Records (35% split among all workers)
        if workers_assigned:
            # Split workers by comma and clean up names
            worker_list = [worker.strip() for worker in workers_assigned.split(',') if worker.strip()]
            print(f"Worker list: {worker_list}")
            
            if worker_list:
                # Calculate 35% of total value
                workers_total = total_value * Decimal('0.35')
                # Split evenly among workers
                worker_price = workers_total / len(worker_list)
                print(f"Worker price each: {worker_price}")
                
                for worker in worker_list:
                    try:
                        print(f"Creating worker record for: {worker}")
                        worker_record = Lead.objects.create(
                            **common_fields,
                            user_name=worker,
                            employee_price=worker_price,
                            user_type='Worker Assigned',
                            
                        )
                        print(f"Worker record created successfully: {worker_record.id}")
                        created_records.append({
                            'type': 'worker',
                            'name': worker,
                            'price': float(worker_price)
                        })
                    except Exception as e:
                        print(f"Error creating worker record for {worker}: {e}")
                        raise e
        
        print(f"Successfully created {len(created_records)} records")
        return {
            'success': True,
            'message': f'Successfully created {len(created_records)} records',
            'records_created': created_records,
            'total_value': float(total_value),
            'handler_percentage': 15,
            'workers_percentage': 35
        }
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in handle_employee_assigner: {e}")
        print(f"Traceback: {error_traceback}")
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to create records',
            'traceback': error_traceback
        }