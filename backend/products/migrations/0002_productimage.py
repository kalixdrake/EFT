import django.db.models.deletion
from django.db import migrations, models


def migrate_legacy_product_images(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    ProductImage = apps.get_model('products', 'ProductImage')
    for product in Product.objects.exclude(image='').exclude(image__isnull=True):
        if not ProductImage.objects.filter(product=product).exists():
            ProductImage.objects.create(product=product, image=product.image, order=0)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/')),
                ('order', models.PositiveIntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.RunPython(migrate_legacy_product_images, migrations.RunPython.noop),
    ]
