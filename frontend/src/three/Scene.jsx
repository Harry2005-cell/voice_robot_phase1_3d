import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Grid, PerspectiveCamera, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

const Robot = ({ command }) => {
  const robotRef = useRef();
  const [targetPosition, setTargetPosition] = useState(new THREE.Vector3(0, 0.5, 0));
  const [targetRotation, setTargetRotation] = useState(0);

  useEffect(() => {
    if (!command || command.type !== 'locomotion') return;

    const step = 2;
    const angleStep = Math.PI / 2;
    const action = (command.action || "").toLowerCase();

    // Safely update position so React triggers a re-render
    setTargetPosition(prev => {
      const newPos = prev.clone();
      if (action.includes('forward')) newPos.z -= step;
      if (action.includes('backward') || action.includes('back')) newPos.z += step;
      return newPos;
    });
    
    // Safely update rotation
    setTargetRotation(prev => {
      if (action.includes('left')) return prev + angleStep;
      if (action.includes('right')) return prev - angleStep;
      return prev;
    });

  }, [command]);

  useFrame(() => {
    if (robotRef.current) {
      // Smoothly animate the robot to the new targets
      robotRef.current.position.lerp(targetPosition, 0.1);
      robotRef.current.rotation.y = THREE.MathUtils.lerp(robotRef.current.rotation.y, targetRotation, 0.1);
    }
  });

  return (
    <mesh ref={robotRef} position={[0, 0.5, 0]} castShadow>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#3b82f6" />
    </mesh>
  );
};

export default function RobotScene({ lastCommand }) {
  return (
    <div style={{ height: '500px', width: '100%', borderRadius: '8px', overflow: 'hidden', background: '#1e1e1e' }}>
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[5, 5, 5]} />
        
        {/* Allows you to click and drag the camera with your mouse */}
        <OrbitControls target={[0, 0, 0]} /> 
        
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} castShadow intensity={1} />
        
        <Robot command={lastCommand} />
        
        <Grid args={[20, 20]} sectionColor="#ffffff" cellColor="#444444" position={[0, -0.01, 0]} />
        <axesHelper args={[5]} />
      </Canvas>
    </div>
  );
}