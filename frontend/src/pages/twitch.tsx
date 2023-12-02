
export default function Twitch() {
    const streamer = 'violet_revenant';
    return (
        <div>
            <h1>Twitch</h1>
            <ul>
                <li><a href={`https://dashboard.twitch.tv/u/${streamer}/stream-manager`}>Stream Manager</a></li>
                <li><a href={`https://dashboard.twitch.tv/u/${streamer}/stream-manager`}>Stream Page</a></li>
                <li><a href={`https://dashboard.twitch.tv/u/${streamer}/stream-manager`}>Stream Chat</a></li>
            </ul>
        </div>
    );

}
