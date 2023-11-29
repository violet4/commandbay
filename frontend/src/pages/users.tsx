import { UsersTable } from "@/components/user/UserTable";
import { AppState } from "@/models/AppState";
import { UserModel } from "@/models/User";
import { useEffect, useState } from "react";
import useSWR from "swr";

const json_headers = {'Content-Type': 'application/json'};

const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function Users() {
    const {data: users, error} = useSWR('/api/users', fetcher);
    const [state, setState] = useState<AppState>({ users: [], error: null });

    const handleSave = (updatedUser: UserModel) => {
        fetch(`/api/users/${updatedUser.user_id}`, {method: "PUT", headers: json_headers, body: JSON.stringify({name: updatedUser.name})})
            .then(response => response.json())
            .then(() => setState(prevState => {
                const updatedUsers = prevState.users.map(user =>
                    user.user_id===updatedUser.user_id ? {...user, name: updatedUser.name} : user
                );
                return { ...prevState, users: updatedUsers};
            }))
    };

    const handleCancel = (id: number) => {
        // Restore original name
        const updatedUsers = state.users.map((user: UserModel) =>
            user.user_id === id ? { ...user, name: user.originalName } : user
        );
        setState({...state, users: updatedUsers});
    };

    if (error) return <div>Failed to load users</div>;
    if (!users) return <div>Loading...</div>;
    return <UsersTable users={users} onSave={handleSave} onCancel={handleCancel} />;

}




// useEffect(() => {
//     fetch("/api/users")
//         .then(response => response.json())
//         .then(data => setState({...state, users: data}))
//         .catch(error => setState({...state, error: error.toString()}));
// }, []);

