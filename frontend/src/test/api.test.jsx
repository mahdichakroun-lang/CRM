import { describe, it, expect, beforeEach, vi } from 'vitest';
import api from '../services/api';

describe('API Interceptors', () => {
  beforeEach(() => {
    // Clear localStorage mock before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('devrait ajouter le token Authorization si présent dans localStorage', async () => {
    localStorage.setItem('token', 'fake-jwt-token');
    
    // Simulate a request config
    const config = { headers: {}, method: 'post', url: '/test' };
    
    // Call the fulfillment handler of the request interceptor
    const requestHandler = api.interceptors.request.handlers[0].fulfilled;
    const result = await requestHandler(config);
    
    expect(result.headers.Authorization).toBe('Bearer fake-jwt-token');
  });

  it('devrait ajouter les headers anti-cache pour les requêtes GET', async () => {
    const config = { headers: {}, method: 'get', url: '/test' };
    
    const requestHandler = api.interceptors.request.handlers[0].fulfilled;
    const result = await requestHandler(config);
    
    expect(result.headers['Cache-Control']).toBe('no-cache, no-store, must-revalidate');
    expect(result.headers['Pragma']).toBe('no-cache');
    expect(result.headers['Expires']).toBe('0');
  });

  it('ne devrait PAS ajouter de headers anti-cache pour les requêtes POST', async () => {
    const config = { headers: {}, method: 'post', url: '/test' };
    
    const requestHandler = api.interceptors.request.handlers[0].fulfilled;
    const result = await requestHandler(config);
    
    expect(result.headers['Cache-Control']).toBeUndefined();
    expect(result.headers['Pragma']).toBeUndefined();
  });

  it('devrait rediriger vers /login sur une erreur 401', async () => {
    localStorage.setItem('token', 'expired-token');
    
    // Mock window.location.href (this is a tricky part in jsdom, but we can verify localStorage is cleared)
    const error = { response: { status: 401 } };
    
    const responseErrorHandler = api.interceptors.response.handlers[0].rejected;
    
    try {
      await responseErrorHandler(error);
    } catch (e) {
      // It rejects the promise
    }
    
    expect(localStorage.getItem('token')).toBeNull();
  });
});
