"use client";

import {
	createContext,
	useContext,
	useEffect,
	useMemo,
	useState,
	ReactNode
} from "react";
import { useQueryClient } from "@tanstack/react-query";
import api, { getAccessToken, setTokens, clearTokens } from "@/lib/api";

type AuthContextType = {
	isAuthenticated: boolean;
	isLoading: boolean;
	login: (phone_number: string, password: string) => Promise<void>;
	logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
	const queryClient = useQueryClient();
	const [isBootstrapping, setIsBootstrapping] = useState(true);

	const accessToken = getAccessToken();
	const isAuthenticated = !!accessToken;

	useEffect(() => {

		async function bootstrap() {
			if (!accessToken) {
				setIsBootstrapping(false);
				return;
			}

			try {
				await queryClient.fetchQuery({
					queryKey: ["currentUser"],
					queryFn: async () => {
						const res = await api.get("auth/me/");
						return res.data.user;
					},
				});
			} catch (error) {
				console.log("Error", error);
				clearTokens();
				queryClient.clear();
			} finally {
				setIsBootstrapping(false);
			}

		}

		bootstrap();
	}, [accessToken, queryClient]);


	async function login(phone_number: string, password: string) {
		const response = await api.post("auth/login/", { phone_number, password });

		const { access, refresh } = response.data;

		setTokens({ access, refresh });

		await queryClient.invalidateQueries({
			queryKey: ["currentUser"],
		});

		return response.data
	}

	function logout() {
		clearTokens();
		queryClient.clear();
	}

	const value = useMemo(
		() => ({
			isAuthenticated,
			isLoading: isBootstrapping,
			login,
			logout,
		}),
		[isAuthenticated, isBootstrapping]
	);


	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;

}

export function useAuth() {
	const context = useContext(AuthContext);

	if (!context) {
		throw new Error("useAuth must be used within AuthProvider");
	}

	return context;
}
