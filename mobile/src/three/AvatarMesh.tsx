import React from "react";

import type { AvatarMetrics } from "./avatarScaling";

/**
 * A lightweight parametric humanoid built from primitives, scaled to the user's
 * measurements. It gives the garment something to drape on and conveys the
 * custom-dimension fit without needing a rigged character model.
 *
 * Coordinate convention: feet at y = 0, model grows upward.
 */
export function AvatarMesh({ metrics }: { metrics: AvatarMetrics }) {
  const {
    height,
    shoulderWidth,
    hipWidth,
    chestDepth,
    legLength,
    armLength,
    headRadius,
  } = metrics;

  const torsoHeight = height - legLength - headRadius * 2;
  const torsoCenterY = legLength + torsoHeight / 2;
  const skin = "#C9A07A";

  return (
    <group>
      {/* Head */}
      <mesh position={[0, legLength + torsoHeight + headRadius, 0]} castShadow>
        <sphereGeometry args={[headRadius, 24, 24]} />
        <meshStandardMaterial color={skin} roughness={0.8} />
      </mesh>

      {/* Torso (tapered box approximated by a scaled cylinder) */}
      <mesh position={[0, torsoCenterY, 0]} castShadow>
        <cylinderGeometry
          args={[shoulderWidth * 0.55, hipWidth * 0.9, torsoHeight, 24]}
        />
        <meshStandardMaterial color={skin} roughness={0.8} />
      </mesh>

      {/* Hips */}
      <mesh position={[0, legLength, 0]} castShadow>
        <sphereGeometry args={[hipWidth * 0.9, 20, 16]} />
        <meshStandardMaterial color={skin} roughness={0.8} />
      </mesh>

      {/* Arms */}
      {([-1, 1] as const).map((side) => (
        <mesh
          key={`arm-${side}`}
          position={[side * (shoulderWidth * 0.6), torsoCenterY + torsoHeight * 0.25 - armLength / 2, 0]}
          rotation={[0, 0, side * 0.08]}
          castShadow
        >
          <cylinderGeometry args={[chestDepth * 0.35, chestDepth * 0.3, armLength, 16]} />
          <meshStandardMaterial color={skin} roughness={0.8} />
        </mesh>
      ))}

      {/* Legs */}
      {([-1, 1] as const).map((side) => (
        <mesh
          key={`leg-${side}`}
          position={[side * (hipWidth * 0.45), legLength / 2, 0]}
          castShadow
        >
          <cylinderGeometry args={[hipWidth * 0.42, hipWidth * 0.32, legLength, 16]} />
          <meshStandardMaterial color={skin} roughness={0.8} />
        </mesh>
      ))}
    </group>
  );
}
