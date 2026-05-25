import { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { Provider, useDispatch, useSelector } from 'react-redux';
import { setStoreRef } from './src/api/client';
import LoadingSpinner from './src/components/LoadingSpinner';
import RootNavigator from './src/navigation/RootNavigator';
import { store } from './src/store';
import { initializeAuth } from './src/store/authSlice';

setStoreRef(store);

function AppContent() {
  const dispatch = useDispatch();
  const initializing = useSelector((state) => state.auth.initializing);

  useEffect(() => {
    dispatch(initializeAuth());
  }, [dispatch]);

  if (initializing) {
    return <LoadingSpinner />;
  }

  return (
    <>
      <RootNavigator />
      <StatusBar style="auto" />
    </>
  );
}

const linking = {
  prefixes: ['eftshop://', 'https://eftshop.com', 'http://localhost:8081'],
  config: {
    screens: {
      // Bold redirects back to /payment-result?orderId=X&bold-tx-status=...
      // React Navigation parses query params as route.params automatically.
      PaymentResult: {
        path: 'payment-result',
        parse: { orderId: (id) => id },
      },
    },
  },
};

export default function App() {
  return (
    <Provider store={store}>
      <NavigationContainer linking={linking}>
        <AppContent />
      </NavigationContainer>
    </Provider>
  );
}
