"use client"

import { useQuery } from "@tanstack/react-query";
import { Student } from "@/types";
import api from "@/lib/api";
import { ColumnDef } from "@tanstack/react-table";
import { Checkbox } from "@/components/ui/checkbox";
import { DataTable } from "@/components/data-table";

// TODO: Define columns here
//
//
//TODO: We only need to pass columns and data, we already have the data
//
//

const columns: ColumnDef<Student>[] = [
	{
		id: "select",
		header: ({ table }) => (
			<Checkbox
				checked={
					table.getIsAllPageRowsSelected() ||
					(table.getIsSomePageRowsSelected() && "indeterminate")
				}
				onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
				aria-label="Select all"
			/>
		),
		cell: ({ row }) => (
			<Checkbox
				checked={row.getIsSelected()}
				onCheckedChange={(value) => row.toggleSelected(!!value)}
				aria-label="Select row"
			/>
		),
		enableSorting: false,
		enableHiding: false,
	},
	{
		accessorKey: "student_name",
		header: "Student",
		enableHiding: false,
		cell: ({ row }) => <div className="font-medium">{row.getValue("student_name")}</div>,
	},
	{
		accessorKey: "admission_number",
		header: "ADM",
		cell: ({ row }) => <div className="font-medium">{row.getValue("admission_number")}</div>,
	},
	{
		accessorKey: "assessment_number",
		header: "Assessment No.",
		cell: ({ row }) => <div className="font-medium">{row.getValue("assessment_number")}</div>,
	},
	{
		id: "grade_stream",
		header: "Grade",
		cell: ({ row }) => {

			const { grade_name, stream_name } = row.original;

			return (
				<div className="flex flex-col leading-tight">
					<span className="">{grade_name ?? "-"}</span>
					{stream_name && (
						<span className="text-xs text-gray-500">{stream_name}</span>
					)}
				</div>
			)
		}
	},
	{
		accessorKey: "enrollment_status",
		header: "Status",
		cell: ({ row }) => <div className="font-medium">{row.getValue("enrollment_status")}</div>,
	},
]

export function StudentsTable() {

	const currentSchool = localStorage.getItem("active_school");

	const school: { school_id: string, school_name: string } = JSON.parse(currentSchool ? currentSchool : "");

	const { data: students, isLoading, error } = useQuery({
		queryKey: ["students"],
		queryFn: async (): Promise<Student[]> => {
			const response = await api.get(`/schools/${school.school_id}/students/`)
			return response.data
		},
	})

	return (
		<div>
			{isLoading && <p>Loading ...</p>}
			{error && <p>Error{error.message}</p>}
			{students && <DataTable columns={columns} data={students} />}
		</div>

	);
}
