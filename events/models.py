import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.db.models import Min, Max
from users.models import Organizer

TICKET_PRICE_OPTIONS = [
    Decimal("500000.00"),
    Decimal("1000000.00"),
    Decimal("1500000.00"),
]

TICKET_PRICE_CHOICES = [
    (TICKET_PRICE_OPTIONS[0], "500000 VND"),
    (TICKET_PRICE_OPTIONS[1], "1000000 VND"),
    (TICKET_PRICE_OPTIONS[2], "1500000 VND"),
]

# VENUE
class Venue(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

# CATEGORY
class Category(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    slug = models.SlugField(max_length=100, unique=True, db_index=True)

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# EVENT
class Event(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    slug = models.SlugField(unique=True, db_index=True)
    name = models.CharField(max_length=200)

    image = models.CharField(max_length=255, blank=True, null=True)

    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name="events"
    )

    organizer = models.ForeignKey(
        Organizer,
        on_delete=models.CASCADE,
        related_name="events"
    )

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_events"
    )

    approved_at = models.DateTimeField(blank=True, null=True)

    categories = models.ManyToManyField(
        Category,
        through="EventCategory",
        related_name="events"
    )

    def __str__(self):
        return self.name

    # Properties
    @property
    def min_price(self):
        return self.ticket_types.aggregate(
            Min("price")
        )["price__min"]

    @property
    def max_price(self):
        return self.ticket_types.aggregate(
            Max("price")
        )["price__max"]

# EVENT CATEGORY 
class EventCategory(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("event", "category")

# TICKET TYPE
class TicketType(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="ticket_types"
    )

    name = models.CharField(max_length=100)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        choices=TICKET_PRICE_CHOICES,
    )

    quantity_total = models.IntegerField()
    quantity_sold = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "price"],
                name="unique_ticket_price_per_event",
            ),
            models.CheckConstraint(
                condition=models.Q(price__in=TICKET_PRICE_OPTIONS),
                name="ticket_price_is_allowed_option",
            ),
        ]

    def __str__(self):
        return f"{self.event.name} - {self.name}"
    
    # Properties
    @property
    def quantity_available(self):
        return self.quantity_total - self.quantity_sold
