import { useQuery } from "@tanstack/react-query";
import api, { getAccessToken } from "../lib/api";


export function useCurrentUser() {
	const token = getAccessToken();

	return useQuery({
		queryKey: ["currentUser"],
		queryFn: async () => {
			const res = await api.get("/me");
			return res.data;
		},
		enabled: !!token,
	});
}
