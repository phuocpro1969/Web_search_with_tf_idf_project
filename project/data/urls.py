from rest_framework import routers

from data.api import DataViewSet

router = routers.DefaultRouter()
router.register('api/data', DataViewSet, 'data')

urlpatterns = router.urls
