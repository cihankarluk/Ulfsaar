import logging
from datetime import timedelta

from celery.schedules import crontab
from celery.task import periodic_task

from musicwire.core.exceptions import ProviderResponseError
from musicwire.music.models import Playlist, CreatedPlaylist
from musicwire.provider.models import Provider
from musicwire.transfer.models import TransferError

logger = logging.getLogger(__name__)


@periodic_task(run_every=(crontab(hour=15, minute=55)))
def transfer_playlists_task(source_slug, source_token, end_slug, end_token, user):
    adapter = Provider.get_provider(
        provider=source_slug,
        token=source_token,
        user=user
    )
    import ipdb
    ipdb.set_trace()
    # Create all playlists in database
    adapter.playlists()
    if source_slug == Provider.SPOTIFY:
        try:
            Playlist.objects.get(
                remote_id=adapter.saved_tracks_id,
                user=user
            )
        except Playlist.DoesNotExist:
            saved_tracks_playlist = Playlist(
                name="saved_tracks",
                status="private",
                remote_id=adapter.saved_tracks_id,
                content=None,
                provider=Provider.SPOTIFY,
                user=user
            )
            saved_tracks_playlist.save()

    # Pull all created playlists from db and send request to end point to create.
    adapter = Provider.get_provider(
        provider=end_slug,
        token=end_token,
        user=user
    )

    playlists = Playlist.objects.filter(
        user=user,
        provider=source_slug,
        is_transferred=False
    )

    for playlist in playlists:
        playlist_data = {
            "playlist_name": playlist.name,
            "privacy_status": playlist.status,
        }
        try:
            adapter.create_playlist(**playlist_data)
            playlist.is_transferred = True
            playlist.save()
        except ProviderResponseError as pre:
            logger.warning(pre)
            TransferError.objects.create(
                request_data=playlist_data,
                error=pre,
                source=source_slug,
                end=end_slug,
                type=TransferError.PLAYLIST,
                user=user
            )
            continue


@periodic_task(run_every=(crontab(hour=0, minute=0)))
def transfer_tracks_task(source_slug, source_token, end_slug, end_token, user):
    adapter = Provider.get_provider(
        provider=source_slug,
        token=source_token,
        user=user
    )

    # Get all playlists of user and get tracks of those playlists.
    playlists = Playlist.objects.filter(
        user=user,
        provider=source_slug
    )

    for playlist in playlists:
        playlist_remote_id = playlist.remote_id
        try:
            if playlist_remote_id == "spotify_saved_tracks":
                adapter.saved_tracks(playlist_id=playlist_remote_id)
            else:
                adapter.playlist_tracks(playlist_id=playlist_remote_id)
        except ProviderResponseError as pre:
            logger.warning(pre)
            TransferError.objects.create(
                request_data={"playlist_id": playlist_remote_id},
                error=pre,
                source=source_slug,
                end=end_slug,
                type=TransferError.PLAYLIST,
                user=user
            )
            continue

    # Search inserted tracks and try to upload them.
    adapter = Provider.get_provider(
        provider=end_slug,
        token=end_token,
        user=user
    )
    created_playlists = CreatedPlaylist.objects.filter(
        user=user,
        provider=end_slug
    )

    for created_playlist in created_playlists:
        playlist = Playlist.objects.prefetch_related(
            "playlisttrack_set"
        ).get(name=created_playlist.name, provider=source_slug)
        tracks = playlist.playlisttrack_set.filter(is_transferred=False)
        for track in tracks:
            try:
                response = adapter.search(track.name)
                adapter.add_track_to_playlist(
                    playlist_id=created_playlist.remote_id,
                    track_id=response['id']
                )
            except ProviderResponseError as pre:
                logger.warning(pre)
                # In search part it create search error.
                continue
