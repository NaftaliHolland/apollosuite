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
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { LoaderCircle } from "lucide-react";

const formSchema = z.object(
	{
		fee_item: z
			.string("Fee Item is required"),
		grade: z
			.string("Grade is required"),
		amount: z
			.coerce
			.number()
			.positive()
			.min(1, "Amount cannot be less than 1")
			.max(100000000, "Maximum amount is 10,000,000"),
		frequency: z
			.enum(["per_term", "yearly", "one_time"])
	}
)

type FormInput = z.input<typeof formSchema>;
type FormOutput = z.infer<typeof formSchema>;

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

	const form = useForm<FormInput, any, FormOutput>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			fee_item: selectedFeeItem?.toString(),
			grade: "",
			amount: 0,
			frequency: "per_term",
		}
	})

	const assignFeeMutation = useMutation(
		{
			mutationFn: async (data: FormOutput) => {
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

	function onSubmit(data: FormOutput) {
		assignFeeMutation.mutate(data)
	}

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
