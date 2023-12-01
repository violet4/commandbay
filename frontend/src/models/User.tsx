
export interface UserModel {
    user_id: number;
    name: string;
    originalName: string;
    platform: string;
    platform_user_id?: string;
    tts_included: boolean;
    tts_nickname?: string;
}
