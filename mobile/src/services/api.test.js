describe('mobile api service', () => {
  const loadModule = (constantsMock) => {
    jest.resetModules();
    const secureStoreMock = {
      getItemAsync: jest.fn(),
      deleteItemAsync: jest.fn(),
    };

    jest.doMock('expo-constants', () => constantsMock);
    jest.doMock('expo-secure-store', () => secureStoreMock);

    // eslint-disable-next-line global-require
    const mod = require('./api');
    return { mod, secureStoreMock };
  };

  it('builds base URL from Expo host', () => {
    const { mod } = loadModule({
      expoConfig: { hostUri: '192.168.1.22:8081' },
      expoGoConfig: {},
    });

    expect(mod.getDefaultApiBase()).toBe('http://192.168.1.22:8000/api/v1');
    expect(mod.API_BASE).toBe('http://192.168.1.22:8000/api/v1');
  });

  it('falls back to localhost when Expo host is unavailable', () => {
    const { mod } = loadModule({
      expoConfig: null,
      expoGoConfig: null,
    });

    expect(mod.getDefaultApiBase()).toBe('http://localhost:8000/api/v1');
  });

  it('injects auth token into outgoing request headers', async () => {
    const { mod, secureStoreMock } = loadModule({
      expoConfig: { hostUri: '10.0.2.2:8081' },
      expoGoConfig: {},
    });
    secureStoreMock.getItemAsync.mockResolvedValue('token-abc');

    const fulfilled = mod.default.interceptors.request.handlers[0].fulfilled;
    const config = await fulfilled({ headers: {} });

    expect(secureStoreMock.getItemAsync).toHaveBeenCalledWith('auth_token');
    expect(config.headers.Authorization).toBe('Bearer token-abc');
  });

  it('clears secure token on 401 responses', async () => {
    const { mod, secureStoreMock } = loadModule({
      expoConfig: { hostUri: '10.0.2.2:8081' },
      expoGoConfig: {},
    });
    const rejected = mod.default.interceptors.response.handlers[0].rejected;
    const error = { response: { status: 401 } };

    await expect(rejected(error)).rejects.toBe(error);
    expect(secureStoreMock.deleteItemAsync).toHaveBeenCalledWith('auth_token');
  });
});
