"use client"

import { useAuth } from "@/context/AuthProvider";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useCurrentUser } from "@/hooks/useCurrentUser";


export default function ProtectedRoute({ children }: { children: React.ReactNode }) {

	const { data: user, isLoading } = useCurrentUser();

	const router = useRouter();
	const [mounted, setMounted] = useState<boolean>(false);

	useEffect(() => {
		setMounted(true);
	}, [])

	useEffect(() => {
		if (mounted && !isLoading && !user) {
			router.replace("/login");
		}
	}, [mounted, user, isLoading, router]);

	if (!mounted) return null;

	if (isLoading) {
		return <div>Loading...</div>
	}

	if (!user) return null;

	return <>{children}</>;
}
