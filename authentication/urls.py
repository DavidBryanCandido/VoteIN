from django.urls import path, include
from .views import RegisterView, ProtectedView, PositionViewSet, PartyListViewSet, ElectionViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'positions', PositionViewSet, basename='position')
router.register(r'partylists', PartyListViewSet, basename='partylist')
router.register(r'elections', ElectionViewSet, basename='election')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('', include(router.urls)),
]
