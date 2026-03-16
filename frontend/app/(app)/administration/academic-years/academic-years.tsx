"use client"

import api from "@/lib/api";
import { useQuery, useMutation } from "@tanstack/react-query";
import { AcademicYear, LocalStorageSchool } from "@/types";
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog"
import { AcademicYearForm } from "@/components/forms/academic-year-form";


export function AcademicYears() {

	// TODO: make this a helper function or someting, I can't be doing this erverywhere meehn
	//
	const currentSchool = localStorage.getItem("active_school");

	const school: LocalStorageSchool = JSON.parse(currentSchool ? currentSchool : "");

	const { data: academicYears, isLoading, error } = useQuery({
		queryKey: ["academicYears"],
		queryFn: async (): Promise<AcademicYear[]> => {
			const response = await api.get(`/schools/${school.school_id}/academic-years/`)

			return response.data;
		}
	})

	const [addYearOpen, setAddYearOpen] = useState(false);

	const [selectedYear, setSelectedYear] = useState<AcademicYear | undefined>(academicYears?.find(year => year.is_active === true))

	return (
		<div className="py-4 px-8">
			{isLoading && <p>Loading ...</p>}
			{error && <p>Error{error.message}</p>}
			{academicYears && (
				<>
					<div className="flex justify-between w-full mb-8">
						<p className="font-semibold text-lg">Academic Years</p>
					</div>
					<div className="max-w-7xl mx-auto">
						<div className="grid grid-cols-1 md:grid-cols-4 gap-6">

							<div className="md:col-span-1 space-y-4">
								<Dialog open={addYearOpen} onOpenChange={setAddYearOpen}>
									<DialogTrigger asChild>
										<Button
											className="w-full h-12"
										>
											Add Academic Year
										</Button>
									</DialogTrigger>
									<DialogContent>
										<DialogHeader>
											<DialogTitle>Add new Academic Year</DialogTitle>
											<DialogDescription className="sr-only">
												Add a new academic year
											</DialogDescription>
										</DialogHeader>
										<AcademicYearForm handleClose={() => setAddYearOpen(false)} />
									</DialogContent>
								</Dialog>

								{academicYears.map((academicYear) =>
									<button
										key={academicYear.id}
										className={`w-full text-left py-2 p-3 rounded-lg transition-all ${selectedYear?.id === academicYear.id
											? "bg-blue-100 dark:bg-blue-900 border border-blue-400 dark:border-blue-600"
											: "hover:bg-gray-50 dark:hover:bg-gray-800 border border-transparent"
											}`}
									>
										<div className="flex items-center justify-between mb-1">
											<span className="font-semibold">{academicYear.name}</span>
											{academicYear.is_active && (
												<div className="w-2 h-2 rounded-full bg-green-500" />
											)}
										</div>
										<p className="text-xs text-gray-600 dark:text-gray-400">
											{academicYear.start_date}
										</p>
									</button>
								)
								}
							</div>

							{/* TODO: Have a query that gets detaild info about that academic year, actually useful details*/}
							<div className="md:col-span-3 bg-gray-300 p-4">
								{selectedYear && (
									<div>
									</div>

								)
								}
							</div>

						</div>
					</div>
				</>
			)}
		</div>
	)
}
