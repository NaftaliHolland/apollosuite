"use client"
// Write zod validation
// Create the form instance
// Create the form - will will have 3 here but taking the same form
//
//
import { useForm, Controller, UseFormReturn } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { LoaderCircle } from "lucide-react";
import { Field, FieldDescription, FieldLabel, FieldGroup, FieldError } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectLabel, SelectValue, SelectGroup } from "@/components/ui/select";
import api from "@/lib/api";
import { useMutation, useQuery } from "@tanstack/react-query";
import { LocalStorageSchool, Grade } from "@/types";
import { Calendar } from "@/components/ui/calendar";
import {
	Popover,
	PopoverTrigger,
	PopoverContent,
} from "@/components/ui/popover";

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
	gender: z
		.enum(["f", "m", ""])
		.refine((value) => value !== "", { message: "Gender is required" })
	,
	date_of_birth: z
		.coerce
		.date(),
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
			gender: "",
			parent_first_name: "",
			parent_last_name: "",
			parent_phone_number: "",
			grade: "",
			stream: "",
			transfered_from: "",
		}
	})

	function onSubmit(data: z.infer<typeof formSchema>) {
		console.log(data)
	}

	const stepTabs = [
		{
			key: "basic_information",
			title: "Basic information",
		},
		{
			key: "parent_details",
			title: "Parent Details",
		},
		{
			key: "additional_details",
			title: "Additional Details",
		}
	]

	type StepType = "basic_information" | "parent_details" | "additional_details";

	const [currentStep, setCurrentStep] = useState<StepType>("basic_information");


	function handleNext(): void {
		//const currentTab = stepTabs.find((step) => step.key === currentStep);

		//let nextStepIndex = 0;
		//if (currentTab) nextStepIndex = stepTabs.indexOf(currentTab) + 1;

		const nextStepIndex = stepTabs.findIndex((step) => step.key === currentStep) + 1;

		setCurrentStep(stepTabs[nextStepIndex].key as StepType);

	}

	function handlePrev(): void {
		//const currentTab = stepTabs.find((step) => step.key === currentStep);

		//let prevStepIndex = 0;
		//if (currentTab) prevStepIndex = stepTabs.indexOf(currentTab) - 1;
		const prevStepIndex = stepTabs.findIndex((step) => step.key === currentStep) - 1;

		setCurrentStep(stepTabs[prevStepIndex].key as StepType);
	}

	return (
		<div className="p-2 sm:p-4 flex flex-col gap-2 sm:gap-4">
			<h2 className="font-medium">Add New Student</h2>
			<Tabs value={currentStep} onValueChange={(value) => setCurrentStep(value as StepType)}>
				<TabsList variant="line" className="gap-2 sm:gap-12 mb-4">
					{stepTabs.map((step) =>
						<TabsTrigger key={step.key} value={step.key}>{step.title}</TabsTrigger>
					)
					}
				</TabsList>
				<Button
					variant="ghost"
					onClick={() => form.reset()}
					className="ml-auto"
				>
					Clear Form
				</Button>

				<TabsContent value="basic_information" className="w-full sm:w-[60vw]">
					<BasicInformation form={form} />
				</TabsContent>

				<TabsContent value="parent_details" className="w-full sm:w-[60vw]">
					<ParentDetails form={form} />
				</TabsContent>

				<TabsContent value="additional_details">
					<p>Additional Details</p>
				</TabsContent>
				<div className="flex justify-end w-full sm:w-[10-vw]">
					{!(stepTabs.findIndex((step) => step.key === currentStep) === 0) && <Button
						variant="ghost"
						onClick={handlePrev}
					>
						Prev
					</Button>
					}
					{!(stepTabs.findIndex((step) => step.key === currentStep) === stepTabs.length - 1) && <Button
						variant="ghost"
						onClick={handleNext}
					>
						Next
					</Button>}
				</div>
			</Tabs>
		</div>
	)
}

export function BasicInformation({ form }: { form: UseFormReturn<any> }) {

	const currentSchool = localStorage.getItem("active_school");

	const school: LocalStorageSchool = JSON.parse(currentSchool ? currentSchool : "");

	const gradesQuery = useQuery({
		queryKey: ["grades"],
		queryFn: async (): Promise<Grade[]> => {
			const response = await api.get(`schools/${school?.school_id}/grades/`)
			return response.data
		}
	});

	const [dateOfBirthOpen, setDateOfBirthOpen] = useState(false)
	const [dateOfBirth, setDateOfBirth] = useState<Date | undefined>(undefined)

	const selectedGrade = form.watch("grade");

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
									<FieldLabel htmlFor="last-name">Last Name</FieldLabel>
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

						<div className="flex flex-row gap-2 sm:gap-4 flex-1">
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
							{(gradesQuery.data
								?.find((grade) => grade.id.toString() === selectedGrade)
								?.streams?.length ?? 0) > 0 &&
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
														{
															gradesQuery.data?.find((grade) => grade.id.toString() === selectedGrade)?.streams?.map((stream, index) =>
																<SelectItem key={index} value={stream.id.toString()}>{stream.name}</SelectItem>
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
							}
						</div>
						<Controller
							name="gender"
							control={form.control}
							render={({ field, fieldState }) => (
								<Field data-invalid={fieldState.invalid} className="flex-1">
									<FieldLabel htmlFor="gender">Gender</FieldLabel>
									<Select
										name={field.name}
										value={field.value}
										onValueChange={field.onChange}
									>
										<SelectTrigger
											id="gender"
											aria-invalid={fieldState.invalid}
										>
											<SelectValue placeholder="Select gender" />
										</SelectTrigger>
										<SelectContent>
											<SelectGroup>
												<SelectItem value="m">Male</SelectItem>
												<SelectItem value="f">Female</SelectItem>
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

					<div className="flex flex-row gap-2 sm:gap-4">
						<Controller
							name="date_of_birth"
							control={form.control}
							render={({ field, fieldState }) => (
								<Field data-invalid={fieldState.invalid}>
									<FieldLabel htmlFor="date_of_birth">Date of Birth</FieldLabel>
									<Popover open={dateOfBirthOpen} onOpenChange={setDateOfBirthOpen}>
										<PopoverTrigger asChild>
											<Button
												variant="outline"
												id="date"
												className="justify-start font-normal"
											>
												{dateOfBirth ? dateOfBirth.toLocaleDateString() : "Select date"}
											</Button>
										</PopoverTrigger>
										<PopoverContent className="overflow-hidden p-0" align="start">
											<Calendar
												mode="single"
												className="w-full"
												selected={dateOfBirth}
												defaultMonth={dateOfBirth}
												captionLayout="dropdown"
												disabled={(date) => {
													return date >= new Date()
												}}
												onSelect={(date) => {
													setDateOfBirth(date)
													setDateOfBirthOpen(false)
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
							name="transfered_from"
							control={form.control}
							render={({ field, fieldState }) => (
								<Field data-invalid={fieldState.invalid}>
									<FieldLabel htmlFor="transfered-from">Transfered From</FieldLabel>
									<Input
										{...field}
										id="transfered-from"
										type="text"
									/>
									{fieldState.invalid && (
										<FieldError errors={[fieldState.error]} />
									)}
								</Field>
							)}
						/>
					</div>
				</FieldGroup >

				<div className="flex justify-between">
				</div>
			</div>
		</form>
	)
}

export function ParentDetails({ form }: { form: UseFormReturn<any> }) {

	return (
		<form>
			<div className="flex flex-col gap-4">
				<FieldGroup >
					<div className="flex flex-row gap-2 sm:gap-4">
						<Controller
							name="parent_first_name"
							control={form.control}
							render={({ field, fieldState }) => (
								<Field data-invalid={fieldState.invalid}>
									<FieldLabel htmlFor="parent-first-name">Parent First Name</FieldLabel>
									<Input
										{...field}
										id="parent-first-name"
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
							name="parent_last_name"
							control={form.control}
							render={({ field, fieldState }) => (
								<Field data-invalid={fieldState.invalid}>
									<FieldLabel htmlFor="parent-last-name">Parent Last Name</FieldLabel>
									<Input
										{...field}
										id="parent-last-name"
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
						<Controller
							name="parent_email"
							control={form.control}
							render={({ field, fieldState }) => (
								<Field data-invalid={fieldState.invalid}>
									<FieldLabel htmlFor="parent-email">Parent Email</FieldLabel>
									<Input
										{...field}
										id="parent-email"
										type="email"
										required
									/>
									{fieldState.invalid && (
										<FieldError errors={[fieldState.error]} />
									)}
								</Field>
							)}
						/>

						<Controller
							name="parent_phone_number"
							control={form.control}
							render={({ field, fieldState }) => (
								<Field data-invalid={fieldState.invalid}>
									<FieldLabel htmlFor="parent-phone-number">Parent Phone Number</FieldLabel>
									<Input
										{...field}
										id="parent-phone-number"
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
				</FieldGroup >

				<div className="flex justify-between">
				</div>
			</div>
		</form>
	)
}

export function AdditionalDetails() {

	return (
		<div>Basic info</div>
	)
}
