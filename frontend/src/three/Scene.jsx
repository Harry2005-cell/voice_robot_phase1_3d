import React, { useRef, useEffect, useState, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Grid, PerspectiveCamera, OrbitControls, useGLTF, useAnimations } from '@react-three/drei'; 
import * as THREE from 'three';

const Robot = ({ command }) => {
  const robotRef = useRef();
  
  // 1. Load the 3D GLTF model and animations from public/robot.glb
  const { scene, animations } = useGLTF('/robot.glb'); 
  const { actions, names } = useAnimations(animations, robotRef);
  
  const targetPos = useRef(new THREE.Vector3(0, 0, 0)); 
  const targetRot = useRef(0);
  
  // State to track movement status
  const [isMoving, setIsMoving] = useState(false);

  useEffect(() => {
    if (names && names.length > 0) {
      console.log("Available 3D Animations:", names);
    }
    
    if (!command || command.type !== 'locomotion') return;

    const step = 2;
    const angleStep = Math.PI / 2;
    const action = (command.action || "").toLowerCase();

    if (action.includes('forward') || action.includes('front') || action.includes('ahead') || action.includes('straight')) {
      targetPos.current.z -= step;
    }
    if (action.includes('backward') || action.includes('back') || action.includes('reverse')) {
      targetPos.current.z += step;
    }
    if (action.includes('left')) {
      targetRot.current += angleStep;
    }
    if (action.includes('right')) {
      targetRot.current -= angleStep;
    }

    // Trigger movement state
    setIsMoving(true);
    
    // Reset movement state after 1.5s
    const timer = setTimeout(() => {
      setIsMoving(false);
    }, 1500);

    return () => clearTimeout(timer);

  }, [command, names]);

  // 2. Play or stop the walking/movement animation dynamically
  useEffect(() => {
    if (!names || names.length === 0 || !actions) return;

    const walkAnimationName = names.find(n => n.toLowerCase().includes('walk') || n.toLowerCase().includes('run')) || names[0]; 
    
    if (!walkAnimationName || !actions[walkAnimationName]) return;

    if (isMoving) {
      actions[walkAnimationName].reset().fadeIn(0.2).play();
    } else {
      actions[walkAnimationName].fadeOut(0.2);
    }
  }, [isMoving, actions, names]);

  useFrame(() => {
    if (robotRef.current) {
      robotRef.current.position.lerp(targetPos.current, 0.05);
      robotRef.current.rotation.y = THREE.MathUtils.lerp(robotRef.current.rotation.y, targetRot.current, 0.1);
    }
  });

  return (
    <primitive ref={robotRef} object={scene} scale={1.5} position={[0, 0, 0]} castShadow />
  );
};

// Fallback visual box while 3D GLTF model is loading
const FallbackBox = () => (
  <mesh position={[0, 0.5, 0]}>
    <boxGeometry args={[1, 1, 1]} />
    <meshStandardMaterial color="#00f3ff" wireframe />
  </mesh>
);

export default function RobotScene({ lastCommand }) {
  return (
    <div style={{ height: '500px', width: '100%', borderRadius: '8px', overflow: 'hidden', background: '#121212' }}>
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[5, 5, 5]} />
        <OrbitControls target={[0, 0, 0]} /> 
        
        <ambientLight intensity={0.8} />
        <directionalLight position={[10, 10, 5]} castShadow intensity={1.2} />
        
        <Suspense fallback={<FallbackBox />}>
          <Robot command={lastCommand} />
        </Suspense>
        
        <Grid args={[20, 20]} sectionColor="#00f3ff" cellColor="#333333" position={[0, -0.01, 0]} />
        <axesHelper args={[5]} />
      </Canvas>
    </div>
  );
}