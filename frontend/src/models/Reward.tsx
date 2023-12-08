
export interface RewardModel {
    reward_id: number;
    name: string;
    platform: string;
    platform_reward_id?: string;
    tts_name?: string;
    tts_included: boolean;
}
