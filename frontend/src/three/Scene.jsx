import React, { useRef, useEffect, useState, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Grid, PerspectiveCamera, OrbitControls, useGLTF, useAnimations } from '@react-three/drei'; 
import * as THREE from 'three';

const Robot = ({ command }) => {
  const robotRef = useRef();
  
  // 1. Load 3D GLTF model and animations from public/robot.glb
  const { scene, animations } = useGLTF('/robot.glb'); 
  const { actions, names } = useAnimations(animations, robotRef);
  
  const targetPos = useRef(new THREE.Vector3(0, 0, 0)); 
  const targetRot = useRef(0);
  const jumpHeight = useRef(0);
  
  // State to track movement status
  const [isMoving, setIsMoving] = useState(false);

  useEffect(() => {
    if (!command || command.type !== 'locomotion') return;

    const step = 2;
    const angleStep = Math.PI / 2;
    const action = (command.action || "").toLowerCase();

    if (action.includes('forward') || action.includes('front') || action.includes('ahead') || action.includes('straight')) {
      targetPos.current.z -= step;
    } else if (action.includes('backward') || action.includes('back') || action.includes('reverse')) {
      targetPos.current.z += step;
    } else if (action.includes('left')) {
      targetRot.current += angleStep;
    } else if (action.includes('right')) {
      targetRot.current -= angleStep;
    } else if (action.includes('jump') || action.includes('hop')) {
      jumpHeight.current = 1.8;
      setTimeout(() => { jumpHeight.current = 0; }, 600);
    } else if (action.includes('spin') || action.includes('dance') || action.includes('twirl')) {
      targetRot.current += Math.PI * 2;
    } else if (action.includes('reset') || action.includes('center')) {
      targetPos.current.set(0, 0, 0);
      targetRot.current = 0;
      jumpHeight.current = 0;
    }

    // Trigger movement animation state
    setIsMoving(true);
    
    const timer = setTimeout(() => {
      setIsMoving(false);
    }, 1500);

    return () => clearTimeout(timer);

  }, [command]);

  // 2. Play or stop walking/running animation
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
      // Lerp X and Z coordinates
      robotRef.current.position.x = THREE.MathUtils.lerp(robotRef.current.position.x, targetPos.current.x, 0.05);
      robotRef.current.position.z = THREE.MathUtils.lerp(robotRef.current.position.z, targetPos.current.z, 0.05);
      
      // Lerp Y height for jumps
      robotRef.current.position.y = THREE.MathUtils.lerp(robotRef.current.position.y, jumpHeight.current, 0.15);
      
      // Lerp Y rotation
      robotRef.current.rotation.y = THREE.MathUtils.lerp(robotRef.current.rotation.y, targetRot.current, 0.1);
    }
  });

  return (
    <primitive ref={robotRef} object={scene} scale={1.5} position={[0, 0, 0]} castShadow />
  );
};

// Camera Controller Component for switching views dynamically
const CameraController = ({ viewMode }) => {
  const cameraRef = useRef();

  useEffect(() => {
    if (!cameraRef.current) return;
    if (viewMode === 'top') {
      cameraRef.current.position.set(0, 10, 0.01);
    } else if (viewMode === 'front') {
      cameraRef.current.position.set(0, 2, 7);
    } else {
      // Isometric view default
      cameraRef.current.position.set(5, 5, 5);
    }
  }, [viewMode]);

  return <PerspectiveCamera ref={cameraRef} makeDefault position={[5, 5, 5]} />;
};

// Fallback visual box while 3D GLTF model is loading
const FallbackBox = () => (
  <mesh position={[0, 0.5, 0]}>
    <boxGeometry args={[1, 1, 1]} />
    <meshStandardMaterial color="#00f3ff" wireframe />
  </mesh>
);

export default function RobotScene({ lastCommand, cameraView = 'isometric' }) {
  return (
    <div style={{ height: '500px', width: '100%', borderRadius: '8px', overflow: 'hidden', background: '#121212', position: 'relative' }}>
      <Canvas shadows>
        <CameraController viewMode={cameraView} />
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