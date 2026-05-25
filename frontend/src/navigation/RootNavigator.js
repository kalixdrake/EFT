import { useEffect } from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useDispatch, useSelector } from 'react-redux';
import AddressFormScreen from '../screens/AddressFormScreen';
import AuthScreen from '../screens/AuthScreen';
import CheckoutScreen from '../screens/CheckoutScreen';
import OrderDetailScreen from '../screens/OrderDetailScreen';
import PaymentResultScreen from '../screens/PaymentResultScreen';
import ProductDetailScreen from '../screens/ProductDetailScreen';
import { fetchCart } from '../store/cartSlice';
import { colors } from '../utils/theme';
import TabNavigator from './TabNavigator';

const Stack = createNativeStackNavigator();

function GuestStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Auth" component={AuthScreen} />
    </Stack.Navigator>
  );
}

function AuthenticatedStack() {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(fetchCart());
  }, [dispatch]);

  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.surface },
        headerTintColor: colors.text,
        headerTitleStyle: { fontWeight: '700' },
        contentStyle: { backgroundColor: colors.background },
      }}
    >
      <Stack.Screen
        name="MainTabs"
        component={TabNavigator}
        options={{ headerShown: false }}
      />
      <Stack.Screen
        name="ProductDetail"
        component={ProductDetailScreen}
        options={{ title: 'Detalle del producto' }}
      />
      <Stack.Screen
        name="Checkout"
        component={CheckoutScreen}
        options={{ title: 'Checkout' }}
      />
      <Stack.Screen
        name="OrderDetail"
        component={OrderDetailScreen}
        options={{ title: 'Detalle del pedido' }}
      />
      <Stack.Screen
        name="PaymentResult"
        component={PaymentResultScreen}
        options={{ title: 'Resultado del pago', headerBackVisible: false }}
      />
      <Stack.Screen
        name="AddressForm"
        component={AddressFormScreen}
        options={({ route }) => ({
          title: route.params?.addressId ? 'Editar dirección' : 'Nueva dirección',
        })}
      />
    </Stack.Navigator>
  );
}

export default function RootNavigator() {
  const accessToken = useSelector((state) => state.auth.accessToken);

  if (!accessToken) {
    return <GuestStack />;
  }

  return <AuthenticatedStack />;
}
