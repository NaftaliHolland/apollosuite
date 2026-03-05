import React from "react";
import ProtectedRoute from "@/components/protected-route";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {

	return (
		<ProtectedRoute>
			{children}
		</ProtectedRoute>
	)
}
