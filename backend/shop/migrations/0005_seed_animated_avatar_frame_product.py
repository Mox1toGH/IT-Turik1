from django.db import migrations

ANIMATED_FRAME_URL = '/avatar-frames/aurora-pulse.svg'


def seed_animated_avatar_frame(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    Product = apps.get_model('shop', 'Product')

    category, _ = Category.objects.get_or_create(name='Digital Goods')

    Product.objects.get_or_create(
        name='Aurora Pulse Avatar Frame',
        defaults={
            'description': 'Animated profile frame with glowing pulse effects.',
            'price': 160,
            'stock_quantity': 999999,
            'category': category,
            'product_type': 'digital',
            'digital_asset_url': ANIMATED_FRAME_URL,
            'is_active': True,
        },
    )


def unseed_animated_avatar_frame(apps, schema_editor):
    Product = apps.get_model('shop', 'Product')
    Product.objects.filter(name='Aurora Pulse Avatar Frame').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0004_seed_flame_frame_product'),
    ]

    operations = [
        migrations.RunPython(seed_animated_avatar_frame, unseed_animated_avatar_frame),
    ]
