from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apiAuditoria.models import EventoAuditoria


class Command(BaseCommand):
    help = "Aplica retención de auditoría eliminando eventos más antiguos al umbral."

    def add_arguments(self, parser):
        parser.add_argument("--retention-days", type=int, default=180)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        retention_days = options["retention_days"]
        dry_run = options["dry_run"]
        threshold = timezone.now() - timedelta(days=retention_days)
        queryset = EventoAuditoria.objects.filter(fecha_evento__lt=threshold)
        total = queryset.count()
        if dry_run:
            self.stdout.write(self.style.WARNING(f"[dry-run] eventos para eliminar: {total}"))
            return
        deleted, _ = queryset.delete()
        self.stdout.write(self.style.SUCCESS(f"eventos eliminados: {deleted}"))

