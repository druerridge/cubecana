import { io } from "socketio";

export function generateDraftmancerSession(CubeFile, tabToOpen) {
    
    const Domain = "https://draftmancer.com";

    // Generate unique user ID and session ID
    const BotID = "CubecanaBot_" + crypto.randomUUID();
    const SessionID = "Cubecana_" + crypto.randomUUID();

    const query = {
        userID: BotID,
        userName: "Cubecana Bot",
        sessionSettings: JSON.stringify({bots: 7, maxTimer: 0}),
        sessionID: SessionID,
    };

    const socket = io(Domain, {
        query,
        transports: ["websocket"], // This is necessary to bypass CORS
    });

    // One of the message received by the client immediately on connection will
    // give you the current session owner. If the session was just created,
    // it should be our bot.
    socket.once("sessionOwner", (ownerID) => {
        if (ownerID !== BotID) {
            console.error("Not the owner!");
            socket.disconnect();
            return;
        }

        socket.emit("parseCustomCardList", CubeFile, (res) => {
            if (res.code < 0) {
                socket.disconnect();
                console.error(res);
            } else {
                // Automatically disconnect once the user has joined the session
                socket.once("sessionUsers", () => {
                    socket.disconnect();
                });
                // Open Draftmancer in specified tab
                tabToOpen.location.href = `${Domain}/?session=${SessionID}`;
            }
        });
    });
}