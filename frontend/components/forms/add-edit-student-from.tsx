"use client"
// Write zod validation
// Create the form instance
// Create the form - will will have 3 here but taking the same form
//
//
import { useForm, Controller, UseFormReturn } from "react-hook-form";
import { LoaderCircle } from "lucide-react";
import { Field, FieldDescription, FieldLabel, FieldGroup, FieldError } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectLabel, SelectValue, SelectGroup } from "@/components/ui/select";
import api from "@/lib/api";
import { useMutation, useQuery } from "@tanstack/react-query";
import { LocalStorageSchool } from "@/types";

// TODO: Write validation for phone number
//

const formSchema = z.object({
	first_name: z
		.string()
		.min(1, "First name is required")
		.max(255, "Cannot exeed 255 characters"),
	last_name: z
		.string()
		.min(1, "Last name is required")
		.max(255, "Cannot exeed 255 characters"),
	parent_first_name: z
		.string()
		.min(1, "Parent first name is required")
		.max(255, "Cannot exeed 255 characters"),
	parent_last_name: z
		.string()
		.min(1, "Parent last name is required")
		.max(255, "Cannot exeed 255 characters"),
	parent_email: z
		.string()
		.email("Invalid email address")
		.optional(),
	parent_phone_number: z
		.string()
		.min(10, "Phone number is too short")
		.max(15, "Phone number is too long"),
	grade: z
		.coerce
		.number()
		.optional(),
	stream: z
		.coerce
		.number()
		.optional(),
	transfered_from: z
		.string()
		.optional()
})

export default function NewStudent() {
	const form = useForm<z.input<typeof formSchema>>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			first_name: "",
			last_name: "",
			parent_first_name: "",
			parent_last_name: "",
			parent_phone_number: "",
		}
	})

	function onSubmit(data: z.infer<typeof formSchema>) {
		console.log(data)
	}


	return (
		<div className="p-2 sm:p-4 flex flex-col gap-2 sm:gap-4">
			<h2 className="font-medium">Add New Student</h2>
			<Tabs defaultValue="basic_information">
				<TabsList variant="line" className="gap-2 sm:gap-12 mb-4">
					<TabsTrigger value="basic_information">Basic Information</TabsTrigger>
					<TabsTrigger value="parent_details">Parent Details</TabsTrigger>
					<TabsTrigger value="additional_details">Additional Details</TabsTrigger>
				</TabsList>

				<TabsContent value="basic_information" className="w-full sm:w-[60vw]">
					<BasicInformation form={form} />
				</TabsContent>

				<TabsContent value="parent_details">
					<p>Parent Details</p>
				</TabsContent>

				<TabsContent value="additional_details">
					<p>Additional Details</p>
				</TabsContent>

			</Tabs>
		</div>
	)
}

export function BasicInformation({ form }: { form: UseFormReturn<any> }) {

	const currentSchool = localStorage.getItem("active_school");

	const school: LocalStorageSchool = JSON.parse(currentSchool ? currentSchool : "");

	const gradesQuery = useQuery({
		queryKey: ["grades"],
		queryFn: () => api.get(`schools/${school?.school_id}/grades/`)
	});

	return (
		<form>
			<div className="flex flex-col gap-4">
				<FieldGroup >
					<div className="flex flex-row gap-2 sm:gap-4">
						<Controller
							name="first_name"
							control={form.control}
							render={({ field, fieldState }) => (
								<Field data-invalid={fieldState.invalid}>
									<FieldLabel htmlFor="first-name">First Name</FieldLabel>
									<Input
										{...field}
										id="first-name"
										type="text"
										required
									/>
									{fieldState.invalid && (
										<FieldError errors={[fieldState.error]} />
									)}
								</Field>
							)}
						/>

						<Controller
							name="last_name"
							control={form.control}
							render={({ field, fieldState }) => (
								<Field data-invalid={fieldState.invalid}>
									<FieldLabel htmlFor="first-name">Last Name</FieldLabel>
									<Input
										{...field}
										id="last-name"
										type="text"
										required
									/>
									{fieldState.invalid && (
										<FieldError errors={[fieldState.error]} />
									)}
								</Field>
							)}
						/>
					</div>

					<div className="flex flex-row gap-2 sm:gap-4">

						<div className="flex flex-row gap-2 sm:gap-4">
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
													: <SelectValue placeholder="Select a fruit" />
												}
											</SelectTrigger>
											<SelectContent>
												<SelectGroup>
													<SelectItem value="apple">Apple</SelectItem>
													<SelectItem value="banana">Banana</SelectItem>
													<SelectItem value="blueberry">Blueberry</SelectItem>
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
								name="stream"
								control={form.control}
								render={({ field, fieldState }) => (
									<Field data-invalid={fieldState.invalid}>
										<FieldLabel htmlFor="stream">Stream</FieldLabel>
										<Select
											name={field.name}
											value={field.value}
											onValueChange={field.onChange}
										>
											<SelectTrigger
												id="stream"
												aria-invalid={fieldState.invalid}

											>
												<SelectValue placeholder="Select a stream" />
											</SelectTrigger>
											<SelectContent>
												<SelectGroup>
													<SelectItem value="apple">Apple</SelectItem>
													<SelectItem value="banana">Banana</SelectItem>
													<SelectItem value="blueberry">Blueberry</SelectItem>
												</SelectGroup>
											</SelectContent>
										</Select>
										{fieldState.invalid && (
											<FieldError errors={[fieldState.error]} />
										)}
									</Field>
								)}
							/>
						</div>
					</div>
				</FieldGroup >

				<div className="flex justify-between">
				</div>
			</div>
		</form>
	)
}

export function ParentDetails() {
	return (
		<div>Basic info</div>
	)
}

export function AdditionalDetails() {

	return (
		<div>Basic info</div>
	)
}
