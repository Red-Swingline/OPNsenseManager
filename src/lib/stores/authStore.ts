import { writable } from 'svelte/store';

interface AuthState {
  isLoggedIn: boolean;
  isConfigured: boolean;
}

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>({
    isLoggedIn: false,
    isConfigured: false
  });

  return {
    subscribe,
    login: () => update(state => ({ ...state, isLoggedIn: true })),
    logout: () => update(state => ({ ...state, isLoggedIn: false })),
    setConfigured: (value: boolean) => update(state => ({ ...state, isConfigured: value })),
    reset: () => set({ isLoggedIn: false, isConfigured: false })
  };
}

export const authStore = createAuthStore();