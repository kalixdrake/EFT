from django_bolt import Router, Request
from django_bolt.auth import IsAuthenticated
from django_bolt.exceptions import HTTPException
from .models.departamento_model import Departamento
from .models.municipio_model import Municipio
from .models.ubicacion_model import Ubicacion
from .serializers import MunicipioSerializer, DepartamentoSerializer, UbicacionSerializer, UbicacionCreateSerializer
from asgiref.sync import sync_to_async

ubicaciones_router = Router(tags=["Ubicaciones"])

@ubicaciones_router.get("/departamentos")
async def listar_departamentos(request: Request) -> list[DepartamentoSerializer]:
    # Optimize query fetching all at once
    deptos = await sync_to_async(list)(
        Departamento.objects.all().order_by('nombre')
    )
    return deptos

@ubicaciones_router.get("/departamentos/{codigo_dane}/municipios")
async def listar_municipios(request: Request, codigo_dane: str) -> list[MunicipioSerializer]:
    # Optimize fetch with select_related for the nested departament relationship
    municipios = await sync_to_async(list)(
        Municipio.objects.filter(departamento_id=codigo_dane).select_related("departamento").order_by('nombre')
    )
    return municipios

@ubicaciones_router.get("/mis-direcciones", guards=[IsAuthenticated()])
async def listar_mis_ubicaciones(request: Request) -> list[UbicacionSerializer]:
    # prefetch_related could be used for ManyToMany, but here we just need select_related 
    # to avoid the N+1 problem fetching nested `municipio` and its `departamento`.
    qs = Ubicacion.objects.filter(usuario=request.user) \
        .select_related('municipio', 'municipio__departamento')
        
    ubicaciones = await sync_to_async(list)(qs)
    return ubicaciones

@ubicaciones_router.post("/mis-direcciones", guards=[IsAuthenticated()])
async def crear_ubicacion(request: Request, payload: UbicacionCreateSerializer) -> UbicacionSerializer:
    municipio_exists = await Municipio.objects.filter(codigo_dane=payload.municipio_id).aexists()
    if not municipio_exists:
        raise HTTPException(status_code=404, detail="Municipio not found")

    ubicacion = Ubicacion(
        usuario=request.user,
        municipio_id=payload.municipio_id,
        name=payload.name,
        phone=payload.phone,
        street=payload.street,
        postalCode=payload.postalCode,
        latitude=payload.latitude,
        longitude=payload.longitude
    )
    await ubicacion.asave()
    
    # Reload relation fields to return the full payload
    await ubicacion.arefresh_from_db(fields=['municipio_id'])
    
    # Use sync_to_async to select_related safely
    ubicacion_reloded = await sync_to_async(
        lambda: Ubicacion.objects.select_related('municipio__departamento').get(id=ubicacion.id)
    )()
    
    return ubicacion_reloded

@ubicaciones_router.delete("/mis-direcciones/{ubicacion_id}", guards=[IsAuthenticated()])
async def eliminar_ubicacion(request: Request, ubicacion_id: int):
    try:
        ubicacion = await Ubicacion.objects.aget(id=ubicacion_id, usuario=request.user)
    except Ubicacion.DoesNotExist:
        raise HTTPException(status_code=404, detail="Ubicacion not found")
        
    await ubicacion.adelete()
    return {"status": "eliminado", "id": ubicacion_id}
