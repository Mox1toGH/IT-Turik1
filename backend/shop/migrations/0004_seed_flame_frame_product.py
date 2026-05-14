from django.db import migrations


FLAME_FRAME_URL = '/avatar-frames/fire-tongues.svg'


def seed_flame_frame(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    Product = apps.get_model('shop', 'Product')

    category, _ = Category.objects.get_or_create(name='Digital Goods')

    Product.objects.get_or_create(
        name='Flame Tongues Avatar Frame',
        defaults={
            'description': 'Equip fiery frame around your avatar.',
            'price': 120,
            'stock_quantity': 999999,
            'category': category,
            'product_type': 'digital',
            'digital_asset_url': FLAME_FRAME_URL,
            'is_active': True,
        },
    )


def unseed_flame_frame(apps, schema_editor):
    Product = apps.get_model('shop', 'Product')
    Product.objects.filter(name='Flame Tongues Avatar Frame').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_product_digital_asset_url_userdigitalinventory'),
    ]

    operations = [
        migrations.RunPython(seed_flame_frame, unseed_flame_frame),
    ]
