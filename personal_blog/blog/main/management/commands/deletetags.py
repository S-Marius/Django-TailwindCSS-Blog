from django.core.management.base import BaseCommand
from taggit.models import Tag

class Command(BaseCommand):
    help = 'Remove tags without associated objects'

    def handle(self, *args, **options):
        self.stdout.write("Removing tags without associated objects...")

        # Fetch tags that have no associated objects using bulk delete
        tags_to_delete = Tag.objects.filter(taggit_taggeditem_items__isnull=True)

        # Check if there are any tags to delete
        if tags_to_delete.exists():
            # Perform the bulk delete operation
            num_deleted_tags, _ = tags_to_delete.delete()

            self.stdout.write(self.style.SUCCESS(f'Successfully removed {num_deleted_tags} tags without associated objects'))
        else:
            self.stdout.write(self.style.SUCCESS('No tags found without associated objects'))
