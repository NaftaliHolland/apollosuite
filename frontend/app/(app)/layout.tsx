"use client"

import React from "react";
import ProtectedRoute from "@/components/protected-route";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { AdminSidebar } from "@/components/admin-sidebar";
import { Sidebar } from "@/components/ui/sidebar";
import { SiteHeader } from "@/components/site-header";

export default function AppLayout({ children }: { children: React.ReactNode }) {

	const { data: user } = useCurrentUser();

	const activeRole = user?.active_role;

	let SidebarComponent: ({ ...props }: React.ComponentProps<typeof Sidebar>) => any = AdminSidebar;

	switch (activeRole) {
		case "admin":
			SidebarComponent = AdminSidebar;
			break;
		case "parent":
			// TODO: fix this
			SidebarComponent = AdminSidebar;
			break;
		case "parent":
			// TODO: fix this
			SidebarComponent = AdminSidebar;
			break;
	}


	return (
		<ProtectedRoute>
			<SidebarProvider
				style={
					{
						"--sidebar-width": "calc(var(--spacing) * 48)",
						"--header-height": "calc(var(--spacing) * 12)",
					} as React.CSSProperties
				}
			>
				<SidebarComponent variant="inset" />

				<SidebarInset>
					<SiteHeader />
					{children}
				</SidebarInset>
			</SidebarProvider>
		</ProtectedRoute>
	)
}
