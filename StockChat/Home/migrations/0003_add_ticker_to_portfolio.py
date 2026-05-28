from django.db import migrations, models


def populate_ticker_and_merge(apps, schema_editor):
    """Set ticker from stock_name (uppercased), merge duplicates per user."""
    Portfolio = apps.get_model('Home', 'Portfolio')
    for row in Portfolio.objects.all():
        row.ticker = row.stock_name.upper().replace(' ', '')
        row.save(update_fields=['ticker'])

    # Merge duplicates: keep the first entry per (user, ticker), sum quantity & invested
    seen = {}
    for row in Portfolio.objects.order_by('id'):
        key = (row.user_id, row.ticker)
        if key in seen:
            master = seen[key]
            master.quantity += row.quantity
            master.invested += row.invested
            master.save(update_fields=['quantity', 'invested'])
            row.delete()
        else:
            seen[key] = row


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0002_portfolio'),
    ]

    operations = [
        # Step 1: Add ticker column with a default
        migrations.AddField(
            model_name='portfolio',
            name='ticker',
            field=models.CharField(default='UNKNOWN', max_length=20),
            preserve_default=False,
        ),
        # Step 2: Populate ticker and merge duplicates
        migrations.RunPython(populate_ticker_and_merge, migrations.RunPython.noop),
        # Step 3: Add unique constraint
        migrations.AlterUniqueTogether(
            name='portfolio',
            unique_together={('user', 'ticker')},
        ),
    ]
