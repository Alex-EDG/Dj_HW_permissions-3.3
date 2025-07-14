from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from advertisements.permissions import IsOwnerOrAdminOnly
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from advertisements.models import Advertisement, Favorite
from advertisements.serializers import AdvertisementSerializer


class AdvertisementFilter(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter()

    class Meta:
        model = Advertisement
        fields = ['title', 'description', 'status', 'creator', 'created_at']


class AdvertisementViewSet(viewsets.ModelViewSet):
    """ViewSet для объявлений."""

    # TODO: настройте ViewSet, укажите атрибуты для кверисета,
    #   сериализаторов и фильтров

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AdvertisementFilter
    search_fields = ['title', 'description', 'status', 'creator']
    ordering_fields = ['title', 'status', 'created_at']
    pagination_class = LimitOffsetPagination
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_queryset(self):

        queryset = Advertisement.objects.filter(~Q(status="DRAFT") | Q(status="DRAFT") & Q(creator__id=self.request.user.id))

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return super().list(request, *args, **kwargs)


    def get_permissions(self):
        """Получение прав для действий."""

        if self.action in ["create"]:
            return [IsAuthenticated()]

        if self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrAdminOnly()]

        return []

    @action(methods=["get"], detail=True, url_path="favorite", url_name="favorite", permission_classes=[IsAuthenticated,])
    def get_favorite(self, request, pk=None):

        instance = self.get_object()

        if instance.creator.id == request.user.id:
            raise ValidationError('Собственные объявления нельзя добавить в избранное')
        else:
            favorite_obj, created = Favorite.objects.get_or_create(
                user_id=request.user.id,
                advertisement_id=pk
            )
        if created:
            return Response(
                {'message': 'Контент добавлен в избранное'},
                status=status.HTTP_201_CREATED
            )
        else:
            favorite_obj.delete()
            return Response(
                {'message': 'Контент удален из избранного'},
                status=status.HTTP_200_OK
            )

    @action(methods=["get"], detail=False, url_path="favorites", url_name="favorites",
            permission_classes=[IsAuthenticated, ])
    def get_favorites(self, request, *args, **kwargs):
        favorites = self.queryset.filter(favorites__user_id=request.user.id)
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)