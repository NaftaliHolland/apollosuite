// Get context here
// When editing - we'll have a function in the context that sets the student details then - 
// actually we'll just call the form.setValues before navigating. Context is pretty cool
//
//
//I don't need context
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

export default function NewStudentPage() {
	return (
		<div className="p-4 flex flex-col gap-4">
			<h2 className="font-medium">Add New Student</h2>
			<Tabs defaultValue="basic_information">
				<TabsList variant="line" className="gap-12">
					<TabsTrigger value="basic_information">Basic Information</TabsTrigger>
					<TabsTrigger value="parent_details">Parent Details</TabsTrigger>
					<TabsTrigger value="additional_details">Additional Details</TabsTrigger>
				</TabsList>

				<TabsContent value="basic_information">
					<p>Basic information</p>
				</TabsContent>

				<TabsContent value="parent_details">
					<p>Parent Details</p>
				</TabsContent>

				<TabsContent value="additional_details">
					<p>Additional Details</p>
				</TabsContent>

			</Tabs>
		</div>
	)
}
