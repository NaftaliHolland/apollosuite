import { ComponentExample } from "@/components/component-example";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Page() {
	return (
		<div className="w-full h-full">
			<div className="flex items-center justify-center">
				<Button asChild>
					<Link href="/dashboard">Dashboard</Link>
				</Button>
			</div>

		</div>
	);
}
