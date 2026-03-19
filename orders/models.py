import uuid
from django.db import models
from django.conf import settings
from events.models import Event, TicketType


class Order(models.Model):
	STATUS_CHOICES = [
		("pending", "Đang chờ"),
		("paid", "Đã thanh toán"),
		("cancelled", "Đã hủy"),
	]
	PAYMENT_METHOD_CHOICES = [
		("bank_transfer", "Chuyển khoản ngân hàng"),
		("momo", "Vi MoMo"),
		("cash", "Tiền mặt"),
	]

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="orders"
	)

	event = models.ForeignKey(
		Event,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="orders"
	)

	total_price = models.DecimalField(max_digits=10, decimal_places=2)
	customer_name = models.CharField(max_length=120, blank=True)
	phone_number = models.CharField(max_length=30, blank=True)
	contact_email = models.EmailField(blank=True)
	payment_method = models.CharField(
		max_length=30,
		choices=PAYMENT_METHOD_CHOICES,
		default="bank_transfer"
	)

	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "main_order"

	def __str__(self):
		return f"Order {self.id}"

	def calculate_total(self):
		return sum(item.price * item.quantity for item in self.items.all())


class OrderItem(models.Model):

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	order = models.ForeignKey(
		Order,
		on_delete=models.CASCADE,
		related_name="items"
	)

	ticket_type = models.ForeignKey(
		TicketType,
		on_delete=models.CASCADE
	)

	quantity = models.PositiveIntegerField()

	price = models.DecimalField(max_digits=10, decimal_places=2)

	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "main_orderitem"
		unique_together = ("order", "ticket_type")

	def __str__(self):
		return f"{self.quantity} x {self.ticket_type.name}"
