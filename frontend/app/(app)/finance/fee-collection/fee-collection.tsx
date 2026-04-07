"use client"

import { useQuery } from "@tanstack/react-query";
import { useState, useMemo } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Student, LocalStorageSchool } from "@/types";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";
import {
	InputGroup,
	InputGroupAddon,
	InputGroupInput,
} from "@/components/ui/input-group"
import { LoaderCircle, Search, X } from "lucide-react"

// TODO: Get all students
// Implement search
// Fetch individual student
//
//
// TODO: fee later


export function FeeCollection() {


	const currentSchool = localStorage.getItem("active_school");

	const school: LocalStorageSchool = JSON.parse(currentSchool ? currentSchool : "");

	const studentsQuery = useQuery({
		queryKey: ["students"],
		queryFn: async (): Promise<Partial<Student>[]> => {
			const response = await api.get(`/schools/${school.school_id}/students?type=summary`)

			return response.data;
		}
	});

	const [query, setQuery] = useState("");
	const [selectedStudent, setSelectedStudent] = useState<Partial<Student> | undefined>(undefined);

	//const studentQuery = useQuery({
	//	queryKey: ["students", selectedStudent?.user_id],
	//	queryFn: async (): Promise<Partial<Student>> => {
	//		const response = await api.get(`/schools/${school.school_id}/students/${selectedStudent?.user_id}/`)

	//		return response.data;
	//	},
	//	enabled: !!selectedStudent,
	//});

	const studentFeeSummaryQuery = useQuery({
		queryKey: ["students", selectedStudent?.user_id],
		// Write this type
		queryFn: async (): Promise<any> => {
			const response = await api.get(`/schools/${school.school_id}/students/${selectedStudent?.user_id}/fee-summary/`)

			return response.data;
		},
		enabled: !!selectedStudent,
	});


	const filtered = useMemo(() => {
		const q = query.trim().toLowerCase();
		//if (!studentsQuery.data) return;
		if (!q) return studentsQuery.data;
		return studentsQuery.data?.filter(
			(s) =>
				s.student_name?.toLowerCase().includes(q) ||
				s.admission_number?.toLowerCase().includes(q) ||
				(s.assessment_number ?? "").toLowerCase().includes(q)
		);
	}, [query]);


	return (
		<div>
			<h2 className="text-2xl font-semibold  tracking-tight">Fee Collection</h2>

			<div className="border rounded-md p-4 mt-4 space-y-4">
				<div className="space-y-2">
					<InputGroup className=" py-4">
						<InputGroupInput
							placeholder="Search by name, admisison number or assessment number ..."
							value={query}
							onChange={(e) => setQuery(e.target.value)}
						/>
						<InputGroupAddon>
							<Search />
						</InputGroupAddon>
						<InputGroupAddon align="inline-end">{filtered?.length} Students</InputGroupAddon>
						{query && (
							<InputGroupAddon align="inline-end">
								<Button
									variant="ghost"
									size="icon"
									onClick={() => setQuery("")}
								>
									<X className="h-4 w-4" />
								</Button>
							</InputGroupAddon>
						)}
					</InputGroup>
					{query &&
						<ScrollArea className="max-h-80 rounded-md border">
							{filtered?.length === 0 && (
								<div className="py-12 text-center text-muted-foreground">
									<Search className="h-8 w-8 mx-auto mb-3 opacity-30" />
									<p className="font-medium">No results for &ldquo;{query}&rdquo;</p>
									<p className="text-sm mt-1">Try a different name, admission number, or assessment number.</p>
								</div>
							)}
							<div className="flex flex-col">
								{filtered?.map((student, index) => (
									<Button
										key={student.user_id}
										variant="ghost"
										className={`w-full justify-between rounded-none h-auto py-2.5 px-4 hover:bg-accent ${index !== filtered.length - 1 ? "border-b" : ""
											}`}
										onClick={() => {
											setQuery("");
											setSelectedStudent(student);
										}
										}
									>
										<div className="flex flex-col items-start gap-0.5">
											<span className="text-sm font-medium leading-tight">
												{student.student_name}
											</span>
											<span className="text-xs text-muted-foreground font-mono leading-tight">
												{student.admission_number}
											</span>
										</div>

										<Badge variant="secondary" className="text-xs shrink-0 ml-2">
											{student.grade_name}
										</Badge>
									</Button>
								))}
							</div>
						</ScrollArea>
					}
				</div>

				{studentFeeSummaryQuery.isLoading &&
					<LoaderCircle className="animate-spin mx-auto" />
				}
				{studentFeeSummaryQuery.error &&
					<p className="text-red-500">{studentFeeSummaryQuery.error.message}</p>
				}
				{studentFeeSummaryQuery.data &&
					<div className="flex justify-between">
						<div>
							<div className="flex items-center gap-5 mb-1">
								<h3 className="text-xl font-semibold text-slate-800">{studentFeeSummaryQuery.data.student.student_name}</h3>
								<Badge variant="outline" className="rounded-sm">{studentFeeSummaryQuery.data.student.grade}{studentFeeSummaryQuery.data.student.stream ? `-${studentFeeSummaryQuery.data.student.stream}` : ""}</Badge>
							</div>
							<p className="text-slate-500 font-medium">Student ID: <span className="font-normal">#{studentFeeSummaryQuery.data.student.admission_number}</span></p>
							{studentFeeSummaryQuery.data.student.assessment_number && <p className="text-slate-500 font-medium">Assessment No: <span className="font-normal">#{studentFeeSummaryQuery.data.student.assessment_number}</span></p>}
						</div>

						<div className="bg-primary  rounded-sm px-8 py-4 flex flex-col items-center justify-center relative z-10 min-w-[200px] shadow-lg shadow-primary/20">
							<p className="text-xs font-bold uppercase tracking-widest opacity-80 mb-1">Outstanding Balance</p>
							<p className="text-4xl font-extrabold tracking-tighter"><span className="text-xl">KSHS:</span> {Intl.NumberFormat("en", { minimumFractionDigits: 2 }).format(studentFeeSummaryQuery.data.summary.total_fees_due)}</p>
						</div>

					</div>
				}
			</div>
		</div>
	)
}
