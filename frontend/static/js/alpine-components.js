/**
 * 🎨 COMPONENTES ALPINE.JS REUTILIZABLES
 * Sistema de componentes para mejorar la UX del frontend
 */

// ====================================================================
// 1. SISTEMA DE NOTIFICACIONES TOAST
// ====================================================================

Alpine.data('notifications', () => ({
    items: [],
    maxNotifications: 5,
    
    /**
     * Agregar una notificación
     * @param {string} message - Mensaje a mostrar
     * @param {string} type - Tipo: success, error, warning, info
     * @param {number} duration - Duración en ms (default 3000)
     */
    add(message, type = 'info', duration = 3000) {
        const id = Date.now() + Math.random();
        
        // Limitar cantidad de notificaciones
        if (this.items.length >= this.maxNotifications) {
            this.items.shift();
        }
        
        this.items.push({ 
            id, 
            message, 
            type, 
            duration,
            progress: 100
        });
        
        // Auto-remover después de la duración
        if (duration > 0) {
            this.animateProgress(id, duration);
            setTimeout(() => this.remove(id), duration);
        }
    },
    
    /**
     * Remover una notificación
     */
    remove(id) {
        this.items = this.items.filter(item => item.id !== id);
    },
    
    /**
     * Animar barra de progreso
     */
    animateProgress(id, duration) {
        const item = this.items.find(i => i.id === id);
        if (!item) return;
        
        const interval = 50; // Actualizar cada 50ms
        const steps = duration / interval;
        let currentStep = 0;
        
        const timer = setInterval(() => {
            currentStep++;
            item.progress = 100 - (currentStep / steps * 100);
            
            if (currentStep >= steps) {
                clearInterval(timer);
            }
        }, interval);
    },
    
    /**
     * Shortcuts para tipos comunes
     */
    success(message, duration = 3000) {
        this.add(message, 'success', duration);
    },
    
    error(message, duration = 5000) {
        this.add(message, 'error', duration);
    },
    
    warning(message, duration = 4000) {
        this.add(message, 'warning', duration);
    },
    
    info(message, duration = 3000) {
        this.add(message, 'info', duration);
    }
}));


// ====================================================================
// 2. LOADING STATES Y SKELETON LOADERS
// ====================================================================

Alpine.data('loadingState', (initialState = false) => ({
    loading: initialState,
    error: null,
    data: null,
    
    /**
     * Ejecutar acción con loading state
     */
    async execute(asyncFn) {
        this.loading = true;
        this.error = null;
        
        try {
            this.data = await asyncFn();
            return this.data;
        } catch (err) {
            this.error = err.message || 'Error desconocido';
            console.error('Error en loadingState:', err);
            throw err;
        } finally {
            this.loading = false;
        }
    },
    
    /**
     * Reset state
     */
    reset() {
        this.loading = false;
        this.error = null;
        this.data = null;
    }
}));


// ====================================================================
// 3. VALIDACIÓN DE FORMULARIOS
// ====================================================================

Alpine.data('formValidation', (initialFields = {}) => ({
    fields: {},
    submitted: false,
    
    init() {
        // Inicializar campos
        Object.keys(initialFields).forEach(key => {
            this.fields[key] = {
                value: initialFields[key].value || '',
                error: '',
                valid: false,
                touched: false,
                rules: initialFields[key].rules || []
            };
        });
    },
    
    /**
     * Validar un campo individual
     */
    validateField(fieldName) {
        const field = this.fields[fieldName];
        if (!field) return;
        
        field.touched = true;
        field.error = '';
        field.valid = true;
        
        // Ejecutar reglas de validación
        for (const rule of field.rules) {
            const error = rule(field.value);
            if (error) {
                field.error = error;
                field.valid = false;
                break;
            }
        }
        
        return field.valid;
    },
    
    /**
     * Validar todos los campos
     */
    validateAll() {
        this.submitted = true;
        let allValid = true;
        
        Object.keys(this.fields).forEach(fieldName => {
            if (!this.validateField(fieldName)) {
                allValid = false;
            }
        });
        
        return allValid;
    },
    
    /**
     * Obtener valores del formulario
     */
    getValues() {
        const values = {};
        Object.keys(this.fields).forEach(key => {
            values[key] = this.fields[key].value;
        });
        return values;
    },
    
    /**
     * Reset formulario
     */
    reset() {
        this.submitted = false;
        Object.keys(this.fields).forEach(key => {
            this.fields[key].value = '';
            this.fields[key].error = '';
            this.fields[key].valid = false;
            this.fields[key].touched = false;
        });
    }
}));

// Reglas de validación comunes
window.ValidationRules = {
    required: (message = 'Este campo es requerido') => {
        return (value) => !value ? message : '';
    },
    
    email: (message = 'Email no válido') => {
        return (value) => {
            if (!value) return '';
            const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return !regex.test(value) ? message : '';
        };
    },
    
    minLength: (min, message = `Mínimo ${min} caracteres`) => {
        return (value) => {
            if (!value) return '';
            return value.length < min ? message : '';
        };
    },
    
    maxLength: (max, message = `Máximo ${max} caracteres`) => {
        return (value) => {
            if (!value) return '';
            return value.length > max ? message : '';
        };
    },
    
    numeric: (message = 'Solo números') => {
        return (value) => {
            if (!value) return '';
            return !/^\d+$/.test(value) ? message : '';
        };
    },
    
    phone: (message = 'Teléfono no válido') => {
        return (value) => {
            if (!value) return '';
            const regex = /^[0-9]{9,10}$/;
            return !regex.test(value) ? message : '';
        };
    }
};


// ====================================================================
// 4. BÚSQUEDA CON DEBOUNCE
// ====================================================================

Alpine.data('searchWithDebounce', (options = {}) => ({
    query: '',
    results: [],
    loading: false,
    debounceTimer: null,
    minChars: options.minChars || 3,
    delay: options.delay || 300,
    endpoint: options.endpoint || '/api/search',
    
    /**
     * Ejecutar búsqueda con debounce
     */
    search() {
        clearTimeout(this.debounceTimer);
        
        // Si no alcanza mínimo de caracteres, limpiar
        if (this.query.length < this.minChars) {
            this.results = [];
            return;
        }
        
        // Esperar delay antes de buscar
        this.debounceTimer = setTimeout(() => {
            this.performSearch();
        }, this.delay);
    },
    
    /**
     * Realizar búsqueda en el servidor
     */
    async performSearch() {
        this.loading = true;
        
        try {
            const response = await fetch(`${this.endpoint}?q=${encodeURIComponent(this.query)}`);
            
            if (!response.ok) {
                throw new Error('Error en búsqueda');
            }
            
            this.results = await response.json();
        } catch (error) {
            console.error('Error en búsqueda:', error);
            this.results = [];
        } finally {
            this.loading = false;
        }
    },
    
    /**
     * Limpiar búsqueda
     */
    clear() {
        this.query = '';
        this.results = [];
        clearTimeout(this.debounceTimer);
    }
}));


// ====================================================================
// 5. MODAL/DIALOG SYSTEM
// ====================================================================

Alpine.data('modal', () => ({
    open: false,
    
    show() {
        this.open = true;
        document.body.style.overflow = 'hidden';
    },
    
    hide() {
        this.open = false;
        document.body.style.overflow = 'auto';
    },
    
    toggle() {
        this.open ? this.hide() : this.show();
    }
}));


// ====================================================================
// 6. DARK MODE
// ====================================================================

Alpine.store('darkMode', {
    on: false,
    
    init() {
        // Leer preferencia guardada o del sistema
        const saved = localStorage.getItem('darkMode');
        
        if (saved !== null) {
            this.on = saved === 'true';
        } else {
            this.on = window.matchMedia('(prefers-color-scheme: dark)').matches;
        }
        
        this.apply();
        
        // Escuchar cambios del sistema
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (localStorage.getItem('darkMode') === null) {
                this.on = e.matches;
                this.apply();
            }
        });
    },
    
    toggle() {
        this.on = !this.on;
        localStorage.setItem('darkMode', this.on);
        this.apply();
    },
    
    apply() {
        if (this.on) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }
});


// ====================================================================
// 7. KEYBOARD NAVIGATION
// ====================================================================

Alpine.data('keyboardNav', (options = {}) => ({
    items: [],
    currentIndex: -1,
    selector: options.selector || '[data-nav-item]',
    
    init() {
        this.items = Array.from(this.$el.querySelectorAll(this.selector));
        
        this.$el.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.next();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.previous();
                    break;
                case 'Enter':
                    e.preventDefault();
                    this.select();
                    break;
                case 'Escape':
                    this.reset();
                    break;
            }
        });
    },
    
    next() {
        this.currentIndex = Math.min(this.currentIndex + 1, this.items.length - 1);
        this.focusCurrent();
    },
    
    previous() {
        this.currentIndex = Math.max(this.currentIndex - 1, 0);
        this.focusCurrent();
    },
    
    select() {
        if (this.currentIndex >= 0 && this.currentIndex < this.items.length) {
            this.items[this.currentIndex].click();
        }
    },
    
    focusCurrent() {
        if (this.currentIndex >= 0 && this.currentIndex < this.items.length) {
            const item = this.items[this.currentIndex];
            item.focus();
            item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    },
    
    reset() {
        this.currentIndex = -1;
    }
}));


// ====================================================================
// 8. CLIPBOARD COPY
// ====================================================================

Alpine.data('clipboard', () => ({
    copied: false,
    
    async copy(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.copied = true;
            
            setTimeout(() => {
                this.copied = false;
            }, 2000);
            
            return true;
        } catch (err) {
            console.error('Error copiando al portapapeles:', err);
            return false;
        }
    }
}));


// ====================================================================
// INICIALIZACIÓN GLOBAL
// ====================================================================

document.addEventListener('alpine:init', () => {
    // Inicializar dark mode
    Alpine.store('darkMode').init();
    
    console.log('✅ Componentes Alpine.js cargados');
});
