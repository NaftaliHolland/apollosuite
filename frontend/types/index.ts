export type LocalStorageSchool = {
	school_id: string;
	school_name: string;
}

export type User = {
	id: string | number;
	first_name: string;
	last_name: string;
	email?: string;
	phone_number: string;
	status: string;
	active_role: string;
	roles: string[];
	schools?: LocalStorageSchool[];
}

export type Student = {
	user_id: string;
	student_name: string;
	admission_number: string;
	assessment_number?: string;
	grade_name?: string;
	stream_name?: string;
	enrollment_status: string;
}

export type StudentDetail = {
}


export type Stream = {
	id: number;
	name: string;
}

export type Grade = {
	id: number;
	name: string;
	description?: string;
	streams: Stream[];
}

export type GradeDetail = {
}

export type AcademicYear = {
	id: number;
	name: string;
	start_date: string;
	end_date: string;
	is_active: boolean;
}
