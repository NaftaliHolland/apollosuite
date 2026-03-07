// Write zod validation
// Create the form instance
// Create the form - will will have 3 here but taking the same form
//
//
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";

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


const form = useForm<z.infer<typeof formSchema>>({
	resolver: zodResolver(formSchema),
	defaultValues: {
		first_name: "",
		last_name: "",
		parent_first_name: "",
		parent_last_name: "",
		parent_email: "",
		parent_phone_number: "",
	}
})

function onSubmit(data: z.infer<typeof formSchema>) {
	console.log(data)
}

export function BasicInformation() {
	return (
		<div>Basic info</div>
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
