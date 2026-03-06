"use client"

import { useAuth } from "@/context/AuthProvider";
import { useCurrentUser } from "@/hooks/useCurrentUser";

export default function Dashboard() {

	const { data: user } = useCurrentUser();

	const activeRole = user?.active_role;

	if (activeRole === "parent") return <p>Parent dashboard</p>
	if (activeRole === "admin") return <p>Admin dashboard</p>
	if (activeRole === "teacher") return <p>Teacher dashboard</p>
}
