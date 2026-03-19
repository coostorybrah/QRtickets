import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("events", "0003_alter_tickettype_price_and_more"),
        ("main", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="Order",
                    fields=[
                        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                        ("total_price", models.DecimalField(decimal_places=2, max_digits=10)),
                        ("status", models.CharField(choices=[("pending", "Pending"), ("paid", "Paid"), ("cancelled", "Cancelled")], default="pending", max_length=20)),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="orders", to=settings.AUTH_USER_MODEL)),
                    ],
                    options={"db_table": "main_order"},
                ),
                migrations.CreateModel(
                    name="OrderItem",
                    fields=[
                        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                        ("quantity", models.PositiveIntegerField()),
                        ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.order")),
                        ("ticket_type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="events.tickettype")),
                    ],
                    options={
                        "db_table": "main_orderitem",
                        "unique_together": {("order", "ticket_type")},
                    },
                ),
            ],
        ),
    ]
