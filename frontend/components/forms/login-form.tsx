"use client"

import * as z from "zod";

import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { Controller, useForm } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { LoaderCircle, EyeIcon, EyeOffIcon } from "lucide-react";
import { Field, FieldLabel, FieldGroup, FieldSeparator, FieldError, FieldDescription } from "@/components/ui/field";
import { useAuth } from "@/context/AuthProvider";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/components/ui/input-group";

const formSchema = z.object({
	phone_number: z
		.string()
		.min(10, "Phone number must be exactly at least 10 numbers"),
	password: z
		.string()
		.min(5, "Password has to be at least 5 characters long")
		.max(50, "Password cannot be more then 50 characters long")
})

export default function LoginForm() {
	const form = useForm<z.infer<typeof formSchema>>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			phone_number: "",
			password: "",
		},
	})

	const [passwordVisible, setPasswordVisible] = useState<boolean>(false);

	const router = useRouter();

	const { login } = useAuth();

	const loginMutation = useMutation(
		{
			mutationFn: ({ phone_number, password }: { phone_number: string, password: string }) =>
				login(phone_number, password),
			onSuccess: (data: any) => {
				toast.success("Login successfull");
				form.reset()

				const roles: string[] = data.roles;
				if (roles.length > 1) {
					router.replace("/select-role");
				} else {
					router.replace("/dashboard");
				}
			},
			onError: (error: any) => {
				toast.error(error.response?.data?.detail);
			}
		}
	)

	function onSubmit(data: z.infer<typeof formSchema>) {
		loginMutation.mutate(data);
	}

	return (
		<form onSubmit={form.handleSubmit(onSubmit)}>
			<div className="flex flex-col items-center gap-1 text-center">
				<h1 className="text-2xl font-bold">Login to your account</h1>
				<p className="text-sm text-balance text-muted-foreground">
					Enter your phone number below to login to your account
				</p>
			</div>
			<FieldGroup>
				<Controller
					name="phone_number"
					control={form.control}
					render={({ field, fieldState }) => (
						<Field data-invalid={fieldState.invalid}>
							<FieldLabel htmlFor="phone_number">Phone Number</FieldLabel>
							<Input
								{...field}
								id="phone_number"
								type="text"
								placeholder="254 7111111"
								required />

							{fieldState.invalid && (
								<FieldError errors={[fieldState.error]} />
							)}
						</Field>
					)}
				/>

				<Controller
					name="password"
					control={form.control}
					render={({ field, fieldState }) => (
						<Field data-invalid={fieldState.invalid}>
							<div className="flex items-center">
								<FieldLabel htmlFor="password">Password</FieldLabel>
								<a
									href="#"
									className="ml-auto text-sm underline-offset-4 hover:underline"
								>
									Forgot your password?
								</a>
							</div>

							<InputGroup>
								<InputGroupInput
									{...field}
									id="password"
									type={passwordVisible ? "text" : "password"}
									required
								/>
								<InputGroupAddon align="inline-end">
									<Button
										onClick={(e) => {
											e.preventDefault()
											setPasswordVisible(!passwordVisible)
										}
										}
										variant="ghost"
										className="h-6 w-6"
									>
										{
											passwordVisible
												? <EyeOffIcon size={16} />
												: <EyeIcon size={16} />
										}
									</Button>

								</InputGroupAddon>
							</InputGroup>

							{fieldState.invalid && (
								<FieldError errors={[fieldState.error]} />
							)}
						</Field>
					)}
				/>

				<Field>
					<Button type="submit" disabled={loginMutation.isPending}>
						{loginMutation.isPending
							? <LoaderCircle className="animate-spin" />
							: "Login"
						}
					</Button>
				</Field>
				<Field>
					<FieldDescription className="text-center">
						Don&apos;t have an account?{" "}
						<a href="/signup" className="underline underline-offset-4">
							Sign up
						</a>
					</FieldDescription>
				</Field>
			</FieldGroup>
		</form>
	)
}
