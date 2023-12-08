import { UserModel } from "@/models/User";
import { UserRow } from "./User";

interface UsersTableProps {
    users: UserModel[];
}

export const UsersTable: React.FC<UsersTableProps> = ({ users }) => {
    if (users === undefined) {
        return (
            <div>No Users</div>
        );
    }
    return (
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>TTS<br/>Included</th>
                    <th>TTS<br/>Nickname</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {users.map(user => (
                    <UserRow key={user.user_id} user={user} />
                ))}
            </tbody>
        </table>
    );
};
