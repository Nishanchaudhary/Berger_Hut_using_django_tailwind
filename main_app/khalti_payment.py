import requests
from django.conf import settings
from django.urls import reverse
import logging
import time
from requests.exceptions import RequestException
from django.core.cache import cache
import hashlib

logger = logging.getLogger(__name__)

class KhaltiPaymentService:
    """
    Official Khalti ePayment implementation based on:
    https://docs.khalti.com/khalti-epayment/
    """
    LIVE_API_URL = "https://khalti.com/api/v2"
    TEST_API_URL = "https://dev.khalti.com/api/v2/"
    
    def __init__(self, request=None, order=None):
        self.request = request
        self.order = order
        self.base_url = self.TEST_API_URL if settings.DEBUG else self.LIVE_API_URL
        self.secret_key = settings.KHALTI_SECRET_KEY

    def _get_headers(self):
        return {
            "Authorization": f"Key {self.secret_key}",
            "Content-Type": "application/json",
        }

    def _generate_product_identity(self):
        """Generate unique product identity as required by Khalti"""
        return f"order_{self.order.id}_{int(time.time())}"

    def initiate_payment(self):
        """
        Initialize payment as per Khalti documentation:
        https://docs.khalti.com/khalti-epayment/#initiate-payment
        """
        payload = {
            "return_url": self.request.build_absolute_uri(reverse('khalti_callback')),
            "website_url": self.request.build_absolute_uri('/'),
            "amount": int(self.order.total_price * 100),  # Convert to paisa
            "purchase_order_id": str(self.order.id),
            "purchase_order_name": f"Order #{self.order.id}",
            "customer_info": {
                "name": self.request.user.get_full_name() or self.request.user.username,
                "email": self.request.user.email,
                "phone": self.order.contact_phone
            },
            "product_details": [
                {
                    "identity": self._generate_product_identity(),
                    "name": item.product.name,
                    "total_price": int(item.price * 100),
                    "quantity": item.quantity,
                    "unit_price": int(item.product.price * 100)
                } for item in self.order.items.all()
            ]
        }

        try:
            response = requests.post(
                f"{self.base_url}/epayment/initiate/",
                json=payload,
                headers=self._get_headers(),
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get('pidx'):
                logger.error("Khalti payment initiation failed - no pidx returned")
                return None
                
            return {
                'payment_url': data.get('payment_url'),
                'pidx': data.get('pidx'),
                'expires_at': data.get('expires_at')
            }

        except RequestException as e:
            logger.error(f"Khalti payment initiation failed: {str(e)}")
            return None

    def verify_payment(self, pidx):
        """
        Verify payment using Khalti's API:
        https://docs.khalti.com/khalti-epayment/#lookup-api
        """
        try:
            response = requests.post(
                f"{self.base_url}/epayment/lookup/",
                json={"pidx": pidx},
                headers=self._get_headers(),
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') == 'Completed':
                # Additional verification
                if int(data['amount']) != int(self.order.total_price * 100):
                    logger.error(f"Amount mismatch: Order {self.order.total_price} vs Khalti {data['amount']}")
                    return False
                return True
            return False

        except RequestException as e:
            logger.error(f"Payment verification failed: {str(e)}")
            return False

    def validate_callback(self, request):
        """
        Validate Khalti callback request:
        https://docs.khalti.com/khalti-epayment/#verification
        """
        try:
            pidx = request.GET.get('pidx')
            transaction_id = request.GET.get('transaction_id')
            amount = request.GET.get('amount')
            status = request.GET.get('status')
            
            if not all([pidx, transaction_id, amount, status]):
                logger.error("Missing required parameters in callback")
                return False
                
            # Basic amount validation
            if int(amount) != int(self.order.total_price * 100):
                logger.error("Amount mismatch in callback")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Callback validation error: {str(e)}")
            return False