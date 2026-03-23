"use client"

import * as z from "zod";
import { cn } from "@/lib/utils";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { useForm, Controller } from "react-hook-form";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { LocalStorageSchool, AcademicYear, Grade, Stream } from "@/types";
import { zodResolver } from "@hookform/resolvers/zod";
import {
	Field,
	FieldGroup,
	FieldLabel,
	FieldError,
	FieldDescription,
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
	streams: z
		.array(z.string())
})

interface GradeProps {
	handleClose: () => void;
}

export function GradeForm({ handleClose }: GradeProps) {

	const currentSchool = localStorage.getItem("active_school");

	const school: LocalStorageSchool = JSON.parse(currentSchool ? currentSchool : "");

	const form = useForm<z.infer<typeof formSchema>>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			name: "",
			description: "",
			streams: [],
		}
	})

	const queryClient = useQueryClient();

	const streamsQuery = useQuery({
		queryKey: ["streams"],
		queryFn: async (): Promise<Stream[]> => {
			const response = await api.get(`schools/${school.school_id}/streams/`);

			return response.data;
		}
	})

	const addGradeMutation = useMutation({
		mutationFn: async (data: z.infer<typeof formSchema>): Promise<Grade> => {
			const response = await api.post(`schools/${school.school_id}/grades/`, data)

			return response.data
		},
		onSuccess: () => {
			toast.success("Grade added successfully")
			queryClient.invalidateQueries({ queryKey: ["grades"] });
			form.reset();
			handleClose();
		},
		onError: (error: any) => {
			toast.error(error.response?.data?.detail);
		}
	})

	function onSubmit(data: z.infer<typeof formSchema>) {
		addGradeMutation.mutate(data)
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

				{streamsQuery.isLoading && <p>Loading ... </p>
				}
				{streamsQuery.error && <p className="text-red-500">{streamsQuery.error.message}</p>
				}

				{streamsQuery.data &&
					<Controller
						name="streams"
						control={form.control}
						render={({ field, fieldState }) => (
							<Field data-invalid={fieldState.invalid}>
								<FieldLabel>Streams</FieldLabel>
								<FieldDescription>
									Select streams available for this class
								</FieldDescription>
								<div className="flex flex-wrap gap-2">
									{streamsQuery.data.map((stream) => {
										const isChecked = field.value?.includes(stream.id.toString());

										return (
											<div key={stream.id} className="flex gap-2">
												<Checkbox
													checked={isChecked}
													onCheckedChange={(checked: boolean) => {
														const next = checked
															? [...(field.value ?? []), stream.id.toString()]
															: (field.value ?? []).filter((v: string) => v !== stream.id.toString());
														field.onChange(next);
													}}
												/>
												<FieldLabel>
													{stream.name}
												</FieldLabel>
											</div>
										);
									})}
								</div>
								{fieldState.error && (
									<p className="text-sm text-destructive">{fieldState.error.message}</p>
								)}
							</Field>
						)}
					/>
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
						disabled={addGradeMutation.isPending}
					>
						{addGradeMutation.isPending &&
							<LoaderCircle className="animate-spin" />}
						Create
					</Button>
				</div>
			</FieldGroup>
		</form>
	)
}
