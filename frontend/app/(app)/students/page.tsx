import { SiteHeader } from "@/components/site-header";
import { StudentsTable } from "./students-table";

export default function() {
	return (
		<>
			<SiteHeader header={"Students"} />
			<div className="flex flex-1 flex-col gap-4 p-4">
				<StudentsTable />
			</div>
		</>
	)
}
