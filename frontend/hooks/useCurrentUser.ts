"use client"

import { useQuery } from "@tanstack/react-query";
import api, { getAccessToken } from "../lib/api";
import { User } from "@/types";


export function useCurrentUser() {
	const token = getAccessToken();

	return useQuery({
		queryKey: ["currentUser", token],
		queryFn: async (): Promise<User> => {
			const response = await api.get("/auth/me/");
			return response.data;
		},
		enabled: !!token,
	});
}
