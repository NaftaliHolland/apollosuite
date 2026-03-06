import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { AdminSidebar } from "@/components/admin-sidebar";
import { SiteHeader } from "@/components/site-header";

export default function AdminDashboard() {
	return (
		<SidebarProvider
			style={
				{
					"--sidebar-width": "calc(var(--spacing) * 48)",
					"--header-height": "calc(var(--spacing) * 12)",
				} as React.CSSProperties
			}
		>
			<AdminSidebar variant="inset" />
			<SidebarInset>
				<SiteHeader />
				<div className="flex flex-1 flex-col">
					<div className="@container/main flex flex-1 flex-col gap-2">
						<div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
							{/*<SectionCards />*/}
							<div className="px-4 lg:px-6">
								{/*<ChartAreaInteractive />*/}
							</div>
							{/*<DataTable data={data} />*/}
						</div>
					</div>
				</div>

			</SidebarInset>

		</SidebarProvider>
	)
}
