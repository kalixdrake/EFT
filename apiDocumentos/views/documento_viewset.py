from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apiUsuarios.permissions import IsAdministradorOrInterno, RoleScopePermission, scope_queryset
from apiUsuarios.rbac_contracts import Actions, Resources

from ..models import AccesoDocumento, Documento, VersionDocumento
from ..serializers import DocumentoSerializer, VersionDocumentoSerializer


class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.select_related(
        "tipo_documento",
        "propietario_empleado__usuario",
        "propietario_cliente__usuario",
        "propietario_socio__usuario",
        "usuario_creador",
        "usuario_actualizador",
    ).all()
    serializer_class = DocumentoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.DOCUMENTO
    rbac_action_map = {
        "versiones": Actions.READ,
        "descargar": Actions.READ,
        "visualizar": Actions.READ,
    }
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["tipo_documento", "estado", "propietario_empresa", "fecha_vencimiento"]
    search_fields = ["codigo", "titulo", "descripcion"]
    ordering_fields = ["fecha_creacion", "fecha_actualizacion", "fecha_vencimiento", "ultima_version"]
    ordering = ["-fecha_actualizacion"]

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        if scope in ("COMPANY", "GLOBAL"):
            return queryset

        scoped_by_user = scope_queryset(queryset, self.request.user, scope)
        extra_qs = queryset.none()

        if hasattr(self.request.user, "cliente"):
            extra_qs = queryset.filter(propietario_cliente=self.request.user.cliente)
        elif hasattr(self.request.user, "empleado"):
            extra_qs = queryset.filter(propietario_empleado=self.request.user.empleado)
        elif hasattr(self.request.user, "socio"):
            extra_qs = queryset.filter(propietario_socio=self.request.user.socio)

        return (scoped_by_user | extra_qs).distinct()

    def perform_create(self, serializer):
        documento = serializer.save(
            usuario_creador=self.request.user,
            usuario_actualizador=self.request.user,
        )
        VersionDocumento.objects.create(
            documento=documento,
            numero_version=1,
            archivo=documento.archivo_actual,
            hash_contenido=documento.hash_contenido,
            observaciones="Version inicial",
            usuario_editor=self.request.user,
        )

    def perform_update(self, serializer):
        with transaction.atomic():
            original = self.get_object()
            archivo_prev = original.archivo_actual
            hash_prev = original.hash_contenido
            version_prev = original.ultima_version

            documento = serializer.save(usuario_actualizador=self.request.user)
            archivo_cambio = "archivo_actual" in serializer.validated_data
            hash_cambio = "hash_contenido" in serializer.validated_data and serializer.validated_data["hash_contenido"] != hash_prev

            if archivo_cambio or hash_cambio:
                VersionDocumento.objects.create(
                    documento=documento,
                    numero_version=version_prev + 1,
                    archivo=documento.archivo_actual,
                    hash_contenido=documento.hash_contenido,
                    observaciones=serializer.validated_data.get("descripcion", ""),
                    usuario_editor=self.request.user,
                )
                documento.ultima_version = version_prev + 1
                documento.save(update_fields=["ultima_version", "fecha_actualizacion"])
            elif archivo_prev != documento.archivo_actual:
                VersionDocumento.objects.create(
                    documento=documento,
                    numero_version=version_prev + 1,
                    archivo=documento.archivo_actual,
                    hash_contenido=documento.hash_contenido,
                    observaciones="Actualizacion de archivo",
                    usuario_editor=self.request.user,
                )
                documento.ultima_version = version_prev + 1
                documento.save(update_fields=["ultima_version", "fecha_actualizacion"])

    def _registrar_acceso(self, documento, tipo_evento):
        version = documento.versiones.filter(numero_version=documento.ultima_version).first()
        AccesoDocumento.objects.create(
            documento=documento,
            version_documento=version,
            usuario=self.request.user,
            tipo_evento=tipo_evento,
            ip_origen=self.request.META.get("REMOTE_ADDR"),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
        )

    @action(detail=True, methods=["get"])
    def versiones(self, request, pk=None):
        documento = self.get_object()
        queryset = documento.versiones.all()
        serializer = VersionDocumentoSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def visualizar(self, request, pk=None):
        documento = self.get_object()
        self._registrar_acceso(documento, AccesoDocumento.TipoEvento.VISUALIZACION)
        serializer = self.get_serializer(documento)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def descargar(self, request, pk=None):
        documento = self.get_object()
        self._registrar_acceso(documento, AccesoDocumento.TipoEvento.DESCARGA)
        serializer = self.get_serializer(documento)
        return Response(
            {
                "documento": serializer.data,
                "descarga_registrada": True,
                "version_descargada": documento.ultima_version,
            },
            status=status.HTTP_200_OK,
        )

