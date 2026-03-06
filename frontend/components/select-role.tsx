"use client"

import { useQueryClient, useQuery, useMutation } from "@tanstack/react-query";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import api from "../lib/api";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Check, LoaderCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export default function SelectRole() {

	// TODO: Do I really need to fetch this again here, am I even fetching it again??
	//
	const { data, isLoading } = useQuery({
		queryKey: ["currentUser"],
		queryFn: async () => {
			const response = await api.get("/auth/me/");
			return response.data;
		},

	});
	const [selected, setSelected] = useState<string | null>(null);

	const router = useRouter();


	const selectRoleMutation = useMutation(
		{
			mutationFn: (role: string) => api.patch(
				"/auth/me/",
				{ "role": role }
			),
			onSuccess: () =>
				router.replace("/dashboard"),
			onError: (error) => {
				toast.error(error.message)
			}
		},
	)

	function handleSelect(role: string) {
		setSelected(role === selected ? null : role);
		selectRoleMutation.mutate(role);
	}

	return (
		<div className="flex flex-col items-center gap-1 text-center">
			<h1 className="text-2xl font-bold">Select role</h1>
			<p className="text-sm text-balance text-muted-foreground">
				Select the role you want to log in as
			</p>

			<div className="w-full mt-4">
				<ul className="flex flex-col gap-1">
					{data?.roles?.map((role: string) => {
						const active = selected === role;
						return (
							<li key={role}>
								<button
									onClick={() => handleSelect(role)}
									className={`w-full flex items-center justify-between px-3 py-2.5 border rounded-md text-sm transition-colors ${active
										? "bg-primary text-white"
										: "text-zinc-700 hover:bg-zinc-100"
										}`}
								>
									<span className="font-medium">{role}</span>
									{active && (
										selectRoleMutation.isPending
											? <LoaderCircle className="animate-spin" />
											: <Check className="w-4 h-4 opacity-80" strokeWidth={2.5} />
									)
									}
								</button>
							</li>
						);
					})}
				</ul>
			</div>
		</div>
	)
}
