"use client"

import { useAuth } from "@/context/AuthProvider";
import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useCurrentUser } from "@/hooks/useCurrentUser";


export default function ProtectedRoute({ children }: { children: React.ReactNode }) {

	const { data: user, isLoading, isPending } = useCurrentUser();

	const router = useRouter();

	useEffect(() => {
		if (!user && !isLoading && !isPending) {
			router.replace("/login");
		}
	}, [user, isLoading]);


	if (isLoading || (!user && !isLoading)) {
		return <p>Loading...</p>
	}

	return children;
}
