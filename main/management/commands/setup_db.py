import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
import shutil

def delete_migration_files(stdout):
    for app_config in apps.get_app_configs():
        # 🚫 Skip third-party apps
        if "site-packages" in app_config.path:
            continue

        migrations_path = os.path.join(app_config.path, "migrations")

        if not os.path.exists(migrations_path):
            continue

        for file in os.listdir(migrations_path):
            file_path = os.path.join(migrations_path, file)

            # ❌ Skip __init__.py
            if file == "__init__.py":
                continue

            # 🧹 Remove __pycache__
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
                stdout.write(f"🗑️ Deleted folder {file_path}")
                continue

            # ✅ Only delete migration-related files
            if file.endswith(".py") or file.endswith(".pyc"):
                try:
                    os.remove(file_path)
                    stdout.write(f"🗑️ Deleted {file_path}")
                except Exception as e:
                    stdout.write(f"⚠️ Could not delete {file_path}: {e}")
                    
def clean_media_folder(stdout):
    media_root = settings.MEDIA_ROOT

    if not os.path.exists(media_root):
        stdout.write("ℹ️ MEDIA_ROOT does not exist, skipping cleanup.")
        return

    for item in os.listdir(media_root):
        item_path = os.path.join(media_root, item)

        # ❌ Skip important placeholder files if needed
        if item in ["default.png", ".gitkeep"]:
            continue

        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
                stdout.write(f"🗑️ Deleted file {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                stdout.write(f"🗑️ Deleted folder {item_path}")
        except Exception as e:
            stdout.write(f"⚠️ Could not delete {item_path}: {e}")
            
class Command(BaseCommand):
    help = "Setup database (makemigrations + migrate + seed)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete database before setup"
        )

    def handle(self, *args, **options):
        db_path = settings.BASE_DIR / "db.sqlite3"

        # 🧨 Optional reset
        if options["reset"]:
            # 🧨 Delete database
            if os.path.exists(db_path):
                self.stdout.write(self.style.WARNING("🧨 Deleting existing database..."))
                os.remove(db_path)
            else:
                self.stdout.write("ℹ️ No database file found, skipping delete.")

            # 🧹 Delete migration files
            self.stdout.write(self.style.WARNING("🧹 Deleting migration files..."))
        
            delete_migration_files(self.stdout)

            # 🧹 Clean media files
            self.stdout.write(self.style.WARNING("🧹 Cleaning media folder..."))

            clean_media_folder(self.stdout)

        # 🆕 MAKE MIGRATIONS
        self.stdout.write("🛠️ Making migrations...")
        call_command("makemigrations")

        # 📦 APPLY MIGRATIONS
        self.stdout.write("📦 Applying migrations...")
        call_command("migrate")

        # 🌱 SEED DATA
        self.stdout.write("🌱 Seeding database...")
        call_command("seed_data")

        # ✅ DONE
        self.stdout.write(self.style.SUCCESS("✅ Database setup complete!"))
        
