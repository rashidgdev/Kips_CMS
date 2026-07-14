from decimal import Decimal

from django.db import migrations

DEFAULT_CATEGORIES = [
    ('Quiz', Decimal('10')),
    ('Assignment', Decimal('10')),
    ('Presentation', Decimal('10')),
    ('Midterm', Decimal('30')),
    ('Final', Decimal('40')),
]


def seed_categories(apps, schema_editor):
    AssessmentCategory = apps.get_model('assessments', 'AssessmentCategory')
    for name, default_weight_percent in DEFAULT_CATEGORIES:
        AssessmentCategory.objects.get_or_create(
            name=name, defaults={'default_weight_percent': default_weight_percent}
        )


def unseed_categories(apps, schema_editor):
    AssessmentCategory = apps.get_model('assessments', 'AssessmentCategory')
    AssessmentCategory.objects.filter(name__in=[name for name, _ in DEFAULT_CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
