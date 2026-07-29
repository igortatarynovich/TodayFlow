/**
 * Natal wheel planet layout — aggressive collision avoidance for stelliums.
 * Radial spiral + angular fan; leader marks true longitude on the planet belt.
 */

export type NatalPlanetLayoutInput = {
  angle: number; // SVG paint angle (deg)
};

export type NatalPlanetLayoutResult = {
  radius: number;
  paintAngle: number;
  trueAngle: number;
  radiusOffset: number;
  angleOffset: number;
  leader: boolean;
  /** Optional visual shrink for ultra-dense clusters (1 = full disc). */
  discScale: number;
};

function angDist(a: number, b: number): number {
  return Math.abs(((a - b + 540) % 360) - 180);
}

function polar(angleDeg: number, radius: number): { x: number; y: number } {
  const rad = (angleDeg * Math.PI) / 180;
  return { x: radius * Math.cos(rad), y: radius * Math.sin(rad) };
}

function buildClusters(angles: number[], thresholdDeg: number): number[][] {
  const n = angles.length;
  if (n === 0) return [];
  const order = Array.from({ length: n }, (_, i) => i).sort((i, j) => angles[i] - angles[j]);
  const assigned = new Array(n).fill(false);
  const clusters: number[][] = [];

  for (let s = 0; s < order.length; s += 1) {
    const startIdx = order[s];
    if (assigned[startIdx]) continue;
    const cluster = [startIdx];
    assigned[startIdx] = true;
    let end = s;
    while (end + 1 < order.length) {
      const a = order[end];
      const b = order[end + 1];
      if (angDist(angles[a], angles[b]) < thresholdDeg) {
        end += 1;
        cluster.push(order[end]);
        assigned[order[end]] = true;
      } else break;
    }
    clusters.push(cluster);
  }

  if (clusters.length >= 2) {
    const first = clusters[0];
    const last = clusters[clusters.length - 1];
    if (angDist(angles[first[0]], angles[last[last.length - 1]]) < thresholdDeg) {
      clusters[0] = [...last, ...first];
      clusters.pop();
    }
  }

  return clusters;
}

/**
 * Place planets so discs do not pile up in stelliums.
 * Uses full radius band + spiral order (outer/inner alternate) + fan until clear.
 */
export function resolveNatalPlanetLayout(
  planets: NatalPlanetLayoutInput[],
  opts: {
    baseRadius: number;
    minRadius: number;
    maxRadius: number;
    discRadius: number;
    gap?: number;
    iterations?: number;
  },
): NatalPlanetLayoutResult[] {
  const n = planets.length;
  if (n === 0) return [];

  const gap = opts.gap ?? 8;
  const minDist = opts.discRadius * 2 + gap;
  const iterations = opts.iterations ?? 24;
  const { baseRadius, minRadius, maxRadius } = opts;
  const band = Math.max(28, maxRadius - minRadius);

  const items = planets.map((p) => ({
    trueAngle: p.angle,
    paintAngle: p.angle,
    radius: baseRadius,
  }));

  // Wide cluster window — Capricorn-style piles often span 15–25°.
  const threshold = Math.max(20, ((minDist * 1.2) / Math.max(baseRadius, 1)) * (180 / Math.PI) + 5);
  const clusters = buildClusters(
    items.map((it) => it.trueAngle),
    threshold,
  );

  for (const cluster of clusters) {
    const size = cluster.length;
    if (size === 1) {
      items[cluster[0]].radius = baseRadius;
      items[cluster[0]].paintAngle = items[cluster[0]].trueAngle;
      continue;
    }

    const sorted = [...cluster].sort((i, j) => items[i].trueAngle - items[j].trueAngle);

    // Alternate outer / inner so angular neighbors differ strongly in radius.
    // For 3+ bodies also stagger mid-band so we use the full radial depth.
    const needChord = minDist * 0.98;
    const stepFan = Math.min(18, Math.max(5.5, (needChord / Math.max(baseRadius, 1)) * (180 / Math.PI) * 1.25));

    for (let k = 0; k < size; k += 1) {
      const idx = sorted[k];
      const t = size <= 1 ? 0 : k / (size - 1);
      // Spiral: outer → mid → inner → outer… across the cluster order.
      const ringPhase = (k % 3) / 2; // 0, 0.5, 1
      const spiral = 1 - ringPhase;
      items[idx].radius = minRadius + spiral * band * (0.88 - t * 0.12);
      // Keep first/last of dense piles near opposite band edges.
      if (k === 0) items[idx].radius = maxRadius;
      if (k === size - 1) items[idx].radius = minRadius;
      if (k === 1 && size >= 4) items[idx].radius = minRadius + band * 0.35;
      if (k === size - 2 && size >= 4) items[idx].radius = maxRadius - band * 0.28;

      const fan = (k - (size - 1) / 2) * stepFan;
      items[idx].paintAngle = (items[idx].trueAngle + fan + 360) % 360;
    }
  }

  for (let iter = 0; iter < iterations; iter += 1) {
    const pushA = new Array(n).fill(0);
    const pushR = new Array(n).fill(0);

    for (let i = 0; i < n; i += 1) {
      for (let j = i + 1; j < n; j += 1) {
        const a = items[i];
        const b = items[j];
        const pa = polar(a.paintAngle, a.radius);
        const pb = polar(b.paintAngle, b.radius);
        const dist = Math.hypot(pa.x - pb.x, pa.y - pb.y) || 0.001;
        if (dist >= minDist) continue;

        const overlap = minDist - dist;
        const step = overlap * (0.78 + iter * 0.03);
        const preferOutI = a.radius <= b.radius ? 1 : -1;
        pushR[i] += preferOutI * step * 0.9;
        pushR[j] -= preferOutI * step * 0.9;

        const angPush = ((step * 0.62) / Math.max(a.radius, 40)) * (180 / Math.PI);
        let order = ((a.trueAngle - b.trueAngle + 540) % 360) - 180;
        if (Math.abs(order) < 0.01) order = i < j ? 1 : -1;
        const sign = order > 0 ? 1 : -1;
        pushA[i] += sign * angPush;
        pushA[j] -= sign * angPush;
      }
    }

    for (let i = 0; i < n; i += 1) {
      items[i].radius = Math.min(maxRadius, Math.max(minRadius, items[i].radius + pushR[i]));
      const nextA = items[i].paintAngle + pushA[i];
      const delta = ((nextA - items[i].trueAngle + 540) % 360) - 180;
      const clamped = Math.max(-26, Math.min(26, delta));
      items[i].paintAngle = (items[i].trueAngle + clamped + 360) % 360;
    }
  }

  // If still colliding, shrink discs in the densest pairs (visual only).
  const discScale = new Array(n).fill(1);
  for (let i = 0; i < n; i += 1) {
    for (let j = i + 1; j < n; j += 1) {
      const pa = polar(items[i].paintAngle, items[i].radius);
      const pb = polar(items[j].paintAngle, items[j].radius);
      const dist = Math.hypot(pa.x - pb.x, pa.y - pb.y);
      if (dist < minDist * 0.92) {
        discScale[i] = Math.min(discScale[i], 0.78);
        discScale[j] = Math.min(discScale[j], 0.78);
      } else if (dist < minDist) {
        discScale[i] = Math.min(discScale[i], 0.9);
        discScale[j] = Math.min(discScale[j], 0.9);
      }
    }
  }

  return items.map((it, i) => {
    const radiusOffset = it.radius - baseRadius;
    const angleOffset = ((it.paintAngle - it.trueAngle + 540) % 360) - 180;
    const leader =
      Math.abs(radiusOffset) > opts.discRadius * 0.35 || Math.abs(angleOffset) > 1.2;
    return {
      radius: it.radius,
      paintAngle: it.paintAngle,
      trueAngle: it.trueAngle,
      radiusOffset,
      angleOffset,
      leader,
      discScale: discScale[i],
    };
  });
}

export function minPlanetDiscDistance(
  layout: Array<{ paintAngle: number; radius: number }>,
): number {
  let min = Infinity;
  for (let i = 0; i < layout.length; i += 1) {
    for (let j = i + 1; j < layout.length; j += 1) {
      const a = polar(layout[i].paintAngle, layout[i].radius);
      const b = polar(layout[j].paintAngle, layout[j].radius);
      min = Math.min(min, Math.hypot(a.x - b.x, a.y - b.y));
    }
  }
  return min === Infinity ? 0 : min;
}
