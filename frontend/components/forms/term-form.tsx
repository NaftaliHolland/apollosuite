"use client"

import { format } from "date-fns";
import * as z from "zod";
import { useState } from "react";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { useForm, Controller } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { LocalStorageSchool, AcademicYear, Term } from "@/types";
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
import {
	Select,
	SelectContent,
	SelectGroup,
	SelectItem,
	SelectLabel,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";

const formSchema = z.object({
	name: z
		.string()
		.min(5, "Name must be more than 5 characters"),
	order: z
		.string()
		.min(1),
	start_date: z.date(),
	end_date: z.date(),
});

interface TermFormProps {
	handleClose: () => void;
	academicYearId?: number;
}

export function TermForm({ handleClose, academicYearId }: TermFormProps) {

	const currentSchool = localStorage.getItem("active_school");

	const school: LocalStorageSchool = JSON.parse(currentSchool ? currentSchool : "");

	const form = useForm<z.infer<typeof formSchema>>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			name: "",
			order: "",
			start_date: undefined,
			end_date: undefined,
		}
	})

	const queryClient = useQueryClient();

	const addTermMutation = useMutation({
		mutationFn: async (data: z.infer<typeof formSchema>): Promise<Term> => {
			const response = await api.post(`schools/${school.school_id}/academic-years/${academicYearId}/terms/`,
				{
					...data,
					"start_date": format(data.start_date, "yyy-MM-dd"),
					"end_date": format(data.end_date, "yyy-MM-dd")
				})

			return response.data
		},
		onSuccess: () => {
			toast.success("Term added successfully")
			queryClient.invalidateQueries({ queryKey: [academicYearId, "terms"] });
			form.reset();
			handleClose();
		},
		onError: (error: any) => {
			toast.error(error.response?.data?.detail);
		}
	})

	function onSubmit(data: z.infer<typeof formSchema>) {
		addTermMutation.mutate(data)
	}

	// NOTE: This can just be one state and the values for start_date and end_date be in an object
	//
	const [startDateOpen, setStartDateOpen] = useState(false)

	const [endDateOpen, setEndDateOpen] = useState(false)

	const selectedStartDate = form.watch("start_date");

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

						</Field>
					)}
				/>
				<Controller
					name="order"
					control={form.control}
					render={({ field, fieldState }) => (
						<Field data-invalid={fieldState.invalid}>
							<FieldLabel>
								Order
							</FieldLabel>
							<Select
								name={field.name}
								value={field.value}
								onValueChange={field.onChange}
							>
								<SelectTrigger aria-invalid={fieldState.invalid}>
									<SelectValue placeholder="Select order" />
								</SelectTrigger>
								<SelectContent>
									<SelectGroup>
										<SelectItem value="1">1</SelectItem>
										<SelectItem value="2">2</SelectItem>
										<SelectItem value="3">3</SelectItem>
									</SelectGroup>
								</SelectContent>
							</Select>
							{fieldState.invalid && <FieldError>Please select order</FieldError>}
						</Field>
					)}
				/>

				<div className="flex gap-4">
					<Controller
						name="start_date"
						control={form.control}
						render={({ field, fieldState }) => (
							<Field data-invalid={fieldState.invalid} className="flex-1">
								<FieldLabel htmlFor="start_date">Start Date</FieldLabel>
								<Popover open={startDateOpen} onOpenChange={setStartDateOpen}>
									<PopoverTrigger asChild>
										<Button
											variant="outline"
											id="date"
											className="justify-start font-normal flex-1"
										>
											{field.value ? field.value.toLocaleDateString() : "Select start date"}
										</Button>
									</PopoverTrigger>
									<PopoverContent className="overflow-hidden p-0" align="start">
										<Calendar
											mode="single"
											className="w-full"
											selected={field.value}
											defaultMonth={field.value}
											captionLayout="dropdown"
											disabled={(date) => {
												return date <= new Date()
											}}
											onSelect={(date) => {
												field.onChange(date)
												setStartDateOpen(false)
											}}
										/>
									</PopoverContent>
								</Popover>
								{fieldState.invalid && (
									<FieldError errors={[fieldState.error]} />
								)}
							</Field>
						)}
					/>

					<Controller
						name="end_date"
						control={form.control}
						render={({ field, fieldState }) => (
							<Field data-invalid={fieldState.invalid} className="flex-1">
								<FieldLabel htmlFor="start-date">End Date</FieldLabel>
								<Popover open={endDateOpen} onOpenChange={setEndDateOpen}>
									<PopoverTrigger asChild>
										<Button
											variant="outline"
											id="date"
											className="justify-start font-normal flex-1"
										>
											{field.value ? field.value.toLocaleDateString() : "Select end date"}
										</Button>
									</PopoverTrigger>
									<PopoverContent className="overflow-hidden p-0" align="start">
										<Calendar
											mode="single"
											className="w-full"
											selected={field.value}
											defaultMonth={field.value}
											captionLayout="dropdown"
											disabled={(date) => {
												if (!selectedStartDate) return false
												return date <= selectedStartDate
											}}
											onSelect={(date) => {
												field.onChange(date)
												setEndDateOpen(false)
											}}
										/>
									</PopoverContent>
								</Popover>
								{fieldState.invalid && (
									<FieldError errors={[fieldState.error]} />
								)}
							</Field>
						)}
					/>
				</div>
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
						disabled={addTermMutation.isPending}
					>
						{addTermMutation.isPending &&
							<LoaderCircle className="animate-spin" />}
						Create
					</Button>
				</div>
			</FieldGroup>
		</form>
	)
}
