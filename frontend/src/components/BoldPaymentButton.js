import { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Modal,
  Platform,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import {
  BOLD_LIBRARY_URL,
  appendOrderIdToRedirectUrl,
  extractBoldResultFromUrl,
  isBoldRedirectUrl,
} from '../utils/bold';
import { colors, spacing } from '../utils/theme';

let WebView = null;
if (Platform.OS !== 'web') {
  try {
    WebView = require('react-native-webview').WebView;
  } catch (_) {
    // react-native-webview not available
  }
}

// ─── Web implementation ────────────────────────────────────────────────────
// Root cause of previous issues:
//   Bold's library scans for <script data-bold-button> only once at page load.
//   Dynamically injected scripts after load are never processed, so the button
//   was rendering but click → window.location.href never fired.
// Fix: use the programmatic BoldCheckout API directly.

function BoldButtonWeb({
  publicKey,
  orderReference,
  amountCents,
  currency,
  integrityHash,
  redirectUrl,
  onPaymentComplete,
}) {
  const [libraryLoaded, setLibraryLoaded] = useState(false);

  // Load Bold library once
  useEffect(() => {
    const existing = document.getElementById('bold-payment-library');
    if (existing) {
      setLibraryLoaded(true);
      return;
    }
    const script = document.createElement('script');
    script.id = 'bold-payment-library';
    script.src = BOLD_LIBRARY_URL;
    script.onload = () => setLibraryLoaded(true);
    script.onerror = () => console.error('[Bold] Failed to load payment library');
    document.head.appendChild(script);
  }, []);

  const handlePay = useCallback(() => {
    if (!window.BoldCheckout) {
      console.error('[Bold] BoldCheckout class not available');
      return;
    }
    const computedRedirectUrl =
      redirectUrl && redirectUrl.startsWith('http')
        ? redirectUrl
        : `${window.location.origin}/payment-result`;

    try {
      // BoldCheckout.open() → window.location.href = boldCheckoutUrl (full-page redirect)
      // This avoids all aria-hidden conflicts with React Navigation's overlay tree.
      new window.BoldCheckout({
        apiKey: publicKey,
        orderId: orderReference,
        amount: String(amountCents),
        currency: currency,
        integritySignature: integrityHash,
        redirectionUrl: computedRedirectUrl,
      }).open();
    } catch (err) {
      console.error('[Bold] Error opening checkout:', err);
    }
  }, [publicKey, orderReference, amountCents, currency, integrityHash, redirectUrl]);

  if (!libraryLoaded) {
    return (
      <View style={styles.loadingRow}>
        <ActivityIndicator color={colors.primary} />
        <Text style={styles.loadingText}>Cargando pasarela de pagos…</Text>
      </View>
    );
  }

  return (
    <Pressable onPress={handlePay} style={styles.boldWebButton}>
      <Text style={styles.boldWebButtonText}>💳  Pagar con Bold</Text>
    </Pressable>
  );
}

// ─── Mobile implementation ─────────────────────────────────────────────────

function BoldButtonMobile({ checkoutUrl, redirectUrl, orderReference, onPaymentComplete, onError }) {
  const [visible, setVisible] = useState(true);

  const handleNavigationChange = useCallback(
    (navState) => {
      const { url } = navState;
      if (!url) return;
      if (isBoldRedirectUrl(url, redirectUrl)) {
        const result = extractBoldResultFromUrl(url);
        setVisible(false);
        onPaymentComplete({
          status: result ? result.status : 'pending',
          orderReference: result?.orderReference || orderReference,
          orderId: result?.orderId ?? null,
        });
      }
    },
    [redirectUrl, orderReference, onPaymentComplete],
  );

  const handleClose = useCallback(() => {
    setVisible(false);
    if (onError) onError(new Error('Pago cancelado por el usuario'));
  }, [onError]);

  if (!WebView) {
    return (
      <View style={styles.fallback}>
        <Text style={styles.fallbackText}>
          El componente de pagos no está disponible. Actualiza la app.
        </Text>
      </View>
    );
  }

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={handleClose}>
      <SafeAreaView style={styles.modal}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Pago con Bold</Text>
          <Pressable style={styles.closeBtn} onPress={handleClose}>
            <Text style={styles.closeBtnText}>✕</Text>
          </Pressable>
        </View>
        <WebView
          source={{ uri: checkoutUrl }}
          onNavigationStateChange={handleNavigationChange}
          originWhitelist={['*']}
          onShouldStartLoadWithRequest={(req) => {
            if (isBoldRedirectUrl(req.url, redirectUrl)) {
              handleNavigationChange({ url: req.url });
              return false;
            }
            return true;
          }}
          style={styles.webView}
        />
      </SafeAreaView>
    </Modal>
  );
}

// ─── Public component ──────────────────────────────────────────────────────

export default function BoldPaymentButton({
  publicKey,
  checkoutUrl,
  orderReference,
  amountCents,
  currency = 'COP',
  integrityHash,
  redirectUrl,
  description,
  customerData,
  billingAddress,
  onPaymentComplete,
  onError,
}) {
  if (Platform.OS === 'web') {
    return (
      <BoldButtonWeb
        publicKey={publicKey}
        orderReference={orderReference}
        amountCents={amountCents}
        currency={currency}
        integrityHash={integrityHash}
        redirectUrl={redirectUrl}
        onPaymentComplete={onPaymentComplete}
      />
    );
  }

  return (
    <BoldButtonMobile
      checkoutUrl={checkoutUrl}
      redirectUrl={appendOrderIdToRedirectUrl(redirectUrl, orderReference)}
      orderReference={orderReference}
      onPaymentComplete={onPaymentComplete}
      onError={onError}
    />
  );
}

const styles = StyleSheet.create({
  loadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.md,
    gap: spacing.sm,
  },
  loadingText: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  fallback: {
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.border,
  },
  fallbackText: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  modal: {
    flex: 1,
    backgroundColor: colors.background,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  modalTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
  },
  closeBtn: {
    padding: spacing.sm,
  },
  closeBtnText: {
    fontSize: 18,
    color: colors.text,
  },
  webView: {
    flex: 1,
  },
  boldWebButton: {
    backgroundColor: '#121E6C',
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: spacing.md,
  },
  boldWebButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
});
