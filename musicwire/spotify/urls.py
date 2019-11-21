from django.urls import path

from musicwire.spotify import views

urlpatterns = [
    path('saved_tracks',
         views.SavedTracksView.as_view(),
         name='update_booking_data'),
]
