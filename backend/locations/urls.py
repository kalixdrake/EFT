from django.urls import path

from locations.views import (
    AddressDetailView,
    AddressListCreateView,
    DepartmentListView,
    MunicipalityListView,
)

urlpatterns = [
    path('departments/', DepartmentListView.as_view(), name='department-list'),
    path('municipalities/', MunicipalityListView.as_view(), name='municipality-list'),
    path('addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
]
