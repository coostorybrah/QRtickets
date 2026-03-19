import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0003_alter_tickettype_price_and_more"),
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="contact_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="order",
            name="customer_name",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="order",
            name="event",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="events.event"),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_method",
            field=models.CharField(choices=[("bank_transfer", "Chuyen khoan ngan hang"), ("momo", "Vi MoMo"), ("cash", "Tien mat")], default="bank_transfer", max_length=30),
        ),
        migrations.AddField(
            model_name="order",
            name="phone_number",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
