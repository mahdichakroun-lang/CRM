import api from './api';

describe('api service', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('uses a base URL ending with /api/v1', () => {
    expect(api.defaults.baseURL).toContain('/api/v1');
  });

  it('attaches bearer token in request interceptor when token exists', async () => {
    localStorage.setItem('token', 'token-123');
    const interceptor = api.interceptors.request.handlers[0].fulfilled;

    const config = await interceptor({ headers: {} });

    expect(config.headers.Authorization).toBe('Bearer token-123');
  });

  it('keeps request headers unchanged when token is missing', async () => {
    const interceptor = api.interceptors.request.handlers[0].fulfilled;

    const config = await interceptor({ headers: {} });

    expect(config.headers.Authorization).toBeUndefined();
  });
});
