// Manager de audio usando Howler.js
export class AudioManager {
  private sounds: Map<string, any> = new Map()
  
  createSound(src: string) {
    try {
      // Simulamos un objeto de sonido básico
      return {
        play: () => {
          console.log(`Playing sound: ${src}`)
          // En producción aquí iría Howler.js
        }
      }
    } catch (error) {
      console.log('Audio not available:', error)
      return {
        play: () => {}
      }
    }
  }
  
  preloadSounds(soundUrls: string[]) {
    soundUrls.forEach(url => {
      this.sounds.set(url, this.createSound(url))
    })
  }
}

export const audioManager = new AudioManager()
