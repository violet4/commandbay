import React from "react";
import { UserModel } from "@/models/User";
import { useKeyPressHandlers, json_headers, buttonClasses } from "@/utils";

interface UserRowProps {
    user: UserModel;
    deleteUser: () => void;
}

type UpdatableFields = 'tts_nickname' | 'tts_included';

function isUpdatableField(field: any): field is UpdatableFields {
    return field === 'tts_nickname' || field === 'tts_included';
}

export const UserRow: React.FC<UserRowProps> = ({ user, deleteUser }) => {
    const [modifiedUserData, setModifiedUserData] = React.useState(user);
    const [savedUserData, setSavedUserData] = React.useState(user);

    const onSave = (field: UpdatableFields) => () => {
        if (!isUpdatableField(field)) return;

        const new_data: Partial<UserModel> = {};
        const stateUpdater = (data2: UserModel) => () => {
            const updateObj: Partial<UserModel> = {};
            updateObj[field] = data2[field] as any;
            return {...modifiedUserData, ...updateObj};
        };

        new_data[field] = modifiedUserData[field] as any;

        fetch(`/api/users/${savedUserData.user_id}`, {method: "PUT", headers: json_headers, body: JSON.stringify(new_data)})
            .then(response => response.json())
            .then((data: UserModel) => {
                setSavedUserData(stateUpdater(data));
                setModifiedUserData(stateUpdater(data));
            });
    };

    const onCancel = (field: UpdatableFields) => () => {
        if (!isUpdatableField(field)) return;

        const resetObj: Partial<UserModel> = {};
        resetObj[field] = savedUserData[field] as any;
        setModifiedUserData({...modifiedUserData, ...resetObj});
    };
    const saveNameChange = onSave("tts_nickname");
    const cancelNameChange = onCancel('tts_nickname');
    const keyPressHandlers = useKeyPressHandlers({ Escape: cancelNameChange, Enter: saveNameChange });

    return (
        <tr>
            <td><button className="indigo-button" onClick={deleteUser}>Delete</button></td>
            {/* <td>{user.user_id}</td> */}
            <td>{user.name}</td>
            <td>
                {/* tts included */}
                <input type="checkbox" checked={savedUserData.tts_included} onChange={(e) => {
                    e.target.disabled = true;
                    fetch(`/api/users/${savedUserData.user_id}`, {method: "PUT", headers: json_headers, body: JSON.stringify({tts_included: e.target.checked})})
                    .then(response => response.json())
                    .then((data: UserModel) => {
                        setSavedUserData(() => ({...savedUserData, tts_included: data.tts_included}));
                        setModifiedUserData(() => ({...modifiedUserData, tts_included: data.tts_included}));
                        e.target.disabled = false;
                    });
                }}/>
            </td>
            <td>
                {/* nickname */}
                <input
                    value={modifiedUserData.tts_nickname||''}
                    onChange={(e) => setModifiedUserData(() => ({...modifiedUserData, tts_nickname: e.target.value}))}
                    {...keyPressHandlers}
                />
                {modifiedUserData.tts_nickname!==savedUserData.tts_nickname &&
                    <>
                        <button className="indigo-button" onClick={saveNameChange}>Save</button>
                        <button className="indigo-button" onClick={cancelNameChange}>Cancel</button>
                    </>
                }
            </td>
        </tr>
    );
};
