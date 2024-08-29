import * as THREE from 'three';
import { degToRad } from './gameTools.js';
import * as ft from './gameTools.js';
import * as gameSocket from '../js/gameSocket.js';


import {RenderPass} from 'three/examples/jsm/postprocessing/RenderPass.js';
import {EffectComposer} from 'three/examples/jsm/postprocessing/EffectComposer.js';
import {UnrealBloomPass} from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';
import { RGBShiftShader } from 'three/examples/jsm/shaders/RGBShiftShader.js';
import { startCountdown } from '../js/countdown.js';
import { HorizontalBlurShader } from 'three/examples/jsm/shaders/HorizontalBlurShader.js';
import { setGameTime } from '../js/counter.js';

let animationId;

const scene = new THREE.Scene();
const renderer = new THREE.WebGLRenderer();
let menuSize = 110;
renderer.setSize((window.innerWidth  - menuSize), window.innerHeight);



// Camera
const camera = new THREE.PerspectiveCamera( 40, (window.innerWidth  - menuSize) / window.innerHeight, 0.1, 1000 );
const cameraPosition = new THREE.Vector3(0, 85, 0);
const cameraRotation = new THREE.Vector3(-90, 0, 0);


camera.position.copy(cameraPosition);
camera.rotation.x = degToRad(cameraRotation.x);
camera.rotation.y = degToRad(cameraRotation.y);
camera.rotation.z = degToRad(cameraRotation.z);


// Renderer
const renderScene = new RenderPass(scene, camera);
const composer = new EffectComposer(renderer);
composer.addPass(renderScene);

let bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth - menuSize, window.innerHeight),
  
  0.5,
  0.5,
  0.001
);
const rgbShift = new ShaderPass(RGBShiftShader);
rgbShift.uniforms['amount'].value = 0;  // Adjust chromatic aberration effect

const horizontalBlur = new ShaderPass(HorizontalBlurShader);
horizontalBlur.uniforms['h'].value = 0;

composer.addPass(bloomPass);
composer.addPass(horizontalBlur);
composer.addPass(rgbShift);


const zFightingOffset = 0.02;
// Field params
let fieldWidth = 80;
let fieldHeight = 50;


// Paddles
let paddleWidth = 2;
let paddleHeight = 8;
const borderColor = 0xFFFFFF;
const innerColor = 0xFFFFFF;
const paddleBorderWidth = 0.45;


let paddle1Position = new THREE.Vector3(-36, 0, 0);
let paddle2Position = new THREE.Vector3(36 , 0, 0);

const paddleBorderGeometry = new THREE.BoxGeometry(1, 1, 1);
const paddleBorderMaterial = new THREE.MeshBasicMaterial( {color: borderColor} ); 
const paddle1BorderObject = new THREE.Mesh( paddleBorderGeometry, paddleBorderMaterial );
const paddle2BorderObject = new THREE.Mesh( paddleBorderGeometry, paddleBorderMaterial );

const paddleInnerXGeometry = new THREE.BoxGeometry(1, 1 - paddleBorderWidth, 1);
const paddleInnerYGeometry = new THREE.BoxGeometry(1, 1 + zFightingOffset, 1);
const paddleInnerZGeometry = new THREE.BoxGeometry(1, 1 - paddleBorderWidth, 1);

const paddleInnerMaterial = new THREE.MeshStandardMaterial( {color: innerColor} ); 

const paddle1InnerXObject = new THREE.Mesh( paddleInnerXGeometry, paddleInnerMaterial );
const paddle1InnerYObject = new THREE.Mesh( paddleInnerYGeometry, paddleInnerMaterial );
const paddle1InnerZObject = new THREE.Mesh( paddleInnerZGeometry, paddleInnerMaterial );

const paddle2InnerXObject = new THREE.Mesh( paddleInnerXGeometry, paddleInnerMaterial );
const paddle2InnerYObject = new THREE.Mesh( paddleInnerYGeometry, paddleInnerMaterial );
const paddle2InnerZObject = new THREE.Mesh( paddleInnerZGeometry, paddleInnerMaterial );

paddle1BorderObject.scale.x = paddleWidth;
paddle1BorderObject.scale.z = paddleHeight;
paddle1InnerXObject.scale.x = paddleWidth + zFightingOffset;
paddle1InnerXObject.scale.z = paddleHeight - paddleBorderWidth;
paddle1InnerYObject.scale.x = paddleWidth - paddleBorderWidth;
paddle1InnerYObject.scale.z = paddleHeight - paddleBorderWidth;
paddle1InnerZObject.scale.x = paddleWidth - paddleBorderWidth;
paddle1InnerZObject.scale.z = paddleHeight + zFightingOffset;

paddle2BorderObject.scale.x = paddleWidth;
paddle2BorderObject.scale.z = paddleHeight;
paddle2InnerXObject.scale.x = paddleWidth + zFightingOffset;
paddle2InnerXObject.scale.z = paddleHeight - paddleBorderWidth;
paddle2InnerYObject.scale.x = paddleWidth - paddleBorderWidth;
paddle2InnerYObject.scale.z = paddleHeight - paddleBorderWidth;
paddle2InnerZObject.scale.x = paddleWidth - paddleBorderWidth;
paddle2InnerZObject.scale.z = paddleHeight + zFightingOffset;

scene.add( paddle1BorderObject, paddle1InnerXObject, paddle1InnerYObject, paddle1InnerZObject);
scene.add( paddle2BorderObject, paddle2InnerXObject, paddle2InnerYObject, paddle2InnerZObject);

movePaddle1To(paddle1Position);
movePaddle2To(paddle2Position);

// Ground plane
const groundWidth = fieldWidth + 4;
const groundHeight = fieldHeight + 4;
const groundGeometry = new THREE.PlaneGeometry(1, 1);
const groundMaterial = new THREE.MeshStandardMaterial( {color: 0xFFFFFF, emissive: 0x000000 ,metalness: 0.8} );
const groundObject = new THREE.Mesh(groundGeometry, groundMaterial);
groundObject.scale.x = groundWidth;
groundObject.scale.y = groundHeight;
scene.add(groundObject);
groundObject.rotateX(degToRad(-90));
groundObject.position.y = -0.8;


// Middle line 
const middleCubeGeometry = new THREE.BoxGeometry(0.2, 0.1, 0.2);
const middleCubeMaterial = new THREE.MeshBasicMaterial({color: 0xFFFFFF});

const middleCubesCount = 30;
let middleCubes = ft.createLineOfCubes(middleCubesCount, fieldHeight, middleCubeGeometry, middleCubeMaterial, scene)


// Borders
const wallBorderWidth = 0.45;
const wallHeight = 2;
const wallBorderGeometry = new THREE.BoxGeometry(1, 1, wallHeight);
const wallInnerXGeometry = new THREE.BoxGeometry(1, 1 - wallBorderWidth, wallHeight - wallBorderWidth);
const wallInnerYGeometry = new THREE.BoxGeometry(1, 1 + zFightingOffset, wallHeight - wallBorderWidth);
const wallInnerZGeometry = new THREE.BoxGeometry(1, 1 - wallBorderWidth, wallHeight + zFightingOffset);
const wallBorderMaterial = new THREE.MeshBasicMaterial({color: 0xFFFFFF});
const wallInnerMaterial = new THREE.MeshStandardMaterial({color: 0xFFFFFF, emissive: 0x111111});

const topWallBorderObject = new THREE.Mesh(wallBorderGeometry, wallBorderMaterial);
const topWallXInnerObject = new THREE.Mesh(wallInnerXGeometry, wallInnerMaterial);
const topWallYInnerObject = new THREE.Mesh(wallInnerYGeometry, wallInnerMaterial);
const topWallZInnerObject = new THREE.Mesh(wallInnerZGeometry, wallInnerMaterial);
topWallBorderObject.position.z = -fieldHeight / 2 - wallHeight / 2;
topWallXInnerObject.position.copy(topWallBorderObject.position);
topWallYInnerObject.position.copy(topWallBorderObject.position);
topWallZInnerObject.position.copy(topWallBorderObject.position);

const botWallBorderObject = new THREE.Mesh(wallBorderGeometry, wallBorderMaterial);
const botWallXInnerObject = new THREE.Mesh(wallInnerXGeometry, wallInnerMaterial);
const botWallYInnerObject = new THREE.Mesh(wallInnerYGeometry, wallInnerMaterial);
const botWallZInnerObject = new THREE.Mesh(wallInnerZGeometry, wallInnerMaterial);
botWallBorderObject.position.z = fieldHeight / 2 + wallHeight / 2;
botWallXInnerObject.position.copy(botWallBorderObject.position);
botWallYInnerObject.position.copy(botWallBorderObject.position);
botWallZInnerObject.position.copy(botWallBorderObject.position);

topWallBorderObject.scale.x = fieldWidth;
topWallXInnerObject.scale.x = fieldWidth + zFightingOffset;
topWallZInnerObject.scale.x = fieldWidth - wallBorderWidth;
topWallYInnerObject.scale.x = fieldWidth - wallBorderWidth;

botWallBorderObject.scale.x = fieldWidth;
botWallXInnerObject.scale.x = fieldWidth + zFightingOffset;
botWallZInnerObject.scale.x = fieldWidth - wallBorderWidth;
botWallYInnerObject.scale.x = fieldWidth - wallBorderWidth;


scene.add(topWallBorderObject, topWallXInnerObject, topWallYInnerObject, topWallZInnerObject);
scene.add(botWallBorderObject, botWallXInnerObject, botWallYInnerObject, botWallZInnerObject);

const topWallLight = new THREE.RectAreaLight(0xFFFFFFF, 1, fieldWidth, 1);
const bottomWallLight = new THREE.RectAreaLight(0xFFFFFFF, 1, fieldWidth, 1);
topWallLight.position.copy(topWallBorderObject.position);
bottomWallLight.position.copy(botWallBorderObject.position);
topWallLight.position.y -= 0.35;
bottomWallLight.position.y -= 0.35;
topWallLight.rotation.x = degToRad(-90);
bottomWallLight.rotation.x = degToRad(-90);


// Ball
let ballSize = 2;
const ballCubeGeometry = new THREE.BoxGeometry(1, 1, 1);
const ballCubeInnerGeometry = new THREE.BoxGeometry(1, 1 + zFightingOffset, 1);
const ballCubeMaterial = new THREE.MeshBasicMaterial({color: 0xBBBBBB});
const ballCubeInnerMaterial = new THREE.MeshBasicMaterial({color: 0xBBBBBB});
const ballCubeObject = new THREE.Mesh(ballCubeGeometry, ballCubeMaterial);
const ballCubeInnerObject = new THREE.Mesh(ballCubeInnerGeometry, ballCubeInnerMaterial);

ballCubeObject.scale.x = ballSize;
ballCubeObject.scale.z = ballSize;
ballCubeInnerObject.scale.x = ballSize - paddleBorderWidth;
ballCubeInnerObject.scale.z = ballSize - paddleBorderWidth;

scene.add(ballCubeObject, ballCubeInnerObject);

function moveBallCube(x, y){
    ballCubeObject.position.x = x;
    ballCubeObject.position.z = y;
    ballCubeInnerObject.position.x = x;
    ballCubeInnerObject.position.z = y;
}



// User 
let roomName = undefined;
let upKeyHolded = false;
let downKeyHolded = false;
let wKeyHolded = false;
let sKeyHolded = false;
let inputsIntervalId = undefined;
let gameMode = "";

export function changeGameMode(mode){
    gameMode = mode;
}

let loaded = false;
let gameRunning = false;

export function isGameLoaded(){
    return loaded;
}

export function setGameRunningToFalse(){
    gameRunning = false;
}

let container = null;
// OnLoad
let currentWidth = 0;
let currentHeight = 0;
export function startAnimation(){
    container = document.querySelector('#canvas');
    container.append(renderer.domElement);
    currentHeight = container.offsetHeight;
    currentWidth = container.offsetWidth;
    onWindowResize(container.offsetWidth, container.offsetHeight);
    if (!animationId)
        animate();
    resetScene();
    handleInputs();
    gameSocket.listenGameUpdates();
    
    loaded = true;
    gameRunning = true;
}


//OnUnload
export function stopAnimation(){
    resetScene();
    cancelAnimationFrame(animationId);
    if (container && container.parentNode)
        container.parentNode.removeChild(container);
    animationId = undefined;
    clearInterval(inputsIntervalId);
    removeHandleInputs();
    if (gameRunning)
        gameSocket.leaveGame();
    loaded = false;
    gameRunning = false;
}

//Update
function animate() {
    animationId = requestAnimationFrame( animate );

    if (isGoalExplosionOn)
        processGoalExplosionParticles();

    onWindowResize(container.offsetWidth, container.offsetHeight);

	composer.render();
}


function onWindowResize(width, height) {
    width = width - 10;
    if (currentWidth == width && currentHeight == height){
        return;
    }
    const aspect = (width / height);
    if (aspect < 1.625){
        height = width / 1.625;
    }
    camera.aspect = (width / height);
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
    composer.setSize(width, height);
}

function resetScene(){


    moveBallCube(0, 0);
    movePaddle1To(new THREE.Vector3(-36, 0, 0));
    movePaddle2To(new THREE.Vector3(36, 0, 0));

    paddle1Position = new THREE.Vector3(-36, 0, 0);
    paddle2Position = new THREE.Vector3(36 , 0, 0);
}

resetScene();

export function updateGameData(data){
    if (loaded == false && gameRunning){
        gameSocket.leaveGame();
    }
    const gameState = data.state;
    moveBallCube(gameState.Ball[0] / 10, -gameState.Ball[1] / 10);
    movePaddle1To(new THREE.Vector3(gameState.Left_Player[0] / 10, 0, -gameState.Left_Player[1] / 10));
    movePaddle2To(new THREE.Vector3(gameState.Right_Player[0] / 10, 0, -gameState.Right_Player[1] / 10));

    if (gameState.Hit == "right scored")
    {
        startGoalExplosion("left");
        startCountdown(0);
    }
    else if (gameState.Hit == "left scored")
    {
        startGoalExplosion("right");
        startCountdown(0);
    }

    setGameTime(gameState.Time);
}

export function setGameSizes(data){
    ballSize = data.ball_side / 10;
    paddleWidth = data.player_w / 10;
    paddleHeight = data.player_h / 10;
    fieldWidth = data.playfield_w / 10;
    fieldHeight = data.playfield_h / 10;

    
    paddle1BorderObject.scale.x = paddleWidth;
    paddle1BorderObject.scale.z = paddleHeight;
    paddle1InnerXObject.scale.x = paddleWidth + zFightingOffset;
    paddle1InnerXObject.scale.z = paddleHeight - paddleBorderWidth;
    paddle1InnerYObject.scale.x = paddleWidth - paddleBorderWidth;
    paddle1InnerYObject.scale.z = paddleHeight - paddleBorderWidth;
    paddle1InnerZObject.scale.x = paddleWidth - paddleBorderWidth;
    paddle1InnerZObject.scale.z = paddleHeight + zFightingOffset;

    paddle2BorderObject.scale.x = paddleWidth;
    paddle2BorderObject.scale.z = paddleHeight;
    paddle2InnerXObject.scale.x = paddleWidth + zFightingOffset;
    paddle2InnerXObject.scale.z = paddleHeight - paddleBorderWidth;
    paddle2InnerYObject.scale.x = paddleWidth - paddleBorderWidth;
    paddle2InnerYObject.scale.z = paddleHeight - paddleBorderWidth;
    paddle2InnerZObject.scale.x = paddleWidth - paddleBorderWidth;
    paddle2InnerZObject.scale.z = paddleHeight + zFightingOffset;

    groundObject.scale.x = groundWidth;
    groundObject.scale.y = groundHeight;

    topWallBorderObject.scale.x = fieldWidth;
    topWallXInnerObject.scale.x = fieldWidth + zFightingOffset;
    topWallZInnerObject.scale.x = fieldWidth - wallBorderWidth;
    topWallYInnerObject.scale.x = fieldWidth - wallBorderWidth;

    botWallBorderObject.scale.x = fieldWidth;
    botWallXInnerObject.scale.x = fieldWidth + zFightingOffset;
    botWallZInnerObject.scale.x = fieldWidth - wallBorderWidth;
    botWallYInnerObject.scale.x = fieldWidth - wallBorderWidth;


    ballCubeObject.scale.x = ballSize;
    ballCubeObject.scale.z = ballSize;
    ballCubeInnerObject.scale.x = ballSize - paddleBorderWidth;
    ballCubeInnerObject.scale.z = ballSize - paddleBorderWidth;

    while(middleCubes.length > 0){
        scene.remove(middleCubes[0]);
        middleCubes.shift();
    }
    middleCubes = ft.createLineOfCubes(middleCubesCount, fieldHeight, middleCubeGeometry, middleCubeMaterial, scene);
}



function movePaddle1To(vec)
{
  paddle1BorderObject.position.copy(vec);
  paddle1InnerXObject.position.copy(vec);
  paddle1InnerYObject.position.copy(vec);
  paddle1InnerZObject.position.copy(vec);  
}

function movePaddle2To(vec)
{
    paddle2BorderObject.position.copy(vec);
    paddle2InnerXObject.position.copy(vec);
    paddle2InnerYObject.position.copy(vec);
    paddle2InnerZObject.position.copy(vec);
}


function handleInputs(){
    document.addEventListener('keydown', keyPress);
    document.addEventListener('keyup', keyUp);

    if (gameMode == "online")
        inputsIntervalId = setInterval(readInputs, 1000 / 60);
    else if (gameMode == "offline")
        inputsIntervalId = setInterval(readOfflineInputs, 1000 / 60);
}

function removeHandleInputs(){
    document.removeEventListener('keydown', keyPress);
    document.removeEventListener('keyup', keyUp);
    upKeyHolded = false;
    downKeyHolded = false;
    wKeyHolded = false;
    sKeyHolded = false;
    inputsIntervalId = undefined;
}

function keyPress(event){
    if (event.code == 'ArrowUp') {
        upKeyHolded = true;
    }
    else if (event.code == 'ArrowDown') {
        downKeyHolded = true;
    }
    if (event.code == 'KeyW')
        wKeyHolded = true;
    else if (event.code == 'KeyS')
        sKeyHolded = true;
}

function keyUp(event){
    if (event.code == 'ArrowUp') {
        upKeyHolded = false;
    }
    else if (event.code == 'ArrowDown') {
        downKeyHolded = false;
    }
    if (event.code == 'KeyW'){
        wKeyHolded = false;
    }
    else if (event.code == 'KeyS'){
        sKeyHolded = false;
    }
}

function readInputs(){
    if (upKeyHolded || wKeyHolded){
        gameSocket.send(JSON.stringify({
            "type": "update_input",
            "mode": "online",
            "key": "UP"}));
    }
    else if (downKeyHolded || sKeyHolded){
        gameSocket.send(JSON.stringify({
            "type": "update_input",
            "mode": "online",
            "key": "DOWN"}));
    }
}


function readOfflineInputs(){

    if (upKeyHolded || downKeyHolded || wKeyHolded || sKeyHolded){
        let user1Input = "";
        let user2Input = "";

        if (wKeyHolded)
            user1Input = "UP";
        else if (sKeyHolded)
            user1Input = "DOWN";
        if (upKeyHolded)
            user2Input = "UP";
        else if (downKeyHolded)
            user2Input = "DOWN";
        const json = {
            "type": "update_input",
            "mode": "offline"
        }
        if (user1Input != "")
            json[0] = user1Input;
        if (user2Input != "")
            json[1] = user2Input;

        gameSocket.send(JSON.stringify(json));
    }
}

//Goal explosion
const goalExplosionParticles = new THREE.BufferGeometry();
const goalExplosionParticlesCount = 100;
const goalExplosionParticlesPositions = new Float32Array(goalExplosionParticlesCount * 3);
for (let i = 0; i < goalExplosionParticlesCount; i++){
    goalExplosionParticlesPositions[i * 3] = 0;
    goalExplosionParticlesPositions[i * 3 + 1] = 0;
    goalExplosionParticlesPositions[i * 3 + 2] = 0;
}
goalExplosionParticles.setAttribute('position', new THREE.BufferAttribute(goalExplosionParticlesPositions, 3));

const goalExplosionParticlesMaterial = new THREE.PointsMaterial({
    color: 0xFFFFFF,
    size: 0.8,
    transparent: true,
    opacity: 0
});
const goalExplosionsParticleSystem = new THREE.Points(goalExplosionParticles, goalExplosionParticlesMaterial);
scene.add(goalExplosionsParticleSystem);

const goalExplosionParticlesMaxPosition = 80;
const goalExplosionParticlesMinPosition = 30;
let explosionParticlesHorizontalModdifier = 1;
let goalExplosionParticlesPositionsDelta = new Float32Array(goalExplosionParticlesCount);
let isGoalExplosionOn = false;
const goalExplosionDuration = 0.4;
let goalExplosionStartTime = 0;
let goalPosition;

const chromaticAberrationMaxValue = 0.005;
const horizontalBlurMaxValue = 1 / 800;

function startGoalExplosion(side){

    explosionParticlesHorizontalModdifier = (side == "left")? 1 : -1;
    goalPosition = (fieldWidth / 2 + 10) * (explosionParticlesHorizontalModdifier * -1);
    goalExplosionStartTime = Date.now();
    
    for (let i = 0; i < goalExplosionParticlesCount; i++){
        goalExplosionParticlesPositions[i * 3] = goalPosition;
        goalExplosionParticlesPositions[i * 3 + 1] = 0;
        goalExplosionParticlesPositions[i * 3 + 2] = Math.random() * fieldHeight - fieldHeight / 2;
        goalExplosionParticlesPositionsDelta[i] = (Math.random() * (goalExplosionParticlesMaxPosition - goalExplosionParticlesMinPosition) + goalExplosionParticlesMinPosition) * explosionParticlesHorizontalModdifier;
    }
    goalExplosionsParticleSystem.geometry.attributes.position.needsUpdate = true;

    isGoalExplosionOn = true;
    rgbShift.uniforms['amount'].value = chromaticAberrationMaxValue;
}

function processGoalExplosionParticles(){
    
    let explosionPercentaje = (Date.now() - goalExplosionStartTime) / (goalExplosionDuration * 1000);
    if (explosionPercentaje >= 1){
        isGoalExplosionOn = false;
        goalPosition = 5000;
        explosionPercentaje = 1;
    }
    for (let i = 0; i < goalExplosionParticlesCount; i++){
        goalExplosionParticlesPositions[i * 3] = goalPosition + goalExplosionParticlesPositionsDelta[i] * ft.easeOutCirc(explosionPercentaje);
        }
    goalExplosionParticlesMaterial.opacity = 1 - explosionPercentaje;
    goalExplosionsParticleSystem.geometry.attributes.position.needsUpdate = true;
    screenShake(explosionPercentaje);
    
    horizontalBlur.uniforms['h'].value = horizontalBlurMaxValue * (1 - explosionPercentaje);
    rgbShift.uniforms['amount'].value = chromaticAberrationMaxValue * (1 - explosionPercentaje);
}

const shakeAmount = 5;
const shakeHighestPoint = 0.2;
function screenShake(explosionPercentaje){

    let shake;
    if (explosionPercentaje < shakeHighestPoint)
        shake = shakeAmount * explosionParticlesHorizontalModdifier * ft.easeInOutQuad(explosionPercentaje / shakeHighestPoint);
    else
        shake = shakeAmount * explosionParticlesHorizontalModdifier * ft.easeInOutQuad(1 - (explosionPercentaje - shakeHighestPoint) / (1 - shakeHighestPoint));
    camera.position.x = shake;
}
