"use client"

import { useQuery } from "@tanstack/react-query";
import { Student, LocalStorageSchool } from "@/types";
import api from "@/lib/api";

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

	return (
		<div>
			<p>Now this is what we are working on now, should be fun</p>
		</div>
	)
}
