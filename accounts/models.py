from django.db import models

# Create your models here.
class Webhook(models.Model):
    payload = models.JSONField()  # Store the entire raw payload
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.received_at}"
    


from django.db import models
from django.core.validators import RegexValidator
from decimal import Decimal


class Lead(models.Model):
    """Model to store lead/opportunity data from webhook"""
    
    # User type choices
    USER_TYPE_CHOICES = [
        ('handler', 'Handler'),
        ('Worker Assigned', 'Worker Assigned'),
    ]
    
    # Contact Information
    contact_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    
    # Phone number with validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17)
    
    address1 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50)
    
    # Opportunity Information
    opportunity_id = models.CharField(max_length=50, unique=True)  # This is the 'id' field from payload
    opportunity_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default='open')
    lead_value = models.DecimalField(max_digits=10, decimal_places=2)
    opportunity_source = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    pipeline_stage = models.CharField(max_length=100)
    pipeline_name = models.CharField(max_length=100)
    
    quote_link = models.URLField(blank=True, null=True)
    
    user_name =  models.CharField(max_length=100)
    value = models.CharField(max_length=50, blank=True) 

    employee_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Price/rate for the employee"
    )
    user_type = models.CharField(
        choices=USER_TYPE_CHOICES,
        default='Worker Assigned',
        help_text="Type of user: assigner or worker"
    )

    date_created = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.full_name} - {self.opportunity_name}"