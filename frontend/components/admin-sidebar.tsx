"use client"

import * as React from "react"
import {
	GalleryVerticalEnd,
	LucideIcon,
	Home,
	GraduationCap,
	Users,
	Banknote,
	ChevronRight,
	ClipboardList,
} from "lucide-react"
import {
	Collapsible,
	CollapsibleTrigger,
	CollapsibleContent,
} from "@/components/ui/collapsible";
import { usePathname } from "next/navigation";
import Link from "next/link";
import {
	Sidebar,
	SidebarContent,
	SidebarFooter,
	SidebarHeader,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
	SidebarGroup,
	SidebarGroupContent,
	SidebarMenuSub,
	SidebarMenuSubButton,
	SidebarMenuSubItem,
} from "@/components/ui/sidebar"

const data = {
	//	user: {
	//		name: "shadcn",
	//		email: "m@example.com",
	//		avatar: "/avatars/shadcn.jpg",
	//	},
	navMain: [
		{
			title: "Dashboard",
			url: "/dashboard",
			icon: Home,
		},
		{
			title: "Students",
			url: "/students",
			icon: Users,
		},
		{
			title: "Teachers",
			url: "#",
			icon: GraduationCap,
		},
		{
			title: "Finance",
			url: "#",
			icon: Banknote,
			items: [
				{
					title: "Fee collection",
					url: "finance/fee-collection"
				},
				{
					title: "School expenses",
					url: "finance/school-expenses"
				},
			]
		},
		{
			title: "Administration",
			url: "#",
			icon: ClipboardList,
			items: [
				{
					title: "Grades",
					url: "administration/fee-items"
				},
				{
					title: "Fee Items",
					url: "administration/fee-items"
				},
				{
					title: "Discounts",
					url: "administration/discounts"
				},
				{
					title: "Academic Years",
					url: "administration/academic-years"
				},
				{
					title: "Calendar",
					url: "administration/calendar"
				},
			]
		},
	],
	//	navClouds: [
	//		{
	//			title: "Capture",
	//			icon: IconCamera,
	//			isActive: true,
	//			url: "#",
	//			items: [
	//				{
	//					title: "Active Proposals",
	//					url: "#",
	//				},
	//				{
	//					title: "Archived",
	//					url: "#",
	//				},
	//			],
	//		},
	//		{
	//			title: "Proposal",
	//			icon: IconFileDescription,
	//			url: "#",
	//			items: [
	//				{
	//					title: "Active Proposals",
	//					url: "#",
	//				},
	//				{
	//					title: "Archived",
	//					url: "#",
	//				},
	//			],
	//		},
	//		{
	//			title: "Prompts",
	//			icon: IconFileAi,
	//			url: "#",
	//			items: [
	//				{
	//					title: "Active Proposals",
	//					url: "#",
	//				},
	//				{
	//					title: "Archived",
	//					url: "#",
	//				},
	//			],
	//		},
	//	],
	//	navSecondary: [
	//		{
	//			title: "Settings",
	//			url: "#",
	//			icon: IconSettings,
	//		},
	//		{
	//			title: "Get Help",
	//			url: "#",
	//			icon: IconHelp,
	//		},
	//		{
	//			title: "Search",
	//			url: "#",
	//			icon: IconSearch,
	//		},
	//	],
	//	documents: [
	//		{
	//			name: "Data Library",
	//			url: "#",
	//			icon: IconDatabase,
	//		},
	//		{
	//			name: "Reports",
	//			url: "#",
	//			icon: IconReport,
	//		},
	//		{
	//			name: "Word Assistant",
	//			url: "#",
	//			icon: IconFileWord,
	//		},
	//	],
}


export function NavMain({
	items,
}: {
	items: {
		title: string
		url: string
		icon?: LucideIcon
		isActive?: boolean
		items?: {
			title: string
			url: string
		}[]
	}[]
}) {

	const pathname = usePathname();

	return (
		<SidebarGroup>
			<SidebarGroupContent className="flex flex-col gap-2">
				<SidebarMenu>
					{items.map((item) => (
						<Collapsible
							key={item.title}
							asChild
							defaultOpen={item.isActive}
							className="group/collapsible"
						>
							<SidebarMenuItem key={item.title}>
								{item.items
									? (
										<>
											<CollapsibleTrigger asChild>
												<SidebarMenuButton
													tooltip={item.title}
													isActive={
														item.items
															.map((sub) => sub.url)
															.some(path => pathname.includes(path))
													}>
													{item.icon && <item.icon />}
													<span>{item.title}</span>
													<ChevronRight className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90 text-gray-500" />
												</SidebarMenuButton>
											</CollapsibleTrigger>
											<CollapsibleContent>
												<SidebarMenuSub>
													{item.items?.map((subItem) => (
														<SidebarMenuSubItem key={subItem.title}>
															<SidebarMenuSubButton asChild isActive={pathname.includes(subItem.url)}>
																<Link href={subItem.url}>
																	<span>{subItem.title}</span>
																</Link>
															</SidebarMenuSubButton>
														</SidebarMenuSubItem>
													))}
												</SidebarMenuSub>

											</CollapsibleContent>
										</>
									)
									: (
										<SidebarMenuButton
											tooltip={item.title}
											isActive={pathname.includes(item.url)}
											asChild
										>
											<Link href={item.url}>
												{item.icon && <item.icon />}
												<span>{item.title}</span>
											</Link>
										</SidebarMenuButton>
									)
								}
							</SidebarMenuItem>
						</Collapsible>
					))}
				</SidebarMenu>
			</SidebarGroupContent>
		</SidebarGroup>
	)
}
export function AdminSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
	return (
		<Sidebar collapsible="offcanvas" {...props}>
			<SidebarHeader>
				<SidebarMenu>
					<SidebarMenuItem>
						<SidebarMenuButton
							asChild
							className="data-[slot=sidebar-menu-button]:p-1.5!"
						>
							<a href="#">
								<GalleryVerticalEnd className="size-5!" />
								<span className="text-base font-semibold">Apollosuite</span>
							</a>
						</SidebarMenuButton>
					</SidebarMenuItem>
				</SidebarMenu>
			</SidebarHeader>
			<SidebarContent>
				<NavMain items={data.navMain} />
				{/*<NavDocuments items={data.documents} />*/}
				{/*<NavSecondary items={data.navSecondary} className="mt-auto" />*/}
			</SidebarContent>
			<SidebarFooter>
				{/*<NavUser user={data.user} />*/}
			</SidebarFooter>
		</Sidebar>
	)
}
