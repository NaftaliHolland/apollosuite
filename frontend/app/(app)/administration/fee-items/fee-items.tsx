"use client"

import { useState } from "react";
import api from "@/lib/api";
import { useQuery, useMutation } from "@tanstack/react-query";
import { FeeItem, LocalStorageSchool } from "@/types";
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
import { Plus } from "lucide-react";

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
								className="group flex flex-col p-5 rounded-sm hover:bg-muted/60 transition-colors border border-1"
							>
								<div className="flex-1 space-y-2">
									<h3 className="font-semibold text-foreground">
										{feeItem.name}
									</h3>
									<p className="text-sm text-muted-foreground leading-relaxed">
										{feeItem.description}
									</p>
								</div>
							</div>
						)}
					</div>
				</>
			)}
		</div>
	)
}
