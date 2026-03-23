"use client"

import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { useState } from "react";
import { LocalStorageSchool, Grade } from "@/types";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog"
import api from "@/lib/api";
import { Button } from "@/components/ui/button"
import { GradeForm } from "@/components/forms/grade-form";

export function Grades() {

	const currentSchool = localStorage.getItem("active_school");

	const school: LocalStorageSchool = JSON.parse(currentSchool ? currentSchool : "");

	const { data: grades, isLoading, error } = useQuery({
		queryKey: ["grades"],
		queryFn: async (): Promise<Grade[]> => {
			const response = await api.get(`/schools/${school.school_id}/grades/`)
			return response.data
		},
	});

	const [addGradeOpen, setAddGradeOpen] = useState(false);

	return (
		<>
			{isLoading && <p>Loading ...</p>}
			{error && <p>Error{error.message}</p>}
			{grades && (
				<div className="flex flex-col gap-4 w-full">
					<div className="flex justify-between w-full">
						<p className="font-semibold text-lg">Grades</p>
						<Dialog open={addGradeOpen} onOpenChange={setAddGradeOpen}>
							<DialogTrigger asChild>
								<Button
								>
									<Plus />
									Add Grade
								</Button>
							</DialogTrigger>
							<DialogContent>
								<DialogHeader>
									<DialogTitle>Add Grade</DialogTitle>
									<DialogDescription className="sr-only">
										Add grade
									</DialogDescription>
								</DialogHeader>
								<GradeForm handleClose={() => setAddGradeOpen(false)} />
							</DialogContent>
						</Dialog>
					</div>
					<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
						{grades.map((grade) => (
							<div key={grade.id} className="py-4 px-6 border border-foreground/9 rounded-lg">
								<div>
									<h3 className="font-semibold text-foreground">{grade.name}</h3>
									<p className="text-sm text-foreground/60 mt-2">{grade.description}</p>
								</div>
								{grade.streams.length > 0 && (
									<>
										<div className="margin-t-4">
											<p className="text-xs font-medium text-foreground/50 uppercase tracking-wide mb-2">
												Streams
											</p>
											<p className="text-sm text-foreground/70">
												{grade.streams.map((s) => s.name).join(', ')}
											</p>
										</div>
									</>
								)}
							</div>
						))}
					</div>
				</div>
			)}
		</>
	)
}
