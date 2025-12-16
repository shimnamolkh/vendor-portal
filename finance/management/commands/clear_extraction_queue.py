from django.core.management.base import BaseCommand
from finance.models import ExtractionTask


class Command(BaseCommand):
    help = 'Clear all extraction tasks from the queue'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all extraction tasks',
        )

    def handle(self, *args, **options):
        # Get all extraction tasks
        tasks = ExtractionTask.objects.all()
        total_count = tasks.count()
        
        if total_count == 0:
            self.stdout.write(self.style.WARNING('No extraction tasks found.'))
            return
        
        # Count by status
        pending_count = tasks.filter(status='pending').count()
        processing_count = tasks.filter(status='processing').count()
        completed_count = tasks.filter(status='completed').count()
        failed_count = tasks.filter(status='failed').count()
        
        # Show summary
        self.stdout.write('\n📊 Extraction Tasks Summary:')
        self.stdout.write(f'   Total tasks: {total_count}')
        self.stdout.write(f'   Pending: {pending_count}')
        self.stdout.write(f'   Processing: {processing_count}')
        self.stdout.write(f'   Completed: {completed_count}')
        self.stdout.write(f'   Failed: {failed_count}')
        
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  This will DELETE all extraction tasks!'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Run with --confirm flag to proceed:'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'python manage.py clear_extraction_queue --confirm'
                )
            )
            return
        
        # Delete all tasks
        deleted_count, _ = tasks.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully deleted {deleted_count} extraction task(s).'
            )
        )
        self.stdout.write('\n✨ Extraction queue is now empty!')
