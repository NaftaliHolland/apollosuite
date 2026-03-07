export type User = {
	id: string | number;
	first_name: string;
	last_name: string;
	email?: string;
	phone_number: string;
	status: string;
	active_role: string;
	roles: string[];
}

export type Student = {
	user_id: string,
	student_name: string,
	admission_number: string,
	assessment_number?: string,
	grade_name?: string,
	stream_name?: string,
	enrollment_status: string,
}

export type StudentDetail = {
}
