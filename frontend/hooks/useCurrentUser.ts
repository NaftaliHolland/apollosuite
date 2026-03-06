import { useQuery } from "@tanstack/react-query";
import api, { getAccessToken } from "../lib/api";


export function useCurrentUser() {
	const token = getAccessToken();

	return useQuery({
		queryKey: ["currentUser", token],
		queryFn: async () => {
			const response = await api.get("/auth/me/");
			return response.data;
		},
		enabled: !!token,
	});
}
