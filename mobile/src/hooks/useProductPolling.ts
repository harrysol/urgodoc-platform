import { useEffect, useRef, useState } from "react";

import { api } from "../api/client";
import type { ProductDetail } from "../api/types";
import { POLL_INTERVAL_MS } from "../config";

const TERMINAL_STATES = new Set(["COMPLETED", "FAILED"]);

/**
 * Polls a product job until it reaches a terminal state (COMPLETED / FAILED).
 * Returns the latest snapshot plus any transport error.
 */
export function useProductPolling(productId: string | null) {
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!productId) return;
    let cancelled = false;

    const tick = async () => {
      try {
        const next = await api.getProduct(productId);
        if (cancelled) return;
        setProduct(next);
        setError(null);
        if (!TERMINAL_STATES.has(next.status)) {
          timer.current = setTimeout(tick, POLL_INTERVAL_MS);
        }
      } catch (e) {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : "Network error");
        // Keep retrying transient failures.
        timer.current = setTimeout(tick, POLL_INTERVAL_MS);
      }
    };

    tick();
    return () => {
      cancelled = true;
      if (timer.current) clearTimeout(timer.current);
    };
  }, [productId]);

  return { product, error };
}
