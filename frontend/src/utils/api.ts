// Cliente API simplificado para evitar errores de tipos
export class APIClient {
  private baseURL = import.meta.env.DEV ? '/api' : 'http://localhost:8000/api'
  private token: string | null = null
  
  constructor() {
    this.token = localStorage.getItem('auth_token')
  }
  
  private getHeaders() {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }
    
    return headers
  }
  
  async get(endpoint: string) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'GET',
      headers: this.getHeaders()
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  }
  
  async post(endpoint: string, data: any) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  }
}

export const api = new APIClient()
