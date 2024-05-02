import subprocess
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = "Backup the database"

    def handle(self, *args, **options):
        try:
            # Generate a timestamp for the filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Construct the filename with the timestamp
            filename = f"backup-{timestamp}.json"

            # Get the backup directory from settings or use a default value
            backup_directory = getattr(settings, "BACKUP_DIRECTORY", "backups")

            # Ensure the backup directory exists, create it if necessary
            os.makedirs(backup_directory, exist_ok=True)

            # Construct the full path to the backup file
            backup_path = os.path.join(backup_directory, filename)

            # Run the command
            subprocess.run(
                f"python -Xutf8 manage.py dumpdata --exclude auth.permission --exclude contenttypes --exclude sessions.Session --exclude admin.logentry > {backup_path}",
                shell=True,
                check=True,
                text=True,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Database backed up successfully. File saved at: {backup_path}"
                )
            )
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"Error during command execution: {e}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Unexpected error: {e}"))
