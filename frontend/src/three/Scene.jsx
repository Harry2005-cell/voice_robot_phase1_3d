import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Grid, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';

const Robot = ({ command }) => {
  const robotRef = useRef();
  const [targetPosition, setTargetPosition] = useState(new THREE.Vector3(0, 0.5, 0));
  const [targetRotation, setTargetRotation] = useState(0);

  useEffect(() => {
    if (!command || command.type !== 'locomotion') return;

    const step = 2;
    const angleStep = Math.PI / 2;

    // We can mutate targetPosition properties because it is an object (Vector3)
    if (command.action === 'forward') targetPosition.z -= step;
    if (command.action === 'backward') targetPosition.z += step;
    
    // We MUST use the setter for targetRotation because it is a primitive number
    if (command.action === 'left') setTargetRotation(prev => prev + angleStep);
    if (command.action === 'right') setTargetRotation(prev => prev - angleStep);
    
    setTargetPosition(targetPosition.clone());
  }, [command, targetPosition]);

  useFrame((state, delta) => {
    // Smooth interpolation for movement (Kinematics)
    robotRef.current.position.lerp(targetPosition, 0.1);
    robotRef.current.rotation.y = THREE.MathUtils.lerp(robotRef.current.rotation.y, targetRotation, 0.1);
  });

  return (
    <mesh ref={robotRef} position={[0, 0.5, 0]} castShadow>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="royalblue" />
    </mesh>
  );
};

export default function RobotScene({ lastCommand }) {
  return (
    <div style={{ height: '500px', width: '100%', background: '#202020' }}>
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[5, 5, 5]} />
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} castShadow intensity={1} />
        
        <Robot command={lastCommand} />
        
        <Grid args={[20, 20]} sectionColor="white" cellColor="#666" position={[0, -0.01, 0]} />
        <axesHelper args={[5]} />
      </Canvas>
    </div>
  );
}