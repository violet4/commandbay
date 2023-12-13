import { UserModel } from "@/models/User";
import { UserRow } from "./User";
import { requestConfirmation } from "@/utils";
import React from "react";

interface UsersTableProps {
    in_users: UserModel[];
}

export const UsersTable: React.FC<UsersTableProps> = ({ in_users }) => {
    const [users, setUsers] = React.useState(in_users);
    const deleteUser = (user_id: Number) => requestConfirmation(() => {
        fetch(`/api/users/${user_id}`, {method: "DELETE"})
            .then(resp => {
                if (!resp.ok)
                    throw new Error("Failed to delete user");
            })
            .then(() => {
                setUsers(users.filter(user => user.user_id !== user_id));
            });
    });
    if (users === undefined) {
        return (
            <div>No Users</div>
        );
    }
    return (
        <table>
            <thead>
                <tr>
                    <th>Actions</th>
                    {/* <th>ID</th> */}
                    <th>Name</th>
                    <th>TTS<br/>Included</th>
                    <th>TTS<br/>Nickname</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {users.map(user => (
                    <UserRow key={user.user_id} user={user} deleteUser={deleteUser(user.user_id)} />
                ))}
            </tbody>
        </table>
    );
};
