from datetime import timedelta

from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Delete old Django admin history entries from django_admin_log."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Retention period in days (default from ADMIN_LOG_RETENTION_DAYS or 90).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many rows would be deleted without deleting.",
        )

    def handle(self, *args, **options):
        retention_days = options["days"]
        if retention_days is None:
            retention_days = int(getattr(settings, "ADMIN_LOG_RETENTION_DAYS", 90))
        retention_days = max(retention_days, 1)

        cutoff = timezone.now() - timedelta(days=retention_days)
        queryset = LogEntry.objects.filter(action_time__lt=cutoff)
        delete_count = queryset.count()

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run: {delete_count} django_admin_log rows older than {retention_days} days would be deleted."
                )
            )
            return

        queryset.delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {delete_count} django_admin_log rows older than {retention_days} days."
            )
        )
