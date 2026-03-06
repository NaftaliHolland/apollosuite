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
