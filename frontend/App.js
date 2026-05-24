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

export default function App() {
  return (
    <Provider store={store}>
      <NavigationContainer>
        <AppContent />
      </NavigationContainer>
    </Provider>
  );
}
