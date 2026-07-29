/**
 * Natal wheel planet layout — collision avoidance for stelliums.
 * Prefer radial stagger + angular fan so discs clear; leader when offset from true ray.
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
  const order = [...angles.keys()].sort((i, j) => angles[i] - angles[j]);
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
    const a = angles[first[0]];
    const b = angles[last[last.length - 1]];
    if (angDist(a, b) < thresholdDeg) {
      clusters[0] = [...last, ...first];
      clusters.pop();
    }
  }

  return clusters;
}

function fanStepForClearance(minDist: number, radialStep: number, radius: number): number {
  const chordNeed = Math.sqrt(Math.max(0, minDist * minDist - radialStep * radialStep));
  const deg = (chordNeed / Math.max(radius, 1)) * (180 / Math.PI);
  return Math.min(12, Math.max(2.2, deg * 1.08));
}

/**
 * Place planets so discs do not pile up in stelliums.
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

  const gap = opts.gap ?? 5;
  const minDist = opts.discRadius * 2 + gap;
  const iterations = opts.iterations ?? 10;
  const { baseRadius, minRadius, maxRadius } = opts;

  const items = planets.map((p) => ({
    trueAngle: p.angle,
    paintAngle: p.angle,
    radius: baseRadius,
  }));

  const threshold = Math.max(13, ((minDist * 0.85) / Math.max(baseRadius, 1)) * (180 / Math.PI) + 3);
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

    const sorted = [...cluster].sort((i, j) => {
      // Order along short arc from median
      return items[i].trueAngle - items[j].trueAngle;
    });

    const radialStep = (maxRadius - minRadius) / Math.max(1, size - 1);
    const stepFan = fanStepForClearance(minDist, radialStep, baseRadius);

    for (let k = 0; k < size; k += 1) {
      const idx = sorted[k];
      items[idx].radius = minRadius + k * radialStep;
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
        const step = overlap * (0.6 + iter * 0.04);
        const preferOutI = a.radius <= b.radius ? 1 : -1;
        pushR[i] += preferOutI * step * 0.75;
        pushR[j] -= preferOutI * step * 0.75;

        const angPush = ((step * 0.45) / Math.max(a.radius, 40)) * (180 / Math.PI);
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
      const clamped = Math.max(-14, Math.min(14, delta));
      items[i].paintAngle = (items[i].trueAngle + clamped + 360) % 360;
    }
  }

  return items.map((it) => {
    const radiusOffset = it.radius - baseRadius;
    const angleOffset = ((it.paintAngle - it.trueAngle + 540) % 360) - 180;
    const leader =
      Math.abs(radiusOffset) > opts.discRadius * 0.4 || Math.abs(angleOffset) > 1.6;
    return {
      radius: it.radius,
      paintAngle: it.paintAngle,
      trueAngle: it.trueAngle,
      radiusOffset,
      angleOffset,
      leader,
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
