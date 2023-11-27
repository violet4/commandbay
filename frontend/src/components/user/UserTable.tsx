import { User } from "../../models/User";
import { UserRow } from "./User";

interface UsersTableProps {
    users: User[];
    onSave: (user: User) => void;
    onCancel: (id: number) => void;
}

export const UsersTable: React.FC<UsersTableProps> = ({ users, onSave, onCancel }) => {
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
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {users.map(user => (
                    <UserRow key={user.user_id} user={user} onSave={onSave} onCancel={onCancel} />
                ))}
            </tbody>
        </table>
    );
};
