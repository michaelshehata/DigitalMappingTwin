import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'

interface LogoModelProps {
  url: string;
}

function LogoModel({ url }: LogoModelProps) {
  const meshRef = useRef<THREE.Group>(null)
  const { scene } = useGLTF(url)

  // Rotate the logo continuously
  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.02 // Rotation speed
    }
  })

  return <primitive ref={meshRef} object={scene} scale={1.5} />; {/* Increased scale */}
}

function Logo3D() {
  return (
    <div className="logo-3d-container">
      <Canvas camera={{ position: [0, 0, 3], fov: 50 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <pointLight position={[-5, -5, -5]} intensity={0.5} />
        <LogoModel url="/logo.glb" />
      </Canvas>
    </div>
  )
}

export default Logo3D