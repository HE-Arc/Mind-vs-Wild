type AuthStore = {
  isLoggedIn: boolean;
  user: any;
  token: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  restoreUser: () => Promise<void>;
}

declare module '@/stores/auth' {
  export function useAuthStore(): AuthStore;
}
