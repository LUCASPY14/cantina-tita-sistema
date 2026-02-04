/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './templates/**/*.html',
    './src/**/*.{js,ts,jsx,tsx}',
    '../backend/**/*.py'  // Para clases de Django
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#FF6B35',  // Color principal
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
          950: '#431407'
        },
        secondary: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#4ECDC4',  // Turquesa
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
          950: '#042f2e'
        },
        success: {
          DEFAULT: '#2ECC71',
          50: '#f0fdf4',
          500: '#2ECC71',
          600: '#16a34a',
          700: '#15803d'
        },
        warning: {
          DEFAULT: '#F39C12',
          50: '#fffbeb',
          500: '#F39C12',
          600: '#d97706',
          700: '#b45309'
        },
        danger: {
          DEFAULT: '#E74C3C',
          50: '#fef2f2',
          500: '#E74C3C',
          600: '#dc2626',
          700: '#b91c1c'
        }
      },
      fontFamily: {
        sans: ['Poppins', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem'
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-in': 'bounceIn 0.5s ease-out'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        },
        bounceIn: {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1)', opacity: '1' }
        }
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio')
  ],
  // DaisyUI configuración (mantener para compatibilidad)
  daisyui: {
    themes: [
      {
        cantina: {
          "primary": "#FF6B35",
          "secondary": "#4ECDC4", 
          "accent": "#F39C12",
          "neutral": "#3D4451",
          "base-100": "#FFFFFF",
          "info": "#3ABFF8",
          "success": "#2ECC71",
          "warning": "#F39C12", 
          "error": "#E74C3C"
        }
      },
      "light", 
      "dark"
    ],
    darkTheme: "dark"
  }
}