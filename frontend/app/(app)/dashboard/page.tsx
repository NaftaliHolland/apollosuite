"use client"

import { useAuth } from "@/context/AuthProvider";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import AdminDashboard from "./admin-dashboard";

export default function Dashboard() {

	const { data: user } = useCurrentUser();

	const activeRole = user?.active_role;

	if (activeRole === "admin") return <AdminDashboard />
	if (activeRole === "parent") return <p>Parent dashboard</p>
	if (activeRole === "teacher") return <p>Teacher dashboard</p>
}
