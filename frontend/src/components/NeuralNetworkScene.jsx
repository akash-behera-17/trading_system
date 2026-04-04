import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, MeshDistortMaterial } from '@react-three/drei';
import * as THREE from 'three';

// ─── Glowing node (neuron) ───────────────────────────────────────
function Neuron({ position, color, speed, distort, size }) {
    const ref = useRef();
    useFrame((state) => {
        const t = state.clock.elapsedTime * speed;
        ref.current.position.y = position[1] + Math.sin(t) * 0.15;
        ref.current.position.x = position[0] + Math.cos(t * 0.7) * 0.08;
    });
    return (
        <mesh ref={ref} position={position}>
            <sphereGeometry args={[size, 32, 32]} />
            <MeshDistortMaterial
                color={color}
                emissive={color}
                emissiveIntensity={0.6}
                roughness={0.2}
                metalness={0.8}
                distort={distort}
                speed={2}
                transparent
                opacity={0.85}
            />
        </mesh>
    );
}

// ─── Animated edge (synapse) between two nodes ───────────────────
function Synapse({ start, end, color, pulseSpeed }) {
    const ref = useRef();
    const dotRef = useRef();

    const curve = useMemo(() => {
        const mid = [
            (start[0] + end[0]) / 2 + (Math.random() - 0.5) * 0.5,
            (start[1] + end[1]) / 2 + (Math.random() - 0.5) * 0.3,
            (start[2] + end[2]) / 2 + (Math.random() - 0.5) * 0.4,
        ];
        return new THREE.QuadraticBezierCurve3(
            new THREE.Vector3(...start),
            new THREE.Vector3(...mid),
            new THREE.Vector3(...end)
        );
    }, [start, end]);

    const points = useMemo(() => curve.getPoints(40), [curve]);
    const geometry = useMemo(() => new THREE.BufferGeometry().setFromPoints(points), [points]);

    // Pulse dot along the synapse
    useFrame((state) => {
        if (dotRef.current) {
            const t = ((state.clock.elapsedTime * pulseSpeed) % 1);
            const pos = curve.getPoint(t);
            dotRef.current.position.copy(pos);
        }
    });

    return (
        <group>
            <line ref={ref} geometry={geometry}>
                <lineBasicMaterial color={color} transparent opacity={0.15} />
            </line>
            {/* Pulse dot */}
            <mesh ref={dotRef}>
                <sphereGeometry args={[0.03, 12, 12]} />
                <meshBasicMaterial color={color} transparent opacity={0.9} />
            </mesh>
        </group>
    );
}

// ─── Central brain orb ──────────────────────────────────────────
function CentralOrb() {
    const ref = useRef();
    useFrame((state) => {
        ref.current.rotation.y = state.clock.elapsedTime * 0.15;
        ref.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.1;
    });
    return (
        <Float speed={1.5} rotationIntensity={0.4} floatIntensity={0.6}>
            <mesh ref={ref} scale={1}>
                <icosahedronGeometry args={[0.7, 4]} />
                <MeshDistortMaterial
                    color="#6366f1"
                    emissive="#4f46e5"
                    emissiveIntensity={0.5}
                    roughness={0.15}
                    metalness={1}
                    distort={0.35}
                    speed={3}
                    transparent
                    opacity={0.7}
                    wireframe
                />
            </mesh>
        </Float>
    );
}

// ─── Orbiting ring ──────────────────────────────────────────────
function OrbitRing({ radius, speed, tilt, color }) {
    const ref = useRef();
    useFrame((state) => {
        ref.current.rotation.z = state.clock.elapsedTime * speed;
    });
    return (
        <mesh ref={ref} rotation={[tilt, 0, 0]}>
            <torusGeometry args={[radius, 0.008, 16, 100]} />
            <meshBasicMaterial color={color} transparent opacity={0.25} />
        </mesh>
    );
}

// ─── Particle field ─────────────────────────────────────────────
function ParticleField({ count = 200 }) {
    const ref = useRef();
    const positions = useMemo(() => {
        const arr = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            arr[i * 3] = (Math.random() - 0.5) * 8;
            arr[i * 3 + 1] = (Math.random() - 0.5) * 8;
            arr[i * 3 + 2] = (Math.random() - 0.5) * 8;
        }
        return arr;
    }, [count]);

    useFrame((state) => {
        ref.current.rotation.y = state.clock.elapsedTime * 0.02;
        ref.current.rotation.x = state.clock.elapsedTime * 0.01;
    });

    return (
        <points ref={ref}>
            <bufferGeometry>
                <bufferAttribute
                    attach="attributes-position"
                    array={positions}
                    count={count}
                    itemSize={3}
                />
            </bufferGeometry>
            <pointsMaterial size={0.015} color="#6366f1" transparent opacity={0.4} sizeAttenuation />
        </points>
    );
}

// ─── Full scene ─────────────────────────────────────────────────
function Scene() {
    const neurons = useMemo(() => [
        { pos: [-1.8, 1.0, 0.3], color: '#818cf8', speed: 0.8, distort: 0.3, size: 0.12 },
        { pos: [1.5, 1.2, -0.4], color: '#a78bfa', speed: 1.0, distort: 0.25, size: 0.1 },
        { pos: [-1.2, -0.8, 0.6], color: '#6366f1', speed: 0.6, distort: 0.35, size: 0.14 },
        { pos: [1.8, -0.6, -0.2], color: '#c084fc', speed: 0.9, distort: 0.2, size: 0.11 },
        { pos: [-0.5, 1.6, -0.3], color: '#818cf8', speed: 1.1, distort: 0.28, size: 0.09 },
        { pos: [0.6, -1.4, 0.5], color: '#a78bfa', speed: 0.7, distort: 0.32, size: 0.13 },
        { pos: [-1.9, -0.1, -0.5], color: '#6366f1', speed: 0.5, distort: 0.2, size: 0.08 },
        { pos: [2.0, 0.4, 0.4], color: '#c084fc', speed: 1.2, distort: 0.3, size: 0.10 },
    ], []);

    const synapses = useMemo(() => [
        { start: neurons[0].pos, end: [0, 0, 0], color: '#818cf8', pulse: 0.4 },
        { start: neurons[1].pos, end: [0, 0, 0], color: '#a78bfa', pulse: 0.5 },
        { start: neurons[2].pos, end: [0, 0, 0], color: '#6366f1', pulse: 0.35 },
        { start: neurons[3].pos, end: [0, 0, 0], color: '#c084fc', pulse: 0.45 },
        { start: neurons[4].pos, end: [0, 0, 0], color: '#818cf8', pulse: 0.55 },
        { start: neurons[5].pos, end: [0, 0, 0], color: '#a78bfa', pulse: 0.3 },
        { start: neurons[6].pos, end: [0, 0, 0], color: '#6366f1', pulse: 0.6 },
        { start: neurons[7].pos, end: [0, 0, 0], color: '#c084fc', pulse: 0.38 },
        // Cross-connections
        { start: neurons[0].pos, end: neurons[3].pos, color: '#4f46e5', pulse: 0.25 },
        { start: neurons[1].pos, end: neurons[5].pos, color: '#4f46e5', pulse: 0.3 },
        { start: neurons[2].pos, end: neurons[7].pos, color: '#4f46e5', pulse: 0.35 },
        { start: neurons[4].pos, end: neurons[6].pos, color: '#4f46e5', pulse: 0.28 },
    ], [neurons]);

    return (
        <>
            <ambientLight intensity={0.3} />
            <pointLight position={[3, 3, 3]} intensity={0.8} color="#6366f1" />
            <pointLight position={[-3, -2, 2]} intensity={0.4} color="#a78bfa" />
            <pointLight position={[0, 0, 4]} intensity={0.3} color="#818cf8" />

            <CentralOrb />

            <OrbitRing radius={1.2} speed={0.3} tilt={Math.PI / 5} color="#6366f1" />
            <OrbitRing radius={1.6} speed={-0.2} tilt={Math.PI / 3} color="#a78bfa" />
            <OrbitRing radius={2.1} speed={0.15} tilt={Math.PI / 7} color="#818cf8" />

            {neurons.map((n, i) => (
                <Neuron key={i} position={n.pos} color={n.color} speed={n.speed} distort={n.distort} size={n.size} />
            ))}

            {synapses.map((s, i) => (
                <Synapse key={i} start={s.start} end={s.end} color={s.color} pulseSpeed={s.pulse} />
            ))}

            <ParticleField count={300} />
        </>
    );
}

// ─── Exported component ─────────────────────────────────────────
export default function NeuralNetworkScene() {
    return (
        <div style={{
            position: 'absolute',
            inset: 0,
            zIndex: 0,
            pointerEvents: 'none',
        }}>
            <Canvas
                camera={{ position: [0, 0, 4.5], fov: 50 }}
                style={{ background: 'transparent' }}
                dpr={[1, 1.5]}
                gl={{ antialias: true, alpha: true }}
            >
                <Scene />
            </Canvas>
        </div>
    );
}
