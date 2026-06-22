import { Canvas, useFrame } from "@react-three/fiber/native";
import React, { Suspense, useRef } from "react";
import { PanResponder, View } from "react-native";

import type { UserDimensions } from "../api/types";
import { AvatarMesh } from "./AvatarMesh";
import { GarmentModel } from "./GarmentModel";
import { deriveAvatarMetrics } from "./avatarScaling";

/**
 * Interactive 3D try-on view: a parametric avatar (sized to the user's
 * measurements) wearing the generated garment. Drag horizontally to rotate;
 * it slowly auto-rotates when idle.
 */
export function Avatar3D({
  modelUrl,
  dimensions,
}: {
  modelUrl: string | null;
  dimensions: UserDimensions | null;
}) {
  const metrics = deriveAvatarMetrics(dimensions);

  // rotation.current is the live yaw; startRotation snapshots it at drag start.
  const rotation = useRef(0);
  const startRotation = useRef(0);
  const dragging = useRef(false);

  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: () => true,
      onPanResponderGrant: () => {
        dragging.current = true;
        startRotation.current = rotation.current;
      },
      onPanResponderMove: (_evt, gesture) => {
        rotation.current = startRotation.current + gesture.dx * 0.01;
      },
      onPanResponderRelease: () => {
        dragging.current = false;
      },
      onPanResponderTerminate: () => {
        dragging.current = false;
      },
    }),
  ).current;

  return (
    <View className="flex-1" {...panResponder.panHandlers}>
      <Canvas
        shadows
        camera={{ position: [0, metrics.height * 0.6, 3.2], fov: 45 }}
      >
        <color attach="background" args={["#0B0B12"]} />
        <ambientLight intensity={0.9} />
        <directionalLight position={[3, 6, 4]} intensity={1.3} castShadow />
        <directionalLight position={[-4, 2, -2]} intensity={0.4} />

        <SceneContent
          rotationRef={rotation}
          draggingRef={dragging}
          metricsHeight={metrics.height}
        >
          <AvatarMesh metrics={metrics} />
          {modelUrl ? (
            <Suspense fallback={null}>
              <GarmentModel url={modelUrl} metrics={metrics} />
            </Suspense>
          ) : null}
        </SceneContent>
      </Canvas>
    </View>
  );
}

/**
 * Wraps the scene in a group whose yaw is driven imperatively each frame, so
 * dragging doesn't trigger React re-renders.
 */
function SceneContent({
  rotationRef,
  draggingRef,
  metricsHeight,
  children,
}: {
  rotationRef: React.MutableRefObject<number>;
  draggingRef: React.MutableRefObject<boolean>;
  metricsHeight: number;
  children: React.ReactNode;
}) {
  const groupRef = useRef<any>(null);

  useFrame((_state, delta) => {
    if (!draggingRef.current) {
      rotationRef.current += delta * 0.4; // gentle idle spin
    }
    if (groupRef.current) {
      groupRef.current.rotation.y = rotationRef.current;
    }
  });

  // Lower the group so the avatar is vertically centred in view.
  return (
    <group ref={groupRef} position={[0, -metricsHeight * 0.45, 0]}>
      {children}
    </group>
  );
}
