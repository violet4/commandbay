import { UsersTable } from "@/components/user/UserTable";
import useSWR from "swr";

const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function Users() {
    const {data: users, error} = useSWR('/api/users', fetcher);

    if (error) return <div>Failed to load users</div>;
    if (!users) return <div>Loading...</div>;
    return <UsersTable in_users={users} />;
}
