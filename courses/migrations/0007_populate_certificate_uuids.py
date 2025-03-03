import uuid
from django.db import migrations

def populate_uuids(apps, schema_editor):
    # Get the historical version of the Certificate model
    Certificate = apps.get_model('courses', 'Certificate')

    # Loop through all certificates and assign UUIDs
    for certificate in Certificate.objects.all():
        if not certificate.uuid:
            certificate.uuid = uuid.uuid4()
            certificate.save()

def reverse_func(apps, schema_editor):
    # No need to do anything for reverse migration
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_certificate_uuid'),
    ]

    operations = [
            migrations.RunPython(populate_uuids, reverse_func),
        ]
