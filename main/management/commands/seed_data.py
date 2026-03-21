import json
import random
from datetime import datetime
from django.utils import timezone

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

from users.models import Organizer
from events.models import Event, Venue, TicketType, Category

User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with real dataset"

    def handle(self, *args, **kwargs):

        # LOAD JSON
        events_file = settings.BASE_DIR / "data" / "events.json"

        with open(events_file, encoding="utf-8") as f:
            events_data = json.load(f)

        # CUSTOMERS
        customers = []
        for i in range(20):
            user, created = User.objects.get_or_create(
                username = f"customer{i+1}",
                defaults = {
                    "email": f"customer{i+1}@gmail.com",
                    "is_staff": False
                }
            )

            if created:
                user.set_password("password123")
                user.save()
            if not user.email:
                user.email = f"customer{i+1}@gmail.com"
                user.save()
                
            customers.append(user)
    
        # ADMINS
        admins = []
        for i in range(2):
            user, created = User.objects.get_or_create(
                username = f"admin{i+1}",
                defaults = {
                    "email": f"admin{i+1}@gmail.com",
                    "is_staff": True
                    }
            )

            if created:
                user.set_password("password123")
                user.save()
            if not user.email:
                user.email = f"admin{i+1}@gmail.com"
                user.save()

            admins.append(user)

        # ORGANIZERS
        organizers = []
        for i in range(10):
            user, created = User.objects.get_or_create(
                username=f"organizer{i+1}",
                defaults={
                    "email": f"organizer{i+1}@gmail.com",
                    "is_staff": False
                }
            )

            if created:
                user.set_password("password123")
                user.save()
            else:
                if not user.email:
                    user.email = f"organizer{i+1}@gmail.com"
                    user.save()

            organizer, created = Organizer.objects.get_or_create(
                user=user,
                defaults={
                    "display_name": f"Organizer{i+1}"
                }
            )

            if not organizer.display_name:
                organizer.display_name = f"Organizer{i+1}"
                organizer.save()

            organizers.append(organizer)

        # CATEGORIES
        category_map = {
            "nhac-song": "Nhạc sống",
            "san-khau-nghe-thuat": "Sân khấu nghệ thuật",
            "hoi-thao-workshop": "Hội thảo & Workshop",
            "tham-quan-trai-nghiem": "Tham quan & Trải nghiệm",
            "the-thao": "Thể thao",
            "khac": "Khác"
        }

        category_objs = {}
        for slug, name in category_map.items():
            category, _ = Category.objects.get_or_create(
                slug = slug,
                defaults = {"name": name}
            )
            category_objs[slug] = category

        # STATUS
        statuses = ["approved"] * 24 + ["pending"] * 3 + ["rejected"] * 3

        # IMPORT EVENTS
        for i, (key, data) in enumerate(events_data.items()):
            city = None
            address = None
            
            # PARSE ADDRESS 
            parts = [p.strip() for p in data["dcCuThe"].split(",")]

            if len(parts) > 1:
                city = parts[-1]
                address = ", ".join(parts[:-1])
            else:
                city = parts[0]
                address = ""

            # PARSE DATE/TIME 
            date = datetime.strptime(data["date"], "%Y-%m-%d").date()

            start_time = (
                datetime.strptime(data["startTime"], "%H:%M").time()
                if data.get("startTime") else None
            )

            end_time = (
                datetime.strptime(data["endTime"], "%H:%M").time()
                if data.get("endTime") else None
            )

            # VENUE 
            venue, _ = Venue.objects.get_or_create(
                name = data["dcTen"],
                city = city,
                defaults = {
                    "address": address,
                    "capacity": 1000
                }
            )

            status = statuses[i]

            # EVENT 
            event, created = Event.objects.get_or_create(
                slug = key,
                defaults = {
                    "name": data["ten"],
                    "description": data["moTa"],
                    "image": data["anh"],
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "venue": venue,
                    "organizer": random.choice(organizers),
                    "status": status,
                    "approved_by": random.choice(admins) if status == "approved" else None,
                    "approved_at": timezone.now() if status == "approved" else None,
                }
            )

            # UPDATE IF EXISTS 
            if not created:
                event.name = data["ten"]
                event.description = data["moTa"]
                event.image = data["anh"]
                event.date = date
                event.start_time = start_time
                event.end_time = end_time
                event.venue = venue
                event.status = status

                if status == "approved":
                    event.approved_by = random.choice(admins)
                    event.approved_at = timezone.now()
                else:
                    event.approved_by = None
                    event.approved_at = None

                event.save()

            # CATEGORIES 
            event.categories.clear()
            for cat_slug in data["categories"]:
                if cat_slug in category_objs:
                    event.categories.add(category_objs[cat_slug])

            # TICKETS 
            event.ticket_types.all().delete()

            for ticket in data["tickets"]:
                TicketType.objects.create(
                    event=event,
                    name=ticket["loai"],
                    price=ticket["gia"],
                    quantity_total=200,
                    quantity_sold=random.randint(0, 100)
                )

        self.stdout.write(self.style.SUCCESS("✅ Database seeded successfully"))