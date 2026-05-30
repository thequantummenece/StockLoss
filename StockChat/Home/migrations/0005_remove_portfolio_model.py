# Move Portfolio model from Home app to portfolio app.
# Only updates Django's state — the DB table (Home_portfolio) stays as-is.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Home", "0004_update_portfolio_constraint_and_related_name"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name="Portfolio"),
            ],
            database_operations=[],
        ),
    ]
