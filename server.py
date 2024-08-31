from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from socketio.exceptions import ConnectionRefusedError, ConnectionError
from enum import Enum
import random
import time
import uvicorn
import socketio
import json
import urllib
import asyncio
import os

random.seed(time.time_ns())

api = FastAPI(title="api")
app = FastAPI(title="app")

api.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/api", api)

# host the static files of the node app
# Will use the relative path for development,
# provide the path to the static file in prod via ENV variable
static_webpath = os.environ.get("SS_STATIC_WEBPATH", "./frontend/dist")
server_port = int(os.environ.get("SS_SERVER_PORT", "8000"))

if os.path.isdir(static_webpath):
    app.mount("/", StaticFiles(directory=static_webpath, html=True), name=static_webpath)
else:
    print("Deploy directory does not exist yet, this is normal when in dev mode and the frontend has never been built before")

# WEBSOCKETS
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')

# ASGI application wrapper
asgi_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)


class ContestantState(Enum):
    NOT_READY = "NOT_READY" # Euqals DONE
    READY = "READY"
    PICKING = "PICKING"
    HAS_PICKED = "HAS_PICKED"
    DONE = "NOT_READY"

class Contestant:

    def __init__(self, name, sid):
        self.Name = name
        self.Sid = sid
        self.Choice = -1
        self.Progress = 0
        self.State = ContestantState.NOT_READY
        self.DidWin = False
        self.IsConnected = True

    def to_json(self, unveil):
        jobj = dict()
        jobj["Name"] = self.Name
        jobj["Sid"] = self.Sid
        jobj["Choice"] = self.Choice if self.State == ContestantState.DONE else -1
        jobj["Progress"] = self.Progress
        jobj["State"] = self.State.value
        jobj["DidWin"] = self.DidWin
        jobj["IsConnected"] = self.IsConnected
        return jobj

class GameOptions:

    def __init__(self, choices, playerCount, goal):
        self.Choices = choices
        self.PlayerCount = playerCount
        self.Goal = goal

    def to_json(self):
        jobj = dict()
        jobj["Choices"] = self.Choices
        jobj["PlayerCount"] = self.PlayerCount
        jobj["Goal"] = self.Goal
        return jobj

class Session:

    def __init__(self, playerCount, choices, goal):
        self.Id = random.randint(1, 999)
        self.GameOptions = GameOptions(choices, playerCount, goal)
        self.Contestants = dict()
        self.Lock = asyncio.Lock()

    def get_connected_contestants_count(self):
        count = 0
        for contestant in self.Contestants:
            if contestant.IsConnected:
                count += 1
        return count

    def add_contestant(self, name, sid):
        print(self.Contestants.keys())
        # check if it is a reconnect attempt
        if name in self.Contestants.keys():
            if self.Contestants[name].IsConnected:
                raise Exception("User of this name already exists and is already connected")
                return
            else:
                # reconnect
                self.Contestants[name].IsConnected = True
                self.Contestants[name].Sid = sid
                return
        else:
            # new user
            # check if lobby is full
            if len(self.Contestants.keys()) == self.GameOptions.PlayerCount:
                raise Exception("Lobby/Session is already full")
                return
            else:
                self.Contestants[name] = Contestant(name, sid)
                return

            

    def disconnect_contestant(self, name, sid):

        if name in self.Contestants.keys():
            if self.Contestants[name].Sid != sid:
                return # we attempted to disconnect the wrong client who claimed the same name!
            self.Contestants[name].IsConnected = False

    def choose(self, name, choice):

        if name not in self.Contestants.keys():
            raise Exception( "User " + name + " does not exist in this session")
            return

        # ignore if already reached the goal
        if self.Contestants[name].Progress >= self.GameOptions.Goal:
            return

        self.Contestants[name].Choice = choice
        self.Contestants[name].State = ContestantState.HAS_PICKED

    def get_competing_contestants(self):
        competing = list(filter(lambda c: c.Progress < self.GameOptions.Goal, self.Contestants.values()))
        return competing

    def evaluate(self):
        if all(c.State == ContestantState.HAS_PICKED and c.IsConnected for c in self.get_competing_contestants()):

            counts = dict()
            for possible_choice in self.GameOptions.Choices:
                counts[possible_choice] = 0

            # filter out unique choices by counting all unique votes
            for contestant in self.get_competing_contestants():
                counts[contestant.Choice] += 1

            for contestant in self.get_competing_contestants():

                contestantKey = contestant.Name

                if counts[contestant.Choice] == 1:
                    # contestant won
                    self.Contestants[contestantKey].Progress += contestant.Choice
                    self.Contestants[contestantKey].DidWin = True
                else:
                    self.Contestants[contestantKey].DidWin = False
                
                #reset all flags
                self.Contestants[contestantKey].State = ContestantState.DONE
            

    def connected_players(self):
        count = 0
        for k in self.Contestants.keys():
            if self.Contestants[k].IsConnected:
                count += 1
        return count


    async def broadcast(self):
        sessionData = self.to_json()
        await sio.emit("broadcast", data=sessionData, room=str(self.Id))


    def to_json(self, unveil = False):
        jobj = dict()
        jobj['Id'] = self.Id
        jobj['GameOptions'] = self.GameOptions.to_json()
        jobj['Contestants'] = dict()
        for k in self.Contestants.keys():
            jobj['Contestants'][k] = self.Contestants[k].to_json(unveil)
        return jobj

    def to_json_str(self):
        return json.dumps(self.to_json())

sessions: dict[int,Session] = dict()


def parse_envir(environment):
    query_string = environment['asgi.scope']['query_string']
    query_string = urllib.parse.unquote(query_string) # decode to utf8 string, not binary b string
    query_dict = urllib.parse.parse_qs(query_string, encoding="utf-8")

    if not ("SessionId" in query_dict.keys() and "Name" in query_dict.keys()):
        raise ConnectionRefusedError("Must specify name and sessionId")

    try:
        sessionId = int(query_dict["SessionId"][0])
        name = query_dict["Name"][0]
    except:
        raise ConnectionRefusedError("Could not parse query parameters!")

    return (sessionId, name)


@api.get("/start_session")
def get_start_session(PlayerCount: int = 2, Choices: str = "1, 3, 5", Goal:int = 1):

    choices = list(map(lambda s: int(s), Choices.split(",")))

    s = Session(PlayerCount, choices, Goal)
    while s.Id in sessions.keys():
        s = Session(PlayerCount, choices, Goal)
            
    sessions[s.Id] = s

    return s.Id

@sio.on("connect")
async def connect(sid, env):

    sessionId, name = parse_envir(env)    

    # check if the requested session exists
    if sessionId not in sessions.keys():
        raise ConnectionRefusedError("Requested Session does not exist!")

    session = sessions[sessionId]


    async with session.Lock:
        
        try:
            session.add_contestant(name, sid)
        except Exception as e:
            await sio.emit("error", e.args[0], to=sid)
            return

        # create a room with the name of the session
        await sio.enter_room(sid=sid, room=str(sessionId))

        # add the new client to session
        await session.broadcast()

        

@sio.on("choose")
async def choose(sid, payload):

    sessionId, name = parse_envir(sio.get_environ(sid))

    if not sessionId in sessions.keys():
        await sio.emit("error", "Requested Session does not exist!")
        return

    session = sessions[sessionId]

    if session.GameOptions.PlayerCount != session.connected_players():
        await sio.emit("error", "Still waiting for players!")
        return

    async with session.Lock:
        try:
            session.choose(name, payload["Choice"])    
        except Exception as ex:
            await sio.emit("error", ex.args[0], to=sid)
            return

        session.evaluate()
        await session.broadcast()


    return

    
@sio.on("disconnect")
async def disconnect(sid):

    sessionId, name = parse_envir(sio.get_environ(sid))

    if sessionId not in sessions.keys():
        return

    async with sessions[sessionId].Lock:
        # remove the new client from the session
        sessions[sessionId].disconnect_contestant(name, sid)
        await sessions[sessionId].broadcast()
        



    print("Client Disconnected: "+" "+str(sid))



if __name__=="__main__":
    uvicorn.run(asgi_app, host="0.0.0.0", port=server_port)