import os
import requests
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from ..models import Organization
import logging

logger = logging.getLogger(__name__)

class APIIntegrationService:
    """Generic service for integrating with external CRM/ERP systems"""

    def __init__(self, organization: Organization):
        self.organization = organization
        self.base_url = getattr(organization, 'crm_api_url', None)
        self.api_key = getattr(organization, 'crm_api_key', None)
        self.api_secret = getattr(organization, 'crm_api_secret', None)
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else None
        }

    def get_customer_info(self, customer_identifier: str) -> Optional[Dict[str, Any]]:
        """Fetch customer information from CRM system"""
        if not self._is_configured():
            return None

        try:
            # Generic customer lookup endpoint
            url = f"{self.base_url}/customers/search"
            params = {'identifier': customer_identifier}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrieved customer info for {customer_identifier}")
                return self._mask_pii(data)
            else:
                logger.warning(f"Failed to get customer info: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching customer info: {str(e)}")
            return None

    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Fetch order status from CRM/ERP system"""
        if not self._is_configured():
            return None

        try:
            url = f"{self.base_url}/orders/{order_id}"

            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrieved order status for {order_id}")
                return data
            else:
                logger.warning(f"Failed to get order status: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching order status: {str(e)}")
            return None

    def get_product_info(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Fetch product information from ERP system"""
        if not self._is_configured():
            return None

        try:
            url = f"{self.base_url}/products/{product_id}"

            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrieved product info for {product_id}")
                return data
            else:
                logger.warning(f"Failed to get product info: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching product info: {str(e)}")
            return None

    def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for products in the ERP system"""
        if not self._is_configured():
            return []

        try:
            url = f"{self.base_url}/products/search"
            params = {'q': query, 'limit': limit}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                products = data.get('products', []) if isinstance(data, dict) else data
                logger.info(f"Found {len(products)} products for query: {query}")
                return products
            else:
                logger.warning(f"Failed to search products: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []

    def get_inventory_status(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Fetch inventory status for a product"""
        if not self._is_configured():
            return None

        try:
            url = f"{self.base_url}/inventory/{product_id}"

            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrieved inventory status for {product_id}")
                return data
            else:
                logger.warning(f"Failed to get inventory status: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching inventory status: {str(e)}")
            return None

    def _is_configured(self) -> bool:
        """Check if the API integration is properly configured"""
        return bool(self.base_url and self.api_key)

    def _mask_pii(self, data: Dict[str, Any]) -> Dict[str, Any]]:
        """Mask personally identifiable information in API responses"""
        masked_data = data.copy()

        # Mask sensitive fields
        pii_fields = ['email', 'phone', 'address', 'ssn', 'credit_card']

        def mask_nested_dict(d):
            for key, value in d.items():
                if isinstance(value, dict):
                    mask_nested_dict(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            mask_nested_dict(item)
                elif key.lower() in pii_fields and isinstance(value, str):
                    # Mask the value (show first 2 and last 2 characters)
                    if len(value) > 4:
                        d[key] = value[:2] + '*' * (len(value) - 4) + value[-2:]
                    else:
                        d[key] = '*' * len(value)

        mask_nested_dict(masked_data)
        return masked_data

    def test_connection(self) -> bool:
        """Test the API connection"""
        if not self._is_configured():
            return False

        try:
            # Try a simple health check or ping endpoint
            url = f"{self.base_url}/health"  # Common health check endpoint

            response = requests.get(url, headers=self.headers, timeout=5)

            if response.status_code in [200, 201, 202]:
                logger.info("API integration connection test successful")
                return True
            else:
                logger.warning(f"API integration connection test failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"API integration connection test error: {str(e)}")
            return False
