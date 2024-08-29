import * as THREE from 'three';
import {RenderPass} from 'three/examples/jsm/postprocessing/RenderPass.js';
import {EffectComposer} from 'three/examples/jsm/postprocessing/EffectComposer.js';
import {UnrealBloomPass} from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
let animationId = null;
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('app-background').appendChild(renderer.domElement);

const renderScene = new RenderPass(scene, camera);
const composer = new EffectComposer(renderer);
composer.addPass(renderScene);

let bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth - 110, window.innerHeight),
    
    2.5,
    1.0,
    0.001
);

composer.addPass(bloomPass);


function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    composer.setSize(window.innerWidth, window.innerHeight);
}
window.addEventListener('resize', onWindowResize);




camera.position.z = 5;
camera.rotation.z = 0.2;

// Handle window resize

// Array to hold the cubes
const cubes = [];
const gridSize = 12;
const cubeSize = 1; // Set the size of each cube to 1 unit
const cubeMargin = 0.002;

// Create a grid of cubes
for (let x = -gridSize; x < gridSize; x++) {
    for (let y = -gridSize; y < gridSize; y++) {
        const geometry = new THREE.BoxGeometry(cubeSize - cubeMargin, cubeSize - cubeMargin, cubeSize);
        const material = new THREE.MeshBasicMaterial({ color: 0x000000}); // Black color
        const cube = new THREE.Mesh(geometry, material);
        cube.position.set(x * cubeSize, y * cubeSize, 0);
        scene.add(cube);
        cubes.push(cube);

        // Add borders to the cube
        const edges = new THREE.EdgesGeometry(geometry);
        const lineMaterial = new THREE.LineBasicMaterial({ color: 0xd17aff }); // Border color
        const lines = new THREE.LineSegments(edges, lineMaterial);
        cube.add(lines);
    }
}

//
const textureLoader = new THREE.TextureLoader();
const particleTexture = textureLoader.load('https://threejs.org/examples/textures/sprites/disc.png');

// Create particles
const particleCount = 2000;
const particlesGeometry = new THREE.BufferGeometry();
const particlesGeometry2 = new THREE.BufferGeometry();
const particlesGeometry3 = new THREE.BufferGeometry();
const particlesMaterial = new THREE.PointsMaterial({
    color: 0xa07aff,
    size: 0.02,
    map: particleTexture,
    transparent: true,
    alphaTest: 0.5
});
const particlesMaterial2 = new THREE.PointsMaterial({
    color: 0xff7aca,
    size: 0.02,
    map: particleTexture,
    transparent: true,
    alphaTest: 0.5
});
const particlesMaterial3 = new THREE.PointsMaterial({
    color: 0xffa97a,
    size: 0.02,
    map: particleTexture,
    transparent: true,
    alphaTest: 0.5
});

const positions = [];
for (let i = 0; i < particleCount; i++) {
    positions.push((Math.random() - 0.5) * gridSize);
    positions.push((Math.random() - 0.5) * gridSize);
    positions.push((Math.random() - 0.5) * 5 + 2);
}
const positions2 = [];
for (let i = 0; i < particleCount; i++) {
    positions2.push((Math.random() - 0.5) * gridSize);
    positions2.push((Math.random() - 0.5) * gridSize);
    positions2.push((Math.random() - 0.5) * 5 + 2);
}
const positions3 = [];
for (let i = 0; i < particleCount; i++) {
    positions3.push((Math.random() - 0.5) * gridSize);
    positions3.push((Math.random() - 0.5) * gridSize);
    positions3.push((Math.random() - 0.5) * 5 + 2);
}

particlesGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
particlesGeometry2.setAttribute('position', new THREE.Float32BufferAttribute(positions2, 3));
particlesGeometry3.setAttribute('position', new THREE.Float32BufferAttribute(positions3, 3));

const particles = new THREE.Points(particlesGeometry, particlesMaterial);
const particles2 = new THREE.Points(particlesGeometry2, particlesMaterial2);
const particles3 = new THREE.Points(particlesGeometry3, particlesMaterial3);
scene.add(particles, particles2, particles3);

const timeMult = 0.02;
const zMult = 2;

let makeTransition = false;
let startTransition = false;
const transitionDuration = 500;
let startTime = 0;
let timeOffset = 0;
let easedT = 0;

function easeInOutQuad(x) {
  return Math.sqrt(1 - Math.pow(x - 1, 2));
}

export function startBackgroundTransition(){
    makeTransition = true;
    startTransition = true;
    timeOffset += easedT;
    easedT = 0;
}

let shakeAmplitude = 0.6;
let shakeFrequency = 0.01


/* import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';

const controls = new OrbitControls( camera, renderer.domElement ); */

//OnLoad
export function startBackgroundAnimation(){
    if (!animationId)
        animate();
}

//OnUnload
export function stopBackgroundAnimation(){
    if (animationId != null){
        cancelAnimationFrame(animationId);
        animationId = null;
        camera.position.x = 50;
        composer.render();
    }
}

function animate() {
    animationId = requestAnimationFrame( animate );

    if (makeTransition){
        if (startTransition){
            startTime = Date.now();
            startTransition = false;
        }
        const elapsedTime = Date.now() - startTime;
        const t = Math.min(elapsedTime / transitionDuration, 1);
        easedT = easeInOutQuad(t) * 4000;
        if (t == 1){
            makeTransition = false;
            timeOffset += easedT;
            easedT = 0;
        }
    }

    // Update cube positions for a noise effect
    cubes.forEach(cube => {
        cube.position.z = Math.sin((Date.now() + timeOffset + easedT) * 0.001 * timeMult + (cube.position.x + cube.position.y) * 0.5) * zMult;
    });

    const shakeX = shakeAmplitude * Math.sin(Date.now() * 0.001 * shakeFrequency);
    const shakeY = shakeAmplitude * Math.sin(Date.now() * 0.001 * shakeFrequency * 1.5);
    camera.position.x = shakeX;
    camera.position.y = shakeY;

    composer.render();
}

animate();