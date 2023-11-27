import { User } from "./User";

export interface AppState {
    users: User[];
    error: string | null;
}
