"use client"

import * as z from "zod";
import { LocalStorageSchool, Grade } from "@/types";
import { zodResolver } from "@hookform/resolvers/zod";
import api from "@/lib/api";
import { useForm, Controller } from "react-hook-form";
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectLabel, SelectValue, SelectGroup } from "@/components/ui/select";
import {
	Field,
	FieldGroup,
	FieldLabel,
	FieldError,
} from "@/components/ui/field";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { LoaderCircle } from "lucide-react";

const TermSchema = z.object({
	term: z.number(),
	amount: z.number(),
});

const formSchema = z.object(
	{
		fee_item: z
			.string("Fee Item is required"),
		grade: z
			.string("Grade is required"),
		amount: z
			.string()
			.min(1, "Amount cannot be less than 1")
			.max(100000000, "Maximum amount is 10,000,000")
		,
		frequency: z
			.enum(["per_term", "yearly", "one_time", ""]),
		terms: z.array(TermSchema),
	}
)


export const FeeSchema = z.object({
	academic_year: z.number(),
	fee_item: z.number(),
	grade: z.number(),
});

//type FormInput = z.input<typeof formSchema>;
type FormValues = z.infer<typeof formSchema>;

interface GradeFeeAssignmentFormProps {
	handleClose: () => void;
	selectedFeeItem?: number;
}

export function GradeFeeAssignmentForm({ handleClose, selectedFeeItem }: GradeFeeAssignmentFormProps) {

	const currentSchool = localStorage.getItem("active_school");

	const school: LocalStorageSchool = JSON.parse(currentSchool ? currentSchool : "");

	const gradesQuery = useQuery({
		queryKey: ["grades"],
		queryFn: async (): Promise<Grade[]> => {
			const response = await api.get(`schools/${school?.school_id}/grades/`)
			return response.data
		}
	});

	const form = useForm<FormValues>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			fee_item: selectedFeeItem?.toString(),
			grade: "",
			amount: undefined,
			frequency: "",
		}
	})

	const assignFeeMutation = useMutation(
		{
			mutationFn: async (data: FormValues) => {
				const response = await api.post(`schools/${school.school_id}/finance/grade-fee-items/`, data)

				return response.data
			},
			onSuccess: () => {
				toast.success("Assigned to grade successfully")
				form.reset();
				handleClose();
			},
			onError: (error: any) => {
				toast.error(error.response?.data?.detail);
			}
		}
	)

	function onSubmit(data: FormValues) {
		assignFeeMutation.mutate(data)
	}

	const frequency = form.watch("frequency");

	const terms = ["Term 1", "Term 2", "Term 3", "Term 4"];

	return (
		<form onSubmit={form.handleSubmit(onSubmit)}>
			<FieldGroup>
				<Controller
					name="grade"
					control={form.control}
					render={({ field, fieldState }) => (
						<Field data-invalid={fieldState.invalid}>
							<FieldLabel htmlFor="grade">Grade</FieldLabel>
							<Select
								name={field.name}
								value={field.value}
								onValueChange={field.onChange}
							>
								<SelectTrigger
									id="grade"
									aria-invalid={fieldState.invalid}
									disabled={gradesQuery.isLoading}

								>
									{gradesQuery.isLoading
										? (
											<div className="flex items-center gap-2">
												Loading...
												<LoaderCircle className="animate-spin" />
											</div>
										)
										: <SelectValue placeholder="Select grade" />
									}
								</SelectTrigger>
								<SelectContent>
									<SelectGroup>
										{gradesQuery.data &&
											gradesQuery.data.map((grade, index) =>
												<SelectItem key={index} value={grade.id.toString()}>{grade.name}</SelectItem>
											)
										}
									</SelectGroup>
								</SelectContent>
							</Select>
							{fieldState.invalid && (
								<FieldError errors={[fieldState.error]} />
							)}
						</Field>
					)}
				/>

				<Controller
					name="frequency"
					control={form.control}
					render={({ field, fieldState }) => (
						<Field data-invalid={fieldState.invalid}>
							<FieldLabel htmlFor="frequency">Frequency</FieldLabel>
							<Select
								name={field.name}
								value={field.value}
								onValueChange={field.onChange}
							>
								<SelectTrigger
									id="frequency"
									aria-invalid={fieldState.invalid}
								>
									<SelectValue placeholder="Select frequency" />
								</SelectTrigger>
								<SelectContent>
									<SelectGroup>
										<SelectItem value="per_term">
											Per Term
										</SelectItem>
										<SelectItem value="yearly">
											Yearly
										</SelectItem>
										<SelectItem value="one_time">
											Once
										</SelectItem>
									</SelectGroup>
								</SelectContent>
							</Select>
							{fieldState.invalid && (
								<FieldError errors={[fieldState.error]} />
							)}
						</Field>
					)}
				/>

				{(frequency == "one_time" || frequency == "yearly") && <Controller
					name="amount"
					control={form.control}
					render={({ field, fieldState }) => (
						<Field data-invalid={fieldState.invalid}>
							<FieldLabel htmlFor="amount">Amount</FieldLabel>
							<Input
								{...field}
								id="amount"
								type="number"
								required
							/>
							{fieldState.invalid && (
								<FieldError errors={[fieldState.error]} />
							)}
						</Field>
					)}
				/>}
				{frequency == "per_term" &&
					<div className="flex flex-col gap-3">
						{terms.map((term) => (
							<div
								key={term}
								className="flex items-center rounded-md border border-input overflow-hidden focus-within:ring-2 focus-within:ring-ring"
							>
								<Label className="px-3 py-2 bg-muted text-muted-foreground text-sm font-mono border-r border-input min-w-[90px]">
									{term}
								</Label>
								<Input
									type="number"
									placeholder="0.00"
									className="border-0 rounded-none focus-visible:ring-0 focus-visible:ring-offset-0"
								/>
							</div>
						))}
					</div>
				}

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
						disabled={assignFeeMutation.isPending}
					>
						{assignFeeMutation.isPending &&
							<LoaderCircle className="animate-spin" />}
						Create
					</Button>
				</div>
			</FieldGroup>
		</form>
	)

}
