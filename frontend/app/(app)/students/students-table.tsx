"use client"

import { useQuery } from "@tanstack/react-query";
import { Student } from "@/types";
import api from "@/lib/api";

export function StudentsTable() {

	const currentSchool = localStorage.getItem("active_school");

	const school: { school_id: string, school_name: string } = JSON.parse(currentSchool ? currentSchool : "");

	const { data: students, isLoading, error } = useQuery({
		queryKey: ["students"],
		queryFn: (): Promise<Student[]> => api.get(`/schools/${school.school_id}/students/`),
	})

	return (
		<p>Students table</p>
	);
}
