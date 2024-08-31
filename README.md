# strategy-steps-web-calculator
A simple, textual, calculator to keep tracks of the numbers for playing the WiiParty Strategy Steps Game in real life

This is not a full game. It features no graphics and has the sole intent to keep tracks of scores and numbers when playing the Strategy Steps Game from WiiParty IRL. 
Using a simple Website that communicates with a Websocket server, Players enter their choice of number. When everybody picked, the winner gets deduced and gains in score.

This lacks some major features such as announcing the winner, and was quickly built with the focus of providing a relatively stable experience. Rejoining Lobbys is implemented but not tested, other players choices are veiled in the Web Socket's broadcast messages to avoid cheating.

## In case anybody ever wants to use and deploy this

### Technologies

The Root directory houses the single python file that makes up the server. It is simply run and then listens for WebSockets trying to connect. In deployment, It also hosts the compiled Javascript&Html of the frontend with the FastAPI library.

This frontend is found in the `frontend` directory and is build upon SolidJs and the Socket.io Library.

### Running locally

For development, the frontend runs via Vite dev. Both Programs can be started with the `./dev.sh` file.

### Deploying

Create a `.env.sh` File that exports the environment variabled `LOCAL`, which is a boolean, and `SERVER_IP` with the deployments IP Adress (including eventual `http://` Prefix), which is subsequently hardcoded/backed into the compiled Javascript (Im too poor to rent a Domain, don't judge me).

Run the `build.sh` Script which compiles the SolidJS frontend via Vite (Vite gets the ip and port via another enviroment file `.env.staging` which this script creates), and initiates a docker build.
You can now deploy this image which contains the python script, and the compiled frontend. Default used port is 80 for external deploy and 8000 for local deploy
