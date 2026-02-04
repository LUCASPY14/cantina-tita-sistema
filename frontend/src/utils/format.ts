// ==================== UTILIDADES DE FORMATEO ====================

// Formatear moneda paraguaya
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('es-PY', {
    style: 'currency',
    currency: 'PYG',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

// Formatear número
export const formatNumber = (num: number, decimals: number = 0): string => {
  return new Intl.NumberFormat('es-PY', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(num);
};

// Formatear fecha
export const formatDate = (date: string | Date, options?: Intl.DateTimeFormatOptions): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  };
  
  return new Intl.DateTimeFormat('es-PY', { ...defaultOptions, ...options }).format(dateObj);
};

// Formatear fecha y hora
export const formatDateTime = (date: string | Date): string => {
  return formatDate(date, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Formatear fecha relativa (hace X tiempo)
export const formatRelativeTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);
  
  if (diffInSeconds < 60) {
    return 'hace un momento';
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `hace ${diffInMinutes} minuto${diffInMinutes !== 1 ? 's' : ''}`;
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `hace ${diffInHours} hora${diffInHours !== 1 ? 's' : ''}`;
  }
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `hace ${diffInDays} día${diffInDays !== 1 ? 's' : ''}`;
  }
  
  return formatDate(dateObj);
};

// Truncar texto
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength).trim()}...`;
};

// Capitalizar primera letra
export const capitalize = (text: string): string => {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

// Formatear teléfono paraguayo
export const formatPhone = (phone: string): string => {
  // Remover caracteres no numéricos
  const digits = phone.replace(/\D/g, '');
  
  // Formatear según longitud
  if (digits.length === 9) {
    // Celular: 0981-123456
    return `${digits.substring(0, 4)}-${digits.substring(4)}`;
  } else if (digits.length === 10) {
    // Fijo con código de área: (021) 123-456
    return `(${digits.substring(0, 3)}) ${digits.substring(3, 6)}-${digits.substring(6)}`;
  }
  
  return phone; // Devolver original si no coincide con formato esperado
};

// Formatear documento paraguayo (CI)
export const formatDocument = (doc: string): string => {
  const digits = doc.replace(/\D/g, '');
  
  if (digits.length <= 8) {
    // CI: 1.234.567-8
    const number = digits.substring(0, digits.length - 1);
    const checkDigit = digits.substring(digits.length - 1);
    
    const formatted = number.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
    return checkDigit ? `${formatted}-${checkDigit}` : formatted;
  }
  
  return doc;
};

// Formatear porcentaje
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${formatNumber(value * 100, decimals)}%`;
};

// Formatear tamaño de archivo
export const formatFileSize = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  
  if (bytes === 0) return '0 Bytes';
  
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${formatNumber(bytes / Math.pow(1024, i), 2)} ${sizes[i]}`;
};
