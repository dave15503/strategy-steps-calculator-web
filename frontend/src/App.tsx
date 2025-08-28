import { createSignal, type Component } from 'solid-js';
import StartPage from './StartPage';
import GamePage from './GamePage';

export interface SessionInformation {
    SessionId: number;
    Name: string;
}

const App: Component = () => {
    
    const [session, setSession ] = createSignal<SessionInformation | null>(null);
    

    return (
        <div class='body'>
            <h2>
                Strategy Steps
            </h2>
            {
                session() == null ? 
                    <StartPage onSubmit={(sessionInfo) => setSession(sessionInfo)}></StartPage> :
                    <GamePage SessionInfo={session()!}></GamePage>
            }
            <footer>
                <h5>
                    Cookie Notice
                </h5>
                This page writes to localStorage to save username and last joined sessionId entered in the text fields above. You can
                opt out from this policy by not using this page 👍.
            </footer>
        </div>
    );
};

export default App;
