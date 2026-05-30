# Move Portfolio model from Home app to portfolio app.
# Only updates Django's state — the DB table (Home_portfolio) already exists.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("Home", "0005_remove_portfolio_model"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="Portfolio",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        ("ticker", models.CharField(default="UNKNOWN", max_length=20)),
                        ("stock_name", models.CharField(max_length=100)),
                        ("quantity", models.PositiveIntegerField()),
                        ("invested", models.DecimalField(decimal_places=2, max_digits=12)),
                        ("added_at", models.DateTimeField(auto_now_add=True)),
                        (
                            "user",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="portfolios",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        "db_table": "Home_portfolio",
                        "constraints": [
                            models.UniqueConstraint(
                                fields=("user", "ticker"), name="unique_user_ticker"
                            )
                        ],
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
