"use client"

import { useQuery } from "@tanstack/react-query";
import api, { getAccessToken } from "../lib/api";
import { User } from "@/types";
import { useState, useEffect } from "react";


export function useCurrentUser() {

	const [token, setToken] = useState<string | null>(null);

	useEffect(() => {
		setToken(getAccessToken());
	}, [])

	return useQuery({
		queryKey: ["currentUser", token],
		queryFn: async (): Promise<User> => {
			const response = await api.get("/auth/me/");
			return response.data;
		},
		enabled: !!token,
	});
}
