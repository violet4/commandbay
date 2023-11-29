import { UserModel } from "./User";

export interface AppState {
    users: UserModel[];
    error: string | null;
}
