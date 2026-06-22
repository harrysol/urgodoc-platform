import type { UserDimensions } from "../api/types";

/**
 * Body metrics in metres used to build the parametric avatar. Derived from the
 * user's calibrated measurements, with sensible adult defaults when a given
 * measurement is missing.
 */
export interface AvatarMetrics {
  height: number;
  shoulderWidth: number;
  hipWidth: number;
  chestDepth: number;
  legLength: number;
  armLength: number;
  headRadius: number;
}

const cm = (v: number | null | undefined, fallback: number) =>
  v && v > 0 ? v / 100 : fallback;

export function deriveAvatarMetrics(d: UserDimensions | null): AvatarMetrics {
  const height = cm(d?.height_cm, 1.7);

  // Fall back to anthropometric ratios of total height where a measurement is
  // absent (e.g. shoulder ≈ 0.23·height, inseam ≈ 0.45·height).
  const shoulderWidth = cm(d?.shoulder_cm, height * 0.23);
  const hipWidth = cm(d?.hips_cm ? d.hips_cm / Math.PI : null, shoulderWidth * 0.85);
  const chestDepth = cm(d?.chest_cm ? d.chest_cm / Math.PI / 2 : null, 0.13);
  const legLength = cm(d?.inseam_cm, height * 0.45);
  const armLength = cm(d?.arm_length_cm, height * 0.33);

  return {
    height,
    shoulderWidth: Math.max(shoulderWidth, 0.28),
    hipWidth: Math.max(hipWidth, 0.16),
    chestDepth: Math.max(chestDepth, 0.1),
    legLength: Math.max(legLength, 0.6),
    armLength: Math.max(armLength, 0.45),
    headRadius: height * 0.07,
  };
}
