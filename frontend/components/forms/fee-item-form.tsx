"use client"

import * as z from "zod";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { useForm, Controller } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { LocalStorageSchool, AcademicYear, FeeItem } from "@/types";
import { zodResolver } from "@hookform/resolvers/zod";
import {
	Popover,
	PopoverTrigger,
	PopoverContent,
} from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import {
	Field,
	FieldGroup,
	FieldLabel,
	FieldError,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { LoaderCircle } from "lucide-react";

const formSchema = z.object({
	name: z
		.string()
		.min(2, "Name must be more than 5 characters"),
	description: z
		.string()
		.min(5, "Name must be more than 5 characters")
		.optional(),
})

interface FeeItemProps {
	handleClose: () => void;
}

export function FeeItemForm({ handleClose }: FeeItemProps) {

	const currentSchool = localStorage.getItem("active_school");

	const school: LocalStorageSchool = JSON.parse(currentSchool ? currentSchool : "");

	const form = useForm<z.infer<typeof formSchema>>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			name: "",
			description: "",
		}
	})

	const queryClient = useQueryClient();

	const addFeeItemMutation = useMutation({
		mutationFn: async (data: z.infer<typeof formSchema>): Promise<AcademicYear> => {
			const response = await api.post(`schools/${school.school_id}/finance/fee-items/`, data)

			return response.data
		},
		onSuccess: () => {
			toast.success("Fee Item added successfully")
			queryClient.invalidateQueries({ queryKey: ["feeItems"] });
			form.reset();
			handleClose();
		},
		onError: (error: any) => {
			toast.error(error.response?.data?.detail);
		}
	})

	function onSubmit(data: z.infer<typeof formSchema>) {
		addFeeItemMutation.mutate(data)
	}

	return (
		<form onSubmit={form.handleSubmit(onSubmit)}>
			<FieldGroup>
				<Controller
					name="name"
					control={form.control}
					render={({ field, fieldState }) => (
						<Field data-invalid={fieldState.invalid}>
							<FieldLabel htmlFor="name">
								Name
							</FieldLabel>
							<Input
								{...field}
								id="name"
								aria-invalid={fieldState.invalid}
								autoComplete="off"
							/>
							<FieldError errors={[fieldState.error]} />
						</Field>
					)}
				/>
				<Controller
					name="description"
					control={form.control}
					render={({ field, fieldState }) => (
						<Field data-invalid={fieldState.invalid}>
							<FieldLabel htmlFor="name">
								Description
							</FieldLabel>
							<Textarea
								{...field}
								id="description"
								aria-invalid={fieldState.invalid}
								autoComplete="off"
							/>

						</Field>
					)}
				/>

				<div className="flex justify-end gap-4">
					<Button
						variant="outline"
						onClick={(e) => {
							e.preventDefault()
							handleClose()
						}}
					>
						Close
					</Button>
					<Button
						disabled={addFeeItemMutation.isPending}
					>
						{addFeeItemMutation.isPending &&
							<LoaderCircle className="animate-spin" />}
						Create
					</Button>
				</div>
			</FieldGroup>
		</form>
	)
}
