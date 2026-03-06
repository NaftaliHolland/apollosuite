import axios, {
	HeadersDefaults,
	AxiosInstance,
	AxiosResponse,
	AxiosError,
	InternalAxiosRequestConfig,
} from 'axios';


const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/'

export const getAccessToken = (): string | null => {
	if (typeof window === 'undefined') return null;

	return localStorage.getItem('accessToken');
}

const getRefreshToken = (): string | null => {
	if (typeof window === 'undefined') return null;

	return localStorage.getItem('refreshToken');
}

export const clearTokens = () => {
	if (typeof window === 'undefined') return;

	localStorage.removeItem('accessToken');
	localStorage.removeItem('refreshToken');
}

type Tokens = {
	access: string;
	refresh: string;
}

export const setTokens = ({ access, refresh }: Tokens) => {
	if (typeof window === 'undefined') return;

	localStorage.setItem('accessToken', access)
	localStorage.setItem('refreshToken', refresh)
}

const axiosInstance: AxiosInstance = axios.create({
	baseURL: BASE_URL,
	timeout: 10000,
	headers: {
		'Content-Type': 'application/json'
	}
})

axiosInstance.interceptors.request.use(
	(config: InternalAxiosRequestConfig) => {
		const token = getAccessToken();
		if (token) config.headers.Authorization = `Bearer ${token}`;

		return config;
	},

	(error: AxiosError) => {
		console.error('Request interceptor error:', error);
		return Promise.reject(error);
	}
);

axiosInstance.interceptors.response.use(
	(response: AxiosResponse) => response,

	async (error: AxiosError) => {
		const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

		if (error.response?.status === 401 && !originalRequest._retry) {
			originalRequest._retry = true;

			const refreshToken = getRefreshToken()

			if (refreshToken) {
				try {
					const response = await axios.post(`${BASE_URL}auth/token/refresh/`, {
						"refresh": refreshToken,
					});

					const accessToken = response.data.access;

					if (typeof window !== 'undefined') {
						localStorage.setItem('accessToken', accessToken);
					}
					originalRequest.headers.Authorization = `Bearer ${accessToken}`;
					return axiosInstance(originalRequest);

				} catch (refreshError) {
					console.error('Token refresh failed:', refreshError);
					clearTokens();

					if (typeof window !== 'undefined') {
						window.location.href = '/login';
					}

					return Promise.reject(refreshError);

				}
			} else {
				clearTokens();
				if (typeof window !== 'undefined') {
					window.location.href = '/login';
				}
			}
		}
		return Promise.reject(error);
	}
);

export default axiosInstance; // Will just be called axios when used in other places
