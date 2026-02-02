# Sonidos para el POS

Este directorio debe contener los siguientes archivos de sonido MP3:

## Archivos necesarios:

1. **beep.mp3** - Sonido corto al agregar productos al carrito
2. **success.mp3** - Sonido de éxito al completar una venta
3. **error.mp3** - Sonido de error al rechazar una operación
4. **scan.mp3** - Sonido al escanear una tarjeta

## Donde conseguir sonidos gratuitos:

- https://freesound.org/
- https://mixkit.co/free-sound-effects/
- https://zapsplat.com/

## Alternativa rápida:

Puedes usar Text-to-Speech o sonidos del sistema mientras consigues los archivos:

```javascript
// En lugar de Howler.js, usar Web Audio API simple:
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

function playBeep() {
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
}
```
