# 📜 Plan de integración frontend — Fases 3 y 4 (Pagos Bold Embedded + Skydropx + Tracking)

## 🎯 Objetivo general

Ampliar la aplicación React Native/Expo **existente** para completar el flujo de compra de principio a fin con la pasarela Bold en modo **Embedded Checkout** (iframe dentro del sitio, sin redirigir al comprador fuera de la app) y envíos vía Skydropx. La app ya tiene construidos los componentes base (ShippingSelector, PaymentMethodSelector, BoldPaymentButton estilizado, CheckoutScreen con flujo, OrderDetailScreen con tracking, y las pantallas OrdersScreen/HomeScreen/CartScreen). El backend ya expone todos los endpoints necesarios.

---

## 📦 Backend: lo que YA existe (no tocar)

| Endpoint | Descripción |
|---|---|
| `POST /api/shipping/quote/` | Recibe `cart_items`, `destination_city`, `destination_postal_code`. Devuelve `quotes[]` (carrier, service, estimated_days, cost_cop, cost_after_credit, quote_id), `weight_kg`, `shipping_credit_available`, `dimensions`. |
| `POST /api/orders/create/` | Recibe `address_id`, `shipping_quote_id`, `payment_method` ("bold" \| "cod"), `notes`. Crea Order + Payment, calcula crédito de envío. **Si payment_method=bold**: devuelve `bold_data` con `order_reference`, `amount_cents`, `currency`, `integrity_hash`, `redirect_url`, `checkout_url`, `public_key`. **Si payment_method=cod**: devuelve `bold_data: null` y dispara guía inmediatamente. |
| `GET /api/orders/` | Lista órdenes del usuario con `order_number`, `status`, `total`, `address`, `payment_status`, `shipment_status`, `shipping_cost`, `is_free_shipping`. |
| `GET /api/orders/<id>/` | Detalle con `items[]`, `subtotal`, `shipment` (carrier, tracking_number, label_url, status), `payment_status`. |
| `GET /api/orders/<id>/tracking/` | Tracking vía Skydropx: `tracking_number`, `carrier`, `current_status`, `estimated_delivery`, `events[]`. |
| `POST /api/payments/webhook/` | Recibe webhook de Bold, valida firma SHA256, actualiza Order → CONFIRMED, dispara Celery task `crear_guia_envio`. |

**Servicio Bold en backend** (`payments/services/bold.py`):
- `calculate_integrity_hash(order_reference, amount_cents, currency)` → SHA256
- `validate_signature(payload_bytes, signature)` → HMAC compare

**Configuración Bold en backend** (`settings.py`):
- `BOLD_PUBLIC_KEY` — llave de identidad (se expone al frontend en `bold_data.public_key`)
- `BOLD_INTEGRITY_SECRET` — NUNCA se expone al frontend
- `BOLD_REDIRECT_URL` — URL de retorno post-pago
- `BOLD_CHECKOUT_URL` — URL del checkout de Bold

---

## 🧩 Lo que YA existe en el frontend (no reescribir desde cero)

### Pantallas
| Pantalla | Archivo | Estado actual |
|---|---|---|
| `HomeScreen` | `src/screens/HomeScreen.js` | ✅ Catálogo con búsqueda y filtros |
| `ProductDetailScreen` | `src/screens/ProductDetailScreen.js` | ✅ Galería, precio, stock, añadir al carrito |
| `CartScreen` | `src/screens/CartScreen.js` | ✅ Lista de items, controles de cantidad, botón checkout |
| `CheckoutScreen` | `src/screens/CheckoutScreen.js` | ✅ Dirección + ShippingSelector + PaymentMethodSelector + resumen + botón pagar/confirmar |
| `OrdersScreen` | `src/screens/OrdersScreen.js` | ✅ Lista de órdenes con `order_number`, status, total |
| `OrderDetailScreen` | `src/screens/OrderDetailScreen.js` | ✅ Detalle con shipping, productos, total, tracking |
| `ProfileScreen` | `src/screens/ProfileScreen.js` | ✅ Perfil y direcciones |
| `AuthScreen` | `src/screens/AuthScreen.js` | ✅ Login/Register |
| `AddressFormScreen` | `src/screens/AddressFormScreen.js` | ✅ CRUD de direcciones |

### Componentes
| Componente | Archivo | Estado actual |
|---|---|---|
| `ShippingSelector` | `src/components/ShippingSelector.js` | ✅ Cotiza vía `POST /api/shipping/quote/`, muestra opciones con crédito y "Envío gratis" |
| `PaymentMethodSelector` | `src/components/PaymentMethodSelector.js` | ✅ Radio buttons Bold vs Contraentrega |
| `BoldPaymentButton` | `src/components/BoldPaymentButton.js` | ⚠️ Actualmente es solo un `<Pressable>` estilizado con texto "Pagar con Bold". **Necesita ser reemplazado** por la integración real con el SDK de Bold en modo Embedded Checkout. |
| `LoadingSpinner` | `src/components/LoadingSpinner.js` | ✅ |
| `ErrorView` | `src/components/ErrorView.js` | ✅ |

### Store (Redux Toolkit)
| Slice | Archivo | Estado actual |
|---|---|---|
| `authSlice` | `src/store/authSlice.js` | ✅ |
| `cartSlice` | `src/store/cartSlice.js` | ✅ |
| `orderSlice` | `src/store/orderSlice.js` | ✅ Thunks: `fetchOrders`, `fetchOrderDetail`, `createOrder`. **Falta**: `pollOrderStatus`. |
| `addressSlice` | `src/store/addressSlice.js` | ✅ Expone `selectedAddressId` |

### API Layer
| Módulo | Archivo | Estado actual |
|---|---|---|
| `apiClient` | `src/api/client.js` | ✅ Axios con interceptors de token y refresh |
| `services` | `src/api/services.js` | ✅ `shippingApi.quote()`, `ordersApi.create()`, `ordersApi.tracking()`, etc. |

### Navegación
| Navigator | Archivo | Estado actual |
|---|---|---|
| `RootNavigator` | `src/navigation/RootNavigator.js` | ✅ GuestStack (Auth) + AuthenticatedStack (MainTabs, ProductDetail, Checkout, OrderDetail, AddressForm) |
| `TabNavigator` | `src/navigation/TabNavigator.js` | ✅ Home, Cart, Orders, Profile |

### Configuración
| Archivo | Estado actual |
|---|---|
| `app.json` | ⚠️ Sin esquema de URL. **Necesita** agregar `scheme` para deep links de Bold. |
| `package.json` | ✅ React 19, Expo ~56, React Navigation 7, Redux Toolkit |

---

## 🔨 CAMBIOS REQUERIDOS (lo que hay que construir/modificar)

---

### 1. `BoldPaymentButton` — REESCRIBIR con Embedded Checkout real ⭐

**Archivo**: `src/components/BoldPaymentButton.js`

**Objetivo**: Integrar el botón de pagos de Bold en modo **Embedded Checkout** (`render-mode="embedded"`). Bold abre un iframe modal dentro de la misma página, sin redirigir al usuario fuera de la app.

**Documentación de referencia**: https://developers.bold.co/pagos-en-linea/boton-de-pagos/integracion-manual/integracion-manual#7-embedded-checkout

**Requisitos**:
- **En web (React Native Web)**: 
  - Inyectar el script de Bold en el `<head>`: `<script src="https://checkout.bold.co/library/boldPaymentButton.js"></script>`
  - Renderizar un tag `<script>` con los atributos `data-bold-button`, `data-api-key`, `data-order-id`, `data-amount`, `data-currency`, `data-integrity-signature`, `data-redirection-url`, `data-render-mode="embedded"`, `data-description`, `data-customer-data`, `data-billing-address`.
  - Usar `useRef` + `useEffect` para insertar el script en el DOM.
  - Escuchar el evento de redirección/postMessage de Bold para detectar cuando el pago finaliza y llamar a `onPaymentComplete`.

- **En móvil (iOS/Android)**:
  - Abrir un `<WebView>` (de `react-native-webview`) que cargue la URL del checkout de Bold (`bold_data.checkout_url`) con los parámetros adecuados.
  - O bien usar `Linking.openURL()` como fallback (el comportamiento actual).
  - Interceptar la navegación del WebView para detectar la URL de retorno (`BOLD_REDIRECT_URL`) y llamar a `onPaymentComplete`.

**Props**:
```typescript
interface BoldPaymentButtonProps {
  publicKey: string;         // data-api-key (BOLD_PUBLIC_KEY)
  orderReference: string;    // data-order-id
  amountCents: number;       // data-amount (en centavos, ej. 95000 para $950 COP)
  currency: string;          // data-currency ("COP")
  integrityHash: string;     // data-integrity-signature
  redirectUrl: string;       // data-redirection-url
  description?: string;      // data-description
  customerData?: {           // data-customer-data (JSON string)
    email?: string;
    fullName?: string;
    phone?: string;
    dialCode?: string;
    documentNumber?: string;
    documentType?: string;
  };
  billingAddress?: {         // data-billing-address (JSON string)
    address?: string;
    zipCode?: string;
    city?: string;
    state?: string;
    country?: string;
  };
  onPaymentComplete: (result: { status: string; orderReference: string }) => void;
  onError?: (error: Error) => void;
  loading?: boolean;
  disabled?: boolean;
}
```

**Comportamiento**:
1. El botón se renderiza como un `<script>` tag de Bold (web) o abre WebView (móvil).
2. Cuando Bold completa el pago, redirige a `BOLD_REDIRECT_URL?bold-order-id=...&bold-tx-status=...`.
3. El componente intercepta esa redirección (en web vía postMessage o URL change; en móvil vía `onNavigationStateChange` del WebView).
4. Llama a `onPaymentComplete({ status, orderReference })`.
5. Mientras se procesa el pago en Bold, muestra un estado de carga.

---

### 2. `PaymentResultScreen` — NUEVA pantalla ⭐

**Archivo**: `src/screens/PaymentResultScreen.js`

**Objetivo**: Pantalla intermedia post-pago que hace polling del estado de la orden hasta que el webhook de Bold la confirme.

**Props vía route params**:
```typescript
interface PaymentResultParams {
  orderId: number;
  status: string; // "success" | "failed" | "pending" (según el parámetro de Bold)
}
```

**Comportamiento**:
1. Al montarse, inicia `pollOrderStatus(orderId)` — llama `GET /api/orders/<id>/` cada 5 segundos.
2. Muestra un spinner con mensaje "Confirmando tu pago…" mientras el estado sea `pending`.
3. Cuando el estado cambia a `confirmed`: muestra ✅ "¡Pago confirmado!" con resumen de la orden y botón "Ver pedido" → navega a `OrderDetail`.
4. Cuando el estado cambia a `cancelled`: muestra ❌ "El pago no pudo ser procesado" con botón "Reintentar pago" → vuelve a `Checkout` o genera nuevo `integrity_hash`.
5. Timeout después de 2 minutos: muestra advertencia de que el pago puede estar en proceso y sugiere revisar el detalle de la orden más tarde.
6. El intervalo de polling se limpia al desmontar (`useEffect` cleanup con `clearInterval`).

---

### 3. `shippingSlice` — NUEVO slice de Redux ⭐

**Archivo**: `src/store/shippingSlice.js`

**Objetivo**: Mover el estado de cotizaciones de envío del estado local del componente `ShippingSelector` a Redux global para que persista entre navegaciones y sea accesible desde `CheckoutScreen` y `PaymentResultScreen`.

```javascript
// Estado
{
  quotes: [],             // Array de opciones de envío
  selectedQuoteId: null,  // quote_id seleccionado
  meta: null,             // { weight, dimensions, credit }
  loading: false,
  error: null,
}

// Thunks
fetchShippingQuotes({ cartItems, destination }) → POST /api/shipping/quote/

// Acciones
setSelectedQuote(quoteId)
clearQuotes()
```

**Integración**: `ShippingSelector` debe usar `dispatch(fetchShippingQuotes(...))` y leer del store en vez de estado local. `CheckoutScreen` lee `selectedQuoteId` del store.

---

### 4. `orderSlice` — AMPLIAR con `pollOrderStatus` ⭐

**Archivo**: `src/store/orderSlice.js` (modificar existente)

**Agregar**:

```javascript
// Nuevo thunk
export const pollOrderStatus = createAsyncThunk(
  'orders/pollStatus',
  async (orderId, { rejectWithValue }) => {
    // NOTA: este thunk es especial — quien lo despacha debe manejar
    // el polling (setInterval) externamente porque createAsyncThunk
    // no soporta polling nativo.
    // Alternativa: crear una acción síncrona `updateOrderStatus(order)`
    // y un helper `startPolling(orderId)` que haga el setInterval.
    const order = await ordersApi.detail(orderId);
    return order;
  }
);

// Nuevo estado
{
  // ...existente...
  pollingActive: false,
  pollingError: null,
}
```

**Alternativa más limpia**: No usar un thunk para polling. En su lugar, `PaymentResultScreen` hace el polling directamente con `ordersApi.detail(orderId)` en un `setInterval` y despacha `fetchOrderDetail.fulfilled` manualmente o actualiza `currentOrder` vía un reducer `updateCurrentOrder`.

---

### 5. `app.json` — Configurar esquema de URL para deep links ⭐

**Archivo**: `app.json` (modificar existente)

Agregar:
```json
{
  "expo": {
    "scheme": "eftshop"
  }
}
```

Esto permite que Bold redirija a `eftshop://payment-result?orderId=...&status=...` en móviles.

Además, configurar el manejo de deep links en `App.js` o en el `NavigationContainer` usando `linking` config:
```javascript
const linking = {
  prefixes: ['eftshop://', 'https://tudominio.com'],
  config: {
    screens: {
      AuthenticatedStack: {
        screens: {
          PaymentResult: 'payment-result',
        },
      },
    },
  },
};
```

---

### 6. `RootNavigator` — Agregar `PaymentResultScreen` al stack ⭐

**Archivo**: `src/navigation/RootNavigator.js` (modificar existente)

Agregar al `AuthenticatedStack`:
```jsx
<Stack.Screen
  name="PaymentResult"
  component={PaymentResultScreen}
  options={{ title: 'Resultado del pago', headerBackVisible: false }}
/>
```

---

### 7. `CheckoutScreen` — Modificar flujo de pago Bold ⭐

**Archivo**: `src/screens/CheckoutScreen.js` (modificar existente)

**Cambios respecto al estado actual**:

1. **Usar `shippingSlice`** en vez de estado local para `selectedQuote`.
2. **El botón de Bold ahora usa el componente real**:
   - Pasar `bold_data` completo del backend a `BoldPaymentButton`.
   - El `onPaymentComplete` de Bold navega a `PaymentResult` en vez de abrir `Linking.openURL()`.
3. **Eliminar `Linking.openURL()`** para el caso Bold — el Embedded Checkout se encarga de todo.
4. **Para COD**: mantener el comportamiento actual (crear orden → navegar a OrderDetail).

**Flujo actualizado**:
```
1. Usuario selecciona dirección y envío
2. Presiona "Pagar con Bold"
3. → dispatch(createOrder({ address_id, shipping_quote_id, payment_method: "bold" }))
4. → El backend responde con bold_data (integrity_hash, public_key, etc.)
5. → Se muestra BoldPaymentButton con los datos reales (Embedded Checkout)
6. → Usuario paga en el iframe de Bold
7. → Bold redirige → onPaymentComplete → navigate('PaymentResult', { orderId, status })
8. → PaymentResultScreen hace polling hasta confirmed/cancelled
```

---

### 8. `OrderDetailScreen` — Agregar botón "Reintentar pago" ⭐

**Archivo**: `src/screens/OrderDetailScreen.js` (modificar existente)

**Cambio**: Si la orden está en estado `pending` y el método de pago es `bold`, mostrar un botón "Reintentar pago" que:
1. Llame a un endpoint del backend para regenerar el `integrity_hash` (o reutilizar el endpoint de creación si la orden no tiene pago asociado).
2. Muestre el `BoldPaymentButton` con el nuevo hash.
3. Nota: si el backend no tiene un endpoint para regenerar el hash, se debe crear uno: `POST /api/orders/<id>/retry-payment/` que devuelva `bold_data` fresco.

---

### 9. `OrdersScreen` — Sin cambios mayores ✅

**Archivo**: `src/screens/OrdersScreen.js` 

Ya muestra `order_number`. Solo verificar que los estilos de estado reflejen correctamente `pending`, `pending_cod`, `confirmed`, `shipped`, `delivered`, `cancelled`.

---

## 🔁 Flujo completo de compra (actualizado)

```
┌─────────────────────────────────────────────────────────┐
│ 1. Usuario en CheckoutScreen                            │
│    - Selecciona dirección (addressSlice)                │
│    - ShippingSelector cotiza vía POST /api/shipping/quote/ │
│    - Elige opción de envío (shippingSlice)              │
│    - Elige método de pago (Bold o COD)                  │
├─────────────────────────────────────────────────────────┤
│ 2. Presiona "Pagar con Bold"                            │
│    - dispatch(createOrder({ address_id, quote_id,       │
│        payment_method: "bold" }))                       │
│    - Backend crea Order (status=pending) + Payment      │
│    - Backend devuelve bold_data con integrity_hash      │
├─────────────────────────────────────────────────────────┤
│ 3. BoldPaymentButton (Embedded Checkout)                │
│    - Renderiza <script> de Bold con todos los data-*    │
│    - Bold abre iframe con pasarela de pagos             │
│    - Usuario paga con tarjeta/PSE/etc.                  │
│    - Bold redirige a eftshop://payment-result?...       │
├─────────────────────────────────────────────────────────┤
│ 4. PaymentResultScreen                                  │
│    - Muestra spinner "Confirmando tu pago…"             │
│    - Polling: GET /api/orders/<id>/ cada 5s             │
│    - Backend recibe webhook de Bold → Order=confirmed   │
│    - Backend dispara crear_guia_envio (Celery)          │
│    - Skydropx genera guía → Shipment creado             │
├─────────────────────────────────────────────────────────┤
│ 5. PaymentResultScreen detecta confirmed                │
│    - Muestra ✅ "¡Pago confirmado!"                      │
│    - Botón "Ver pedido" → OrderDetail                   │
├─────────────────────────────────────────────────────────┤
│ 6. OrderDetailScreen                                    │
│    - Muestra order_number, status, productos            │
│    - Sección "Envío": carrier, tracking_number, estado  │
│    - Tracking en tiempo real vía GET .../tracking/      │
│    - Si pending: botón "Reintentar pago"                │
└─────────────────────────────────────────────────────────┘

Flujo COD:
  2' → createOrder con payment_method="cod"
  3' → Backend crea Order (status=pending_cod)
  4' → Backend dispara crear_guia_envio inmediatamente
  5' → Navega a OrderDetail (sin PaymentResult)
```

---

## 🔒 Seguridad y consideraciones

1. **El `integrity_hash` NUNCA se calcula en el frontend**. Lo calcula el backend con la llave secreta y lo devuelve en `bold_data`.
2. **El `integrity_hash` es de un solo uso**. Si el pago falla o se abandona, se debe regenerar desde el backend con un endpoint dedicado.
3. **Validación del webhook**: el backend ya valida la firma `X-Bold-Signature` con SHA256.
4. **Idempotencia**: el backend ya maneja `transaction_id` único para evitar procesar el mismo webhook dos veces.
5. **Polling con cleanup**: `PaymentResultScreen` debe limpiar `setInterval` al desmontar.
6. **Timeout de polling**: después de 2 minutos sin confirmación, mostrar mensaje informativo (no bloquear al usuario).
7. **WebView**: en móvil, si se usa WebView para Bold, asegurarse de que `originWhitelist` y `onShouldStartLoadWithRequest` estén configurados correctamente.

---

## 📦 Nuevas dependencias (si se usa WebView en móvil)

```
npx expo install react-native-webview
```

`package.json` ya tiene React 19, Expo ~56, React Navigation 7, Redux Toolkit, Axios.

---

## ✅ Checklist de implementación

### Hito 1: Bold Embedded Checkout
- [ ] Reescribir `BoldPaymentButton.js` con inyección de script Bold (web) y WebView (móvil)
- [ ] Renderizar `<script>` con `data-bold-button`, `data-api-key`, `data-order-id`, `data-amount`, `data-currency`, `data-integrity-signature`, `data-redirection-url`, `data-render-mode="embedded"`
- [ ] Capturar evento de finalización de pago (URL redirect / postMessage)
- [ ] Instalar `react-native-webview` si se requiere para móvil

### Hito 2: PaymentResultScreen + Polling
- [ ] Crear `PaymentResultScreen.js` con polling vía `setInterval`
- [ ] Implementar estados: cargando, confirmado, cancelado, timeout
- [ ] Cleanup del intervalo al desmontar

### Hito 3: shippingSlice (Redux)
- [ ] Crear `src/store/shippingSlice.js`
- [ ] Migrar `ShippingSelector` a usar el slice
- [ ] Actualizar `store/index.js` para incluir el nuevo reducer

### Hito 4: Navegación y Deep Links
- [ ] Agregar `scheme: "eftshop"` en `app.json`
- [ ] Configurar `linking` en `App.js` o `NavigationContainer`
- [ ] Agregar `PaymentResult` screen al `AuthenticatedStack`
- [ ] Modificar `CheckoutScreen` para navegar a `PaymentResult` en vez de `Linking.openURL()`

### Hito 5: OrderDetailScreen — Reintentar pago
- [ ] Agregar botón "Reintentar pago" cuando `status === "pending"` y `payment_method === "bold"`
- [ ] (Opcional) Crear endpoint backend `POST /api/orders/<id>/retry-payment/` si no existe

### Hito 6: Pruebas E2E
- [ ] Probar flujo completo Bold en web (sandbox)
- [ ] Probar flujo COD
- [ ] Verificar polling y transiciones de estado
- [ ] Probar abandono y reintento de pago
- [ ] Verificar cleanup de intervalos (sin memory leaks)
