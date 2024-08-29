import * as THREE from 'three';

export function createLineOfCubes(middleCubesCount, playHeight, middleCubeGeometry, middleCubeMaterial, scene) {
	const cubes = [];
  
	for (let i = 0; i < middleCubesCount; i++) {
		const cube = new THREE.Mesh(middleCubeGeometry, middleCubeMaterial);
		cube.position.z = playHeight / middleCubesCount * (i + 0.5) - (playHeight / 2);
		cube.position.y = -0.8;
		cubes.push(cube);
		scene.add(cube);
	}
  
	return cubes;
}

export function degToRad(deg){
	return (deg * Math.PI / 180)
}

export function easeOutCirc(number){
	return Math.sqrt(1 - Math.pow(number - 1, 2));
}

export function easeInOutQuad(number){
	return number < 0.5 ? 2 * number * number : 1 - Math.pow(-2 * number + 2, 2) / 2;
}