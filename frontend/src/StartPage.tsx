import { Component } from "solid-js"
import { Properties } from "solid-js/web";
import { BACKEND_URI } from "../globals";
import { SessionInformation } from "./App";



interface StartPageProps {
    onSubmit: (info: SessionInformation) => void;
}


const StartPage: Component<StartPageProps> = (props: StartPageProps) => {
    
    let nameTextareaDom!: HTMLTextAreaElement, idTextareaDom!: HTMLTextAreaElement;
    let choicesTextareaDom!: HTMLTextAreaElement, playerInputDom!: HTMLInputElement;
    let goalInputDom!: HTMLInputElement;

    const createSession = async () => {
        
        const request = await fetch(BACKEND_URI + "/api/start_session?" + new URLSearchParams({
            PlayerCount: playerInputDom.value,
            Choices: choicesTextareaDom.value,
            Goal: goalInputDom.value
        }));
        const text = await request.text();
        
        props.onSubmit({
            Name: nameTextareaDom.value,
            SessionId: parseInt(text),
           
        })
    }

    const joinSession = () => {



        props.onSubmit({
            Name: nameTextareaDom.value,
            SessionId: parseInt(idTextareaDom.value)
        })
    }


    return (
        <div>
            <div class="btn-row">
                <div>Name</div>
                <textarea ref={nameTextareaDom} rows={1} cols={20}></textarea>
            </div>
            <hr></hr>
            <h4>Join a Session</h4>
            <div class="btn-row">
                <div>3 Digit Code</div>
                <textarea ref={idTextareaDom} rows={1} cols={20}></textarea>
            </div>
            <div class="btn-row">
                <div></div>
                <button onclick={() => joinSession()}>Join by code</button>
            </div>
            <hr></hr>
            <h4>Create a Session</h4>
            <div class="btn-row">
                <div>Choices (csv)</div>
                <textarea ref={choicesTextareaDom} rows={1} cols={20} value="1, 2, 3, 4, 5">1, 2, 3, 4, 5</textarea>
            </div>
            <div class="btn-row">
                <div>Players</div>
                <input ref={playerInputDom} type="number" min="2" max="100" value="2"></input>
            </div>
            <div class="btn-row">
                <div>Goal</div>
                <input ref={goalInputDom} type="number" min="1" max="100" value="5"></input>
            </div>
            <div class="btn-row">
                <div></div>
                <button onclick={() => createSession()}>Start Session</button>
            </div>
            
        </div>
    );
}


export default StartPage;