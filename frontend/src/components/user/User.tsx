import React from "react";
import { UserModel } from "@/models/User";
import { useSaveCancelKeys } from "@/utils";

interface UserRowProps {
    user: UserModel;
    onSave: (user: UserModel) => void;
    onCancel: (id: number) => void;
}

export const UserRow: React.FC<UserRowProps> = ({ user, onSave, onCancel }) => {
    const [editName, setEditName] = React.useState(user.name);
    const [savedName, setSavedName] = React.useState(user.name);

    const saveAction = () => {
        onSave({...user, name: editName});
        setSavedName(editName);
    };
    const cancelAction = () => {
        onCancel(user.user_id);
        setEditName(savedName);
    };

    const saveCancelKeyHandlers = useSaveCancelKeys({ onEnter: saveAction, onEscape: cancelAction });

    return (
        <tr>
            <td>{user.user_id}</td>
            <td>
                <input
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    {...saveCancelKeyHandlers}
                />
            </td>
            {editName!==savedName &&
                <td>
                    <button onClick={saveAction}>Save</button>
                    <button onClick={cancelAction}>Cancel</button>
                </td>
            }
        </tr>
    );
};
