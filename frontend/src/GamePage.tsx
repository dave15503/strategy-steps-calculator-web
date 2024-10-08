import { Component, createEffect, createRenderEffect, createSignal } from "solid-js";
import { SessionInformation } from "./App";
import { BACKEND_URI } from "../globals";
import { io } from "socket.io-client";
import ErrorView from "./ErrorView";



interface GamePageProps {
    SessionInfo: SessionInformation;
}

interface Contestant {
    Choice: number;
    DidWin: boolean;
    Name: string;
    Progress: number;
    IsConnected: boolean;
    State: "NOT_READY" | "READY" | "PICKING" | "HAS_PICKED";
}

interface GameOptions {
    Choices: number[];
    Goal: number;
    PlayerCount: number;
}

interface Session {
    Contestants: Record<string, Contestant>;
    GameOptions: GameOptions;
    Id: number;
}

interface ContestantLineProps {
    Contestant: Contestant;
    Goal: number
}

const ContestantLine: Component<ContestantLineProps> = (props: ContestantLineProps) => {
    const cont = props.Contestant;
    

    let isConnected = cont.IsConnected ? "○" : "●"

    let status = "⌛"
    if (cont.State == "HAS_PICKED"){
        status = "✅"
    }
    else if (cont.Progress >= props.Goal) {
        status = "🚩"
    }

    return  <tr class="contestant">
                <td style={`color: ${ cont.IsConnected ? "green" : "red"};`}>{isConnected}</td>
                <td class="name">{cont.Name}</td>
                <td>{status}</td>
                <td class={cont.DidWin ? "won last-guess" : "last-guess"}>
                    {cont.Choice == -1 ? "?" : cont.Choice}
                </td>
                <td>{cont.Progress}</td>
            </tr>
}



const GamePage: Component<GamePageProps> = (props: GamePageProps) => {
    
    const [error, setError] = createSignal<any>(null);

    const [session, setSession] = createSignal<Session | undefined>(undefined);

    // connect to ws
    const socket = io(BACKEND_URI + "/", {
        query: props.SessionInfo,
        autoConnect: false,
        closeOnBeforeunload: true
    });


    socket.on("connect_error", (err: Error) => {
        setSession(undefined);
        setError(err);
    })

    socket.on("error", (msg: string) => {
        setSession(undefined);
        setError(new Error(msg));
    })

    socket.on("connect", () => {
        console.log("connected!");
    })

    socket.on("broadcast", (data: Session) => {
        console.log(data)
        setSession(data)
    })


    socket.connect()

    const onViewSelectChoice = (value: number) => {
        socket.emit("choose", {
            ...props.SessionInfo,
            Choice: value
        })
    } 


    const currentPlayers = () => {
        const sess = session();
        if(sess == undefined) return 0;
        let count = 0;
        Object.entries(sess.Contestants).forEach(([key, val]) => {
            if(val.IsConnected) count++;
        });
        return count;
    }
    const playerCount = () => {
        const sess = session();
        if(sess == undefined) return 0;
        return sess.GameOptions.PlayerCount
    }

    const hasFinished = () => {
        const sess = session();
        if(sess == null) return false;
        let me = sess.Contestants[props.SessionInfo.Name]
        return me.Progress >= sess.GameOptions.Goal
    }

    return (
        <div class="content">
            <div>Name: {props.SessionInfo.Name}</div>
            <div>Session {props.SessionInfo.SessionId}</div>
            <hr></hr>
            {error() ? <ErrorView Error={error()}></ErrorView> : ""}
            {session() ? <>
                <div>Goal to reach: {session()!.GameOptions.Goal}</div>
                <div>{currentPlayers()} of {playerCount()} Players joined:</div>
                <table id="contestants-table">
                    <tbody>
                        <tr class="contestant header">
                            <th></th>
                            <th class="name">Name</th>
                            <th></th>
                            <th>Last</th>
                            <th>Progress</th>
                        </tr>
                        {Object.entries(session()!.Contestants).map(([k, v]) => {
                            return <ContestantLine Contestant={v as Contestant} Goal={session()!.GameOptions.Goal}></ContestantLine>
                        })}
                    </tbody>
                </table>
                <hr></hr>
                {
                    currentPlayers() < playerCount() ? 
                        <div>Waiting for Players...</div>
                    : (
                        hasFinished() ?
                        <div class="finish-message">
                            You finished!
                        </div>
                        :
                        <div class="choice-buttons">
                            {session()!.GameOptions.Choices.map((c:number) => <div onclick={() => onViewSelectChoice(c)}>{c}</div>)}
                        </div>
                    )
                }
                
            </> : ""}
        </div>
    )
}

export default GamePage;
