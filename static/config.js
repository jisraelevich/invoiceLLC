// ============================================================================
// CONFIG.JS - Configuración centralizada de la aplicación
// ============================================================================

const APP_CONFIG = {
  // Colors (Paleta de colores)
  colors: {
    primary: '#1e40af',      // Azul principal
    secondary: '#64748b',    // Gris
    success: '#16a34a',      // Verde
    warning: '#ea580c',      // Naranja
    danger: '#dc2626',       // Rojo
    light: '#f8fafc',        // Blanco
    border: '#e2e8f0',       // Gris borde
    text: '#1e293b',         // Texto oscuro
    textLight: '#64748b'     // Texto gris
  },

  // Typography
  fonts: {
    family: '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
    sizes: {
      h1: '28px',
      h2: '24px',
      h3: '20px',
      base: '14px',
      small: '12px'
    }
  },

  // Spacing
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px'
  },

  // Buttons
  buttons: {
    height: '40px',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '500',
    padding: '8px 16px'
  },

  // Inputs
  inputs: {
    height: '40px',
    borderRadius: '6px',
    fontSize: '14px',
    padding: '8px 12px',
    borderWidth: '1px'
  },

  // Months (Meses en español)
  months: [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ],

  // Viernes códigos (Códigos de facturación predefinidos)
  // Invoice Bill Type codes (AFIP)
  billTypeCodes: [
    { code: '055', label: 'Services - IT & Training' },
    { code: '061', label: 'Goods Sale' },
    { code: '062', label: 'Services' }
  ],

  // Status codes
  statusCodes: [
    { code: '01', label: 'PENDIENTE', description: 'Pending - Not yet sent to AFIP' },
    { code: '02', label: 'EMITIDO', description: 'Issued - Sent to AFIP' },
    { code: '03', label: 'PAGADO', description: 'Paid - Payment received' },
    { code: '04', label: 'CANCELADO', description: 'Cancelled' }
  ],

  // Labels y textos
  labels: {
    monthSummary: 'Monthly Summary',
    estimatedAmount: 'Estimated Amount to Invoice:',
    invoiced: 'Invoiced',
    pending: 'Pending',
    invoiceByFriday: 'Amounts to Invoice by Friday',
    type: 'Type',
    calculatePreview: 'Calculate & Preview',
    edit: 'Edit',
    approveFacurate: 'Approve & Facturate',
    resultsTab: 'Results',
    adminTab: 'Admin',
    pricePerLine: 'Price per Code Line:',
    save: 'Save',
    priceHistory: 'Price History',
    date: 'Date',
    price: 'Price',
    alert: 'Alert',
    warningExceeded: 'Total invoices exceed estimated amount!',
    total: 'Total',
    withinEstimate: 'Within estimate',
    exceededEstimate: 'Exceeded estimate'
  },

  // Años disponibles para dropdown (ejemplos)
  availableYears: [2026, 2025, 2024],

  // Configuración de tabla
  table: {
    borderColor: '#e2e8f0',
    headerBg: '#f1f5f9',
    hoverBg: '#f8fafc'
  }
};

// Exportar para uso en otros archivos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = APP_CONFIG;
}
