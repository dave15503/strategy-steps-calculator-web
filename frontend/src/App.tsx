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
        </div>
    );
};

export default App;
