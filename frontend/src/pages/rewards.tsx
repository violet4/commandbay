import React, { useCallback } from "react";
import useSWR from "swr";

import { createKeyPressHandlers, json_headers } from "@/utils";
import { RewardModel } from "@/models/Reward";

const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function Rewards() {
    const {data: rewards, error} = useSWR('/api/rewards', fetcher);

    if (error) return <div>Failed to load rewards</div>;
    if (!rewards) return <div>Loading...</div>;
    return <RewardsTable rewards={rewards} />;

}
 
interface RewardsTableProps {
    rewards: RewardModel[];
}

export const RewardsTable: React.FC<RewardsTableProps> = ({ rewards }) => {
    if (rewards === undefined) {
        return (
            <div>No rewards</div>
        );
    }
    return (
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>TTS<br/>Nickname</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {rewards.map(reward => (
                    <RewardRow key={reward.reward_id} reward={reward} />
                ))}
            </tbody>
        </table>
    );
};

interface RewardRowProps {
    reward: RewardModel;
}

type UpdatableFields = 'tts_name' | 'tts_included';

function isUpdatableField(field: any): field is UpdatableFields {
    return field === 'tts_name' || field === 'tts_included';
}

export const RewardRow: React.FC<RewardRowProps> = ({ reward }) => {
    const [modifiedRewardData, setModifiedRewardData] = React.useState(reward);
    const [savedRewardData, setSavedRewardData] = React.useState(reward);

    const onSave = (field: UpdatableFields) => () => {
        if (!isUpdatableField(field)) return;

        const new_data: Partial<RewardModel> = {};
        const stateUpdater = (data2: RewardModel) => () => {
            const updateObj: Partial<RewardModel> = {};
            updateObj[field] = data2[field] as any;
            return {...modifiedRewardData, ...updateObj};
        };

        new_data[field] = modifiedRewardData[field] as any;

        fetch(`/api/rewards/${savedRewardData.reward_id}`, {method: "PUT", headers: json_headers, body: JSON.stringify(new_data)})
            .then(response => response.json())
            .then((data: RewardModel) => {
                setSavedRewardData(stateUpdater(data));
                setModifiedRewardData(stateUpdater(data));
            });
    };

    const onCancel = (field: UpdatableFields) => () => {
        if (!isUpdatableField(field)) return;

        const resetObj: Partial<RewardModel> = {};
        resetObj[field] = savedRewardData[field] as any;
        setModifiedRewardData({...modifiedRewardData, ...resetObj});
    };
    const saveNameChange = onSave("tts_name");
    const cancelNameChange = onCancel('tts_name');

    return (
        <tr>
            <td>{reward.reward_id}</td>
            <td>{reward.name}</td>
            <td>
                {/* nickname */}
                <input
                    value={modifiedRewardData?.tts_name||''}
                    onChange={(e) => setModifiedRewardData(() => ({...modifiedRewardData, tts_name: e.target.value}))}
                    {...createKeyPressHandlers({Escape: cancelNameChange, Enter: saveNameChange})}
                />
                {modifiedRewardData.tts_name!==savedRewardData.tts_name &&
                    <>
                        <button onClick={saveNameChange}>Save</button>
                        <button onClick={cancelNameChange}>Cancel</button>
                    </>
                }
            </td>
        </tr>
    );
};
