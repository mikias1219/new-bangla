from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User, Organization
from core.models import Client, BanglaIntent, Product

class Command(BaseCommand):
    help = "Seed demo data: organization, client, intents, products, and approve org"

    def handle(self, *args, **options):
        # Organization
        org, _ = Organization.objects.get_or_create(
            name='Demo E-Commerce',
            defaults={
                'description': 'Demo org for BanglaChatPro',
                'website': 'https://demo.shop',
                'approval_status': 'approved',
                'is_active': True,
            }
        )
        # Admin user (if exists), associate with org
        admin = User.objects.filter(username='admin').first()
        if admin and not admin.organization:
            admin.organization = org
            admin.save()

        # Client
        client, _ = Client.objects.get_or_create(
            name='Demo Shop',
            domain='demo.shop',
            defaults={
                'contact_email': 'support@demo.shop',
                'description': 'Primary storefront client',
                'website': 'https://demo.shop',
                'phone': '+8801700000000',
                'is_active': True,
            }
        )

        # Intents
        BanglaIntent.objects.get_or_create(
            client=client,
            name='order_status',
            defaults={
                'training_phrase': 'অর্ডারের অবস্থা জানতে চাই',
                'ai_response_template': 'আপনার অর্ডারের অবস্থা: {{status}}',
                'description': 'Order status inquiry',
                'examples': ['আমার অর্ডার কোথায়?', 'অর্ডার স্ট্যাটাস'],
                'responses': ['আপনার অর্ডার প্রক্রিয়াধীন আছে'],
                'is_active': True,
            }
        )

        # Products
        Product.objects.get_or_create(
            sku='SKU-100',
            defaults={
                'client': client,
                'organization': org,
                'name': 'টি-শার্ট',
                'description': 'উচ্চমানের কটন টি-শার্ট',
                'price': 499,
                'currency': 'BDT',
                'in_stock': True,
                'stock_qty': 50,
                'is_active': True,
            }
        )
        Product.objects.get_or_create(
            sku='SKU-200',
            defaults={
                'client': client,
                'organization': org,
                'name': 'জুতো',
                'description': 'দীর্ঘস্থায়ী এবং আরামদায়ক',
                'price': 1299,
                'currency': 'BDT',
                'in_stock': False,
                'stock_qty': 0,
                'is_active': True,
            }
        )

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))


