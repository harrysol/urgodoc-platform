import { useGLTF } from "@react-three/drei/native";
import React, { useLayoutEffect, useMemo } from "react";
import { Box3, Vector3 } from "three";

import type { AvatarMetrics } from "./avatarScaling";

/**
 * Loads the Tripo3D-generated .glb and auto-fits it onto the avatar's torso.
 *
 * The garment is uniformly scaled so its height matches roughly the avatar's
 * upper-body span, then re-centred on the chest. This keeps any garment —
 * regardless of how Tripo3D scaled/oriented the mesh — sensibly placed.
 */
export function GarmentModel({
  url,
  metrics,
}: {
  url: string;
  metrics: AvatarMetrics;
}) {
  const { scene } = useGLTF(url);

  // Clone so the cached GLTF scene isn't mutated across mounts.
  const model = useMemo(() => scene.clone(true), [scene]);

  const { scale, position } = useMemo(() => {
    const box = new Box3().setFromObject(model);
    const size = new Vector3();
    const center = new Vector3();
    box.getSize(size);
    box.getCenter(center);

    // Target: garment spans the torso (~40% of total height).
    const targetHeight = metrics.height * 0.42;
    const s = size.y > 0 ? targetHeight / size.y : 1;

    const torsoCenterY = metrics.legLength + (metrics.height - metrics.legLength) * 0.5;

    return {
      scale: s,
      position: [
        -center.x * s,
        torsoCenterY - center.y * s,
        -center.z * s + metrics.chestDepth * 0.2,
      ] as [number, number, number],
    };
  }, [model, metrics]);

  useLayoutEffect(() => {
    model.traverse((obj) => {
      // Ensure consistent shading regardless of exported material flags.
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const mesh = obj as any;
      if (mesh.isMesh) {
        mesh.castShadow = true;
        mesh.frustumCulled = false;
      }
    });
  }, [model]);

  return <primitive object={model} scale={scale} position={position} />;
}
