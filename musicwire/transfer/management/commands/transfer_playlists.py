from django.core.management import BaseCommand

from musicwire.transfer.tasks import transfer_playlists_task


class Command(BaseCommand):
    help = 'Transfer playlists from source to end.'

    def add_arguments(self, parser):
        parser.add_argument('source', type=str)
        parser.add_argument('source_token', type=str)
        parser.add_argument('end', type=str)
        parser.add_argument('end_token', type=str)

    def handle(self, *args, **options):
        source_slug = options['source']
        source_token = options['source_token']
        end_slug = options['end']
        end_token = options['end_token']
        transfer_playlists_task(source_slug, source_token, end_slug, end_token)
