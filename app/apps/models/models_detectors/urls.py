from django.urls import path

from .api import views

urlpatterns = [
    path(
        "detectors/retinanet-bird-lite/",
        views.RetinaNetBirdLiteModelView.as_view(),
        name="detectors-retinanet-bird-lite",
    ),
]
