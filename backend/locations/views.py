from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from locations.models import Address, Department, Municipality
from locations.serializers import (
    AddressSerializer,
    AddressWriteSerializer,
    DepartmentSerializer,
    MunicipalitySerializer,
)


class DepartmentListView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]


class MunicipalityListView(generics.ListAPIView):
    serializer_class = MunicipalitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Municipality.objects.select_related('department')
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        return queryset


class AddressListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).select_related(
            'municipality__department',
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddressWriteSerializer
        return AddressSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        address = Address.objects.select_related('municipality__department').get(
            pk=write_serializer.save().pk,
        )
        read_serializer = AddressSerializer(address)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).select_related(
            'municipality__department',
        )

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return AddressWriteSerializer
        return AddressSerializer
