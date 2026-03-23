"use client"

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
	DropdownMenu,
	DropdownMenuTrigger,
	DropdownMenuItem,
	DropdownMenuContent,
	DropdownMenuGroup,
	DropdownMenuLabel,
	DropdownMenuPortal,
	DropdownMenuSeparator,
	DropdownMenuShortcut,
	DropdownMenuSub,
	DropdownMenuSubContent,
	DropdownMenuSubTrigger,
} from "@/components/ui/dropdown-menu";
import { FeeItem, LocalStorageSchool } from "@/types";
import { GradeFeeAssignmentForm } from "@/components/forms/grade-fee-assignment-form";
import { FeeItemForm } from "@/components/forms/fee-item-form";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog"
import { Plus, Ellipsis, Pencil, GraduationCap } from "lucide-react";

export function FeeItems() {

	const currentSchool = localStorage.getItem("active_school");

	const school: LocalStorageSchool = JSON.parse(currentSchool ? currentSchool : "");

	const { data: feeItems, isLoading, error } = useQuery({
		queryKey: ["feeItems"],
		queryFn: async (): Promise<FeeItem[]> => {
			const response = await api.get(`/schools/${school.school_id}/finance/fee-items/`)

			return response.data;
		},
	})

	const [addFeeItemOpen, setAddFeeItemOpen] = useState(false);
	const [assignToGradesOpen, setAssignToGradesOpen] = useState(false);

	const [selectedFeeItem, setSelectedFeeItem] = useState<number | undefined>(undefined);

	return (
		<div className="max-w-7xl mx-auto">

			{isLoading && <div> loading ...</div>}
			{error && <div className="text-red-500">{error.message}</div>}


			{feeItems && (
				<>
					<div className="flex justify-between w-full space-y-4">
						<p className="font-semibold text-lg">Fee Items</p>
						<Dialog open={addFeeItemOpen} onOpenChange={setAddFeeItemOpen}>
							<DialogTrigger asChild>
								<Button
								>
									Add Fee Item
								</Button>
							</DialogTrigger>
							<DialogContent>
								<DialogHeader>
									<DialogTitle>Add Fee Item</DialogTitle>
									<DialogDescription className="sr-only">
										Add a new fee Item
									</DialogDescription>
								</DialogHeader>
								<FeeItemForm handleClose={() => setAddFeeItemOpen(false)} />
							</DialogContent>
						</Dialog>
					</div>
					<div className="grid gap-6 grid-cols-1 md:grid-cols-3 lg:grid-cols-4">
						{feeItems.map((feeItem: FeeItem) =>
							<div
								key={feeItem.id}
								className="group flex flex-col p-4 rounded-sm border border-1"
							>
								<div className="flex-1 space-y-2">
									<div className="flex justify-between align-center">
										<h3 className="font-semibold text-foreground">
											{feeItem.name}
										</h3>
										<DropdownMenu>
											<DropdownMenuTrigger asChild>
												<Button
													variant="ghost"
													size="icon"
													aria-label="actions"
												>


													<Ellipsis />
												</Button>
											</DropdownMenuTrigger>
											<DropdownMenuContent className="w-fit">
												<DropdownMenuLabel>Actions</DropdownMenuLabel>
												<DropdownMenuItem

												>
													<Pencil />
													Edit
												</DropdownMenuItem>
												<DropdownMenuItem
													onSelect={() => {
														setSelectedFeeItem(feeItem.id)
														setAssignToGradesOpen(true)
													}
													}
												>
													<GraduationCap />
													Assign to grades
												</DropdownMenuItem>
												<DropdownMenuSeparator />
												<DropdownMenuItem>
													{/* TODO: This should be a toggle for active or inactive */}
													Active
												</DropdownMenuItem>
											</DropdownMenuContent>

										</DropdownMenu>
									</div>
									<p className="text-sm text-muted-foreground leading-relaxed">
										{feeItem.description}
									</p>
								</div>
							</div>
						)}
					</div>

					{/* TODO: Should this be a separate component - I think so, it looks weird here */}
					<Dialog open={assignToGradesOpen} onOpenChange={setAssignToGradesOpen}>
						<DialogContent>
							<DialogHeader>
								<DialogTitle>Add Fee Item</DialogTitle>
								<DialogDescription className="sr-only">
									Add a new fee Item
								</DialogDescription>
							</DialogHeader>
							<GradeFeeAssignmentForm handleClose={() => setAssignToGradesOpen(false)} selectedFeeItem={selectedFeeItem} />
						</DialogContent>
					</Dialog>
				</>
			)}
		</div>
	)
}
