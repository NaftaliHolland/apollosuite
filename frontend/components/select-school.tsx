"use client"

import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useState } from "react";
import { Check, LoaderCircle } from "lucide-react";
import { useRouter } from "next/navigation";

export default function SelectSchool() {

	const { data: user, isLoading } = useCurrentUser();

	const [selected, setSelected] = useState<{ school_id: string, school_name: string } | null>(null);

	const router = useRouter();

	function handleSelect(school: { school_id: string, school_name: string }) {
		setSelected(school === selected ? null : school);
		localStorage.setItem("active_school", JSON.stringify(school))

		router.replace("/dashboard");
	}

	return (
		<div className="flex flex-col items-center gap-1 text-center">
			<h1 className="text-2xl font-bold">Select School</h1>
			<p className="text-sm text-balance text-muted-foreground">
				You are in multiple schools, select the school you want to log in to
			</p>

			<div className="w-full mt-4">
				{isLoading &&
					<div className="flex justify-center w-full">
						<LoaderCircle className="animate-spin text-primary" />
					</div>
				}
				<ul className="flex flex-col gap-1 w-full">
					{user?.schools?.map((school) => {
						const active = selected === school;
						return (
							<li key={school.school_id}>
								<button
									onClick={() => handleSelect(school)}
									className={`w-full flex items-center justify-between px-3 py-2.5 border rounded-md text-sm transition-colors ${active
										? "bg-primary text-white"
										: "text-zinc-700 hover:bg-zinc-100"
										}`}
								>
									<span className="font-medium">{school.school_name}</span>
									{active && <Check className="w-4 h-4 opacity-80" strokeWidth={2.5} />
									}
								</button>
							</li>
						);
					})}
				</ul>
			</div>
		</div>
	)
}
