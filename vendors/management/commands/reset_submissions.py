from django.core.management.base import BaseCommand
from vendors.models import Submission


class Command(BaseCommand):
    help = 'Reset all submissions to pending status (as if just submitted by vendors)'

    def handle(self, *args, **options):
        # Get all submissions
        submissions = Submission.objects.all()
        total_count = submissions.count()
        
        if total_count == 0:
            self.stdout.write(self.style.WARNING('No submissions found.'))
            return
        
        # Reset all to pending
        updated_count = submissions.update(
            status='pending',
            verified_by=None,
            verification_notes='',
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully reset {updated_count} submission(s) to pending status.'
            )
        )
        
        # Show summary
        self.stdout.write('\n📊 Summary:')
        self.stdout.write(f'   Total submissions: {total_count}')
        self.stdout.write(f'   Reset to pending: {updated_count}')
        self.stdout.write('\n✨ All submissions are now in "pending" state, ready for finance review!')
