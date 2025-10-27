import stripe
import json
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from accounts.models import Organization, Subscription, Payment, APIKey


class StripeService:
    """Stripe payment processing service"""

    def __init__(self, organization=None):
        # Get Stripe API key
        if organization:
            try:
                stripe_key = APIKey.objects.get(
                    organization=organization,
                    provider='stripe',
                    is_active=True
                )
                stripe.api_key = stripe_key.key
            except APIKey.DoesNotExist:
                stripe.api_key = settings.STRIPE_SECRET_KEY
        else:
            stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_customer(self, organization):
        """Create Stripe customer for organization"""
        customer = stripe.Customer.create(
            email=organization.contact_email,
            name=organization.name,
            metadata={
                'organization_id': organization.id,
            }
        )

        # Update organization with Stripe customer ID
        organization.stripe_customer_id = customer.id
        organization.save()

        return customer

    def create_subscription(self, organization, price_id, payment_method_id=None):
        """Create subscription for organization"""

        # Ensure customer exists
        if not organization.stripe_customer_id:
            customer = self.create_customer(organization)
        else:
            customer = stripe.Customer.retrieve(organization.stripe_customer_id)

        # Create subscription data
        subscription_data = {
            'customer': customer.id,
            'items': [{
                'price': price_id,
            }],
            'metadata': {
                'organization_id': organization.id,
            },
            'expand': ['latest_invoice.payment_intent'],
        }

        if payment_method_id:
            # Attach payment method and set as default
            stripe.PaymentMethod.attach(payment_method_id, customer=customer.id)
            stripe.Customer.modify(
                customer.id,
                invoice_settings={'default_payment_method': payment_method_id}
            )

        subscription = stripe.Subscription.create(**subscription_data)

        # Create local subscription record
        local_subscription = Subscription.objects.create(
            organization=organization,
            plan_name=f"Plan {price_id}",
            stripe_subscription_id=subscription.id,
            stripe_customer_id=customer.id,
            status='active',
            current_period_start=timezone.datetime.fromtimestamp(subscription.current_period_start),
            current_period_end=timezone.datetime.fromtimestamp(subscription.current_period_end),
        )

        return subscription, local_subscription

    def create_payment_intent(self, amount, currency='usd', metadata=None):
        """Create payment intent for one-time payment"""
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency=currency,
            metadata=metadata or {},
        )

        return intent

    def confirm_payment(self, payment_intent_id, payment_method_id=None):
        """Confirm payment intent"""
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if payment_method_id:
            intent = stripe.PaymentIntent.modify(
                payment_intent_id,
                payment_method=payment_method_id
            )

        confirmed_intent = stripe.PaymentIntent.confirm(payment_intent_id)

        return confirmed_intent

    def create_setup_intent(self, customer_id=None):
        """Create setup intent for saving payment method"""
        intent = stripe.SetupIntent.create(
            customer=customer_id,
            payment_method_types=['card'],
        )

        return intent

    def get_payment_methods(self, customer_id):
        """Get customer's payment methods"""
        payment_methods = stripe.PaymentMethod.list(
            customer=customer_id,
            type='card'
        )

        return payment_methods.data

    def update_subscription(self, subscription_id, new_price_id):
        """Update subscription to new plan"""
        subscription = stripe.Subscription.retrieve(subscription_id)

        # Update the subscription item
        stripe.Subscription.modify(
            subscription_id,
            items=[{
                'id': subscription.items.data[0].id,
                'price': new_price_id,
            }],
            proration_behavior='create_prorations',
        )

        # Update local record
        local_subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        local_subscription.plan_name = f"Plan {new_price_id}"
        local_subscription.save()

        return subscription

    def cancel_subscription(self, subscription_id, cancel_at_period_end=True):
        """Cancel subscription"""
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=cancel_at_period_end
        )

        # Update local record
        local_subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        local_subscription.status = 'cancelled'
        local_subscription.save()

        return subscription

    def handle_webhook(self, payload, sig_header):
        """Handle Stripe webhook"""
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            raise ValueError(f"Invalid payload: {e}")
        except stripe.error.SignatureVerificationError as e:
            raise ValueError(f"Invalid signature: {e}")

        # Handle different event types
        event_type = event['type']

        if event_type == 'customer.subscription.created':
            self._handle_subscription_created(event['data']['object'])
        elif event_type == 'customer.subscription.updated':
            self._handle_subscription_updated(event['data']['object'])
        elif event_type == 'customer.subscription.deleted':
            self._handle_subscription_deleted(event['data']['object'])
        elif event_type == 'invoice.payment_succeeded':
            self._handle_payment_succeeded(event['data']['object'])
        elif event_type == 'invoice.payment_failed':
            self._handle_payment_failed(event['data']['object'])

        return event

    def _handle_subscription_created(self, subscription_data):
        """Handle subscription created webhook"""
        subscription_id = subscription_data['id']
        customer_id = subscription_data['customer']

        # Find organization
        try:
            organization = Organization.objects.get(stripe_customer_id=customer_id)
            subscription, created = Subscription.objects.get_or_create(
                stripe_subscription_id=subscription_id,
                defaults={
                    'organization': organization,
                    'stripe_customer_id': customer_id,
                    'status': 'active',
                    'current_period_start': timezone.datetime.fromtimestamp(subscription_data['current_period_start']),
                    'current_period_end': timezone.datetime.fromtimestamp(subscription_data['current_period_end']),
                }
            )
        except Organization.DoesNotExist:
            pass

    def _handle_subscription_updated(self, subscription_data):
        """Handle subscription updated webhook"""
        subscription_id = subscription_data['id']

        try:
            subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
            subscription.status = subscription_data['status']
            subscription.current_period_start = timezone.datetime.fromtimestamp(subscription_data['current_period_start'])
            subscription.current_period_end = timezone.datetime.fromtimestamp(subscription_data['current_period_end'])
            subscription.save()
        except Subscription.DoesNotExist:
            pass

    def _handle_subscription_deleted(self, subscription_data):
        """Handle subscription deleted webhook"""
        subscription_id = subscription_data['id']

        try:
            subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
            subscription.status = 'cancelled'
            subscription.save()
        except Subscription.DoesNotExist:
            pass

    def _handle_payment_succeeded(self, invoice_data):
        """Handle successful payment webhook"""
        customer_id = invoice_data['customer']
        amount_paid = invoice_data['amount_paid'] / 100  # Convert from cents

        try:
            organization = Organization.objects.get(stripe_customer_id=customer_id)

            # Create payment record
            Payment.objects.create(
                organization=organization,
                amount=Decimal(str(amount_paid)),
                currency=invoice_data['currency'].upper(),
                status='completed',
                metadata={
                    'invoice_id': invoice_data['id'],
                    'subscription_id': invoice_data.get('subscription'),
                }
            )
        except Organization.DoesNotExist:
            pass

    def _handle_payment_failed(self, invoice_data):
        """Handle failed payment webhook"""
        customer_id = invoice_data['customer']
        amount_due = invoice_data['amount_due'] / 100

        try:
            organization = Organization.objects.get(stripe_customer_id=customer_id)

            # Create failed payment record
            Payment.objects.create(
                organization=organization,
                amount=Decimal(str(amount_due)),
                currency=invoice_data['currency'].upper(),
                status='failed',
                metadata={
                    'invoice_id': invoice_data['id'],
                    'subscription_id': invoice_data.get('subscription'),
                }
            )
        except Organization.DoesNotExist:
            pass

    def get_subscription_plans(self):
        """Get available subscription plans"""
        # This would typically fetch from Stripe Products/Prices
        # For now, return hardcoded plans
        return [
            {
                'id': 'price_basic',
                'name': 'Basic Plan',
                'price': 29.99,
                'currency': 'USD',
                'interval': 'month',
                'features': ['100 conversations/month', 'Voice calls', 'Email support']
            },
            {
                'id': 'price_premium',
                'name': 'Premium Plan',
                'price': 79.99,
                'currency': 'USD',
                'interval': 'month',
                'features': ['1000 conversations/month', 'Voice calls', 'Social media integration', 'Priority support']
            },
            {
                'id': 'price_enterprise',
                'name': 'Enterprise Plan',
                'price': 199.99,
                'currency': 'USD',
                'interval': 'month',
                'features': ['Unlimited conversations', 'All integrations', 'White-label', 'Dedicated support']
            }
        ]
