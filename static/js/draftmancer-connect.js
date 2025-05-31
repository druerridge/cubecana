import { io } from "socketio";

export const GAME_MODE = {
    DRAFT: "DRAFT",
    SEALED: "SEALED",
    SUPER_SEALED: "SUPER_SEALED",
}

export function generateDraftmancerSession(CubeFile, tabToOpen, metadata, gameMode = GAME_MODE.DRAFT) {
    
    const Domain = "https://draftmancer.com";

    // Generate unique user ID and session ID
    const BotID = "CubecanaBot_" + crypto.randomUUID();
    const SessionID = "Cubecana_" + crypto.randomUUID();
    const maxSupportedPlayers = Math.floor( metadata.cardCount / (metadata.boostersPerPlayer * metadata.cardsPerBooster) )
    const numBots = Math.min(maxSupportedPlayers - 1, 7) ;
    const query = {
        userID: BotID,
        userName: "Cubecana Bot",
        sessionSettings: JSON.stringify({bots: numBots, maxTimer: 0}),
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
            tabToOpen.close();
            socket.disconnect();
            return;
        }

        socket.emit("parseCustomCardList", CubeFile, (res) => {
            if (res.code < 0) {
                console.error(res);
                tabToOpen.close();
                socket.disconnect();
            } else {
                function startDraftOnCompletion(responseData) {
                    // Automatically disconnect bot once the human user has joined the session
                    socket.once("sessionUsers", () => {
                        if (gameMode == GAME_MODE.SUPER_SEALED) {
                            socket.emit("distributeSealed", 16, null, (res) => {
                                if (res.code < 0) {
                                    console.error(res);
                                } else {
                                    console.log("Draftmancer session started successfully.");
                                }
                                socket.disconnect();
                            });
                        } else if (gameMode == GAME_MODE.SEALED) {
                            socket.emit("distributeSealed", 6, null, (res) => {
                                if (res.code < 0) {
                                    console.error(res);
                                } else {
                                    console.log("Draftmancer session started successfully.");
                                }
                                socket.disconnect();
                            });
                        } else {
                            console.log("Draftmancer session started successfully.");
                            socket.disconnect();
                        }
                    });
                    // Open Draftmancer in specified tab
                    tabToOpen.location.href = `${Domain}/?session=${SessionID}`;
                }
                if (metadata.cubeId) {
                    request(`/api/cube/${metadata.cubeId}/startDraft`,null,startDraftOnCompletion,startDraftOnCompletion,'POST');
                } else if (metadata.setId) {
                    request(`/api/retail_sets/${metadata.setId}/startDraft`,null,startDraftOnCompletion,startDraftOnCompletion,'POST');
                } else {
                    startDraftOnCompletion(null);
                }
            }
        });
    });
}