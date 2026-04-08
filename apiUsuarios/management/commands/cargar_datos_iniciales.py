"""
Management command para cargar datos iniciales en el sistema ERP
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from apiUsuarios.models import Usuario, PerfilSocio
from apiInventario.models import Producto
from apiTransacciones.models import Categoria
from apiBancos.models import Banco
from apiCuentas.models.cuenta_model import Cuenta


class Command(BaseCommand):
    help = 'Carga datos iniciales para el sistema ERP'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando carga de datos iniciales...\n'))

        # 1. Crear usuarios de ejemplo
        self.stdout.write('📝 Creando usuarios...')
        self.crear_usuarios()

        # 2. Crear categorías empresariales
        self.stdout.write('📂 Creando categorías...')
        self.crear_categorias()

        # 3. Crear bancos y cuentas
        self.stdout.write('🏦 Creando bancos y cuentas...')
        self.crear_bancos_cuentas()

        # 4. Crear productos de ejemplo
        self.stdout.write('📦 Creando productos...')
        self.crear_productos()

        self.stdout.write(self.style.SUCCESS('\n✅ Datos iniciales cargados exitosamente!'))
        self.mostrar_resumen()

    def crear_usuarios(self):
        """Crear usuarios de ejemplo de cada rol"""
        
        # Admin ya existe, solo crear los demás
        usuarios_crear = [
            {
                'username': 'cliente1',
                'email': 'cliente1@eft.com',
                'password': 'cliente123',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'rol': 'CLIENTE',
                'telefono': '555-0001'
            },
            {
                'username': 'socio1',
                'email': 'socio1@eft.com',
                'password': 'socio123',
                'first_name': 'María',
                'last_name': 'González',
                'rol': 'SOCIO',
                'telefono': '555-0002'
            },
            {
                'username': 'interno1',
                'email': 'interno1@eft.com',
                'password': 'interno123',
                'first_name': 'Carlos',
                'last_name': 'Ramírez',
                'rol': 'INTERNO',
                'telefono': '555-0003'
            },
        ]

        for user_data in usuarios_crear:
            username = user_data.pop('username')
            password = user_data.pop('password')
            
            if not Usuario.objects.filter(username=username).exists():
                usuario = Usuario.objects.create_user(
                    username=username,
                    password=password,
                    **user_data
                )
                self.stdout.write(f'  ✓ Usuario creado: {username} ({usuario.get_rol_display()})')

                # Crear perfil de socio si aplica
                if usuario.rol == 'SOCIO':
                    PerfilSocio.objects.create(
                        usuario=usuario,
                        porcentaje_anticipo=Decimal('30.00'),
                        limite_credito=Decimal('50000.00'),
                        descuento_especial=Decimal('10.00')
                    )
                    self.stdout.write(f'    → Perfil de socio creado para {username}')

    def crear_categorias(self):
        """Crear categorías empresariales"""
        categorias = [
            {'nombre': 'Ventas Productos', 'descripcion': 'Ingresos por venta de productos', 'egreso': False, 'tipo': 'VENTA'},
            {'nombre': 'Compras Inventario', 'descripcion': 'Gastos en compra de inventario', 'egreso': True, 'tipo': 'COSTO'},
            {'nombre': 'Nóminas', 'descripcion': 'Pagos de nómina a empleados', 'egreso': True, 'tipo': 'NOMINA'},
            {'nombre': 'Impuestos', 'descripcion': 'Pago de impuestos', 'egreso': True, 'tipo': 'IMPUESTOS'},
            {'nombre': 'Servicios', 'descripcion': 'Pago de servicios (luz, agua, internet)', 'egreso': True, 'tipo': 'COSTO'},
            {'nombre': 'Otros Ingresos', 'descripcion': 'Otros ingresos varios', 'egreso': False, 'tipo': 'GENERAL'},
        ]

        for cat_data in categorias:
            categoria, created = Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  ✓ Categoría: {categoria.nombre} ({categoria.get_tipo_display()})')

    def crear_bancos_cuentas(self):
        """Crear bancos y cuentas de ejemplo"""
        bancos_data = [
            'Banco Nacional',
            'Banco Popular',
            'Banco Comercial'
        ]

        for nombre_banco in bancos_data:
            banco, created = Banco.objects.get_or_create(nombre=nombre_banco)
            if created:
                self.stdout.write(f'  ✓ Banco: {banco.nombre}')

        # Crear cuenta principal
        banco_principal = Banco.objects.first()
        cuenta, created = Cuenta.objects.get_or_create(
            numero=1001,
            defaults={
                'banco': banco_principal,
                'saldo': Decimal('100000.00'),
                'nombre': 'Cuenta Principal Empresa'
            }
        )
        if created:
            self.stdout.write(f'  ✓ Cuenta creada: {cuenta.nombre} con saldo ${cuenta.saldo}')

    def crear_productos(self):
        """Crear productos de ejemplo"""
        productos = [
            {
                'nombre': 'Laptop Dell Inspiron 15',
                'sku': 'LAP-DELL-001',
                'descripcion': 'Laptop Dell Inspiron 15, 8GB RAM, 256GB SSD',
                'precio_base': Decimal('15000.00'),
                'porcentaje_impuesto': Decimal('16.00'),
                'stock_actual': 10,
                'stock_minimo': 3
            },
            {
                'nombre': 'Mouse Inalámbrico Logitech',
                'sku': 'MOU-LOG-001',
                'descripcion': 'Mouse inalámbrico Logitech MX Master 3',
                'precio_base': Decimal('1200.00'),
                'porcentaje_impuesto': Decimal('16.00'),
                'stock_actual': 25,
                'stock_minimo': 5
            },
            {
                'nombre': 'Teclado Mecánico RGB',
                'sku': 'TEC-RGB-001',
                'descripcion': 'Teclado mecánico RGB con switches azules',
                'precio_base': Decimal('2500.00'),
                'porcentaje_impuesto': Decimal('16.00'),
                'stock_actual': 15,
                'stock_minimo': 5
            },
            {
                'nombre': 'Monitor LG 27" 4K',
                'sku': 'MON-LG-001',
                'descripcion': 'Monitor LG 27 pulgadas, resolución 4K UHD',
                'precio_base': Decimal('8500.00'),
                'porcentaje_impuesto': Decimal('16.00'),
                'stock_actual': 8,
                'stock_minimo': 2
            },
            {
                'nombre': 'Webcam Logitech HD',
                'sku': 'CAM-LOG-001',
                'descripcion': 'Webcam Logitech C920 Full HD 1080p',
                'precio_base': Decimal('1800.00'),
                'porcentaje_impuesto': Decimal('16.00'),
                'stock_actual': 20,
                'stock_minimo': 5
            },
        ]

        for prod_data in productos:
            producto, created = Producto.objects.get_or_create(
                sku=prod_data['sku'],
                defaults=prod_data
            )
            if created:
                precio_final = producto.precio_con_impuesto()
                self.stdout.write(f'  ✓ Producto: {producto.nombre} | Precio: ${precio_final:.2f} | Stock: {producto.stock_actual}')

    def mostrar_resumen(self):
        """Mostrar resumen de datos cargados"""
        self.stdout.write(self.style.SUCCESS('\n📊 RESUMEN DE DATOS CARGADOS:'))
        self.stdout.write(f'  • Usuarios: {Usuario.objects.count()}')
        self.stdout.write(f'  • Categorías: {Categoria.objects.count()}')
        self.stdout.write(f'  • Bancos: {Banco.objects.count()}')
        self.stdout.write(f'  • Cuentas: {Cuenta.objects.count()}')
        self.stdout.write(f'  • Productos: {Producto.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\n🔑 CREDENCIALES DE ACCESO:'))
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Cliente: cliente1 / cliente123')
        self.stdout.write('  Socio: socio1 / socio123')
        self.stdout.write('  Interno: interno1 / interno123')
