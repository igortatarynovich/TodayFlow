"use client";

import { useEffect, useRef, type CSSProperties } from "react";
import styles from "./celestialMoon.module.css";

export type CelestialMoonProps = {
  /** 0 = new, 0.5 = full, 1 = new again (terminator travels east→west). */
  phase?: number;
  size?: number;
  /** Axial spin around the polar (Y) axis, rad/sec — globe turn, not flat “vinyl”. */
  spin?: number;
  /** Extra longitude offset in radians (libration). */
  longitude?: number;
  glow?: number;
  className?: string;
  /** Equirectangular lunar albedo. */
  textureSrc?: string;
  /**
   * Continuous rAF spin loop. When false (Today summary), draw on demand only —
   * phase still updates via props; cheaper on battery.
   */
  animated?: boolean;
  testId?: string;
};

/** NASA LRO equirect — needed for true axial spin (near-side photo cannot yaw). */
const DEFAULT_TEXTURE = "/images/celestial/moon_lro_2k.jpg";

const VERT = /* glsl */ `
  attribute vec3 aPosition;
  attribute vec2 aUv;
  attribute vec3 aNormal;
  uniform mat4 uMVP;
  uniform mat4 uMV;
  uniform mat3 uNormalMat;
  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vView;
  void main() {
    vUv = aUv;
    vNormal = normalize(uNormalMat * aNormal);
    vec4 viewPos = uMV * vec4(aPosition, 1.0);
    vView = viewPos.xyz;
    gl_Position = uMVP * vec4(aPosition, 1.0);
  }
`;

const FRAG = /* glsl */ `
  precision mediump float;
  uniform sampler2D uTex;
  uniform vec3 uLightDir;
  uniform float uGlow;
  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vView;

  void main() {
    vec3 N = normalize(vNormal);
    vec3 L = normalize(uLightDir);
    float ndl = dot(N, L);

    float lit = smoothstep(-0.12, 0.34, ndl);
    float penumbra = smoothstep(-0.34, 0.04, ndl);

    vec3 albedo = texture2D(uTex, vUv).rgb;
    albedo *= vec3(0.96, 0.98, 1.02);
    albedo = mix(albedo, sqrt(max(albedo, 0.0)), 0.18);

    /* UI floor: even near-new keeps maria readable (earthshine + soft fill). */
    float ambient = 0.1;
    float diffuse = lit * 0.9;
    float earthshine = (1.0 - penumbra) * 0.32;
    float shade = ambient + diffuse + earthshine;
    shade = max(shade, mix(0.26, 0.08, lit));

    vec3 V = normalize(-vView);
    float fresnel = pow(1.0 - max(dot(N, V), 0.0), 3.1);
    float rim = fresnel * (0.22 + 0.38 * lit) * uGlow;

    vec3 color = albedo * shade;
    color += vec3(0.86, 0.9, 1.0) * rim;

    vec3 H = normalize(L + V);
    color += vec3(pow(max(dot(N, H), 0.0), 64.0) * lit * 0.05);

    gl_FragColor = vec4(color, 1.0);
  }
`;

function compile(gl: WebGLRenderingContext, type: number, src: string): WebGLShader {
  const sh = gl.createShader(type);
  if (!sh) throw new Error("shader create failed");
  gl.shaderSource(sh, src);
  gl.compileShader(sh);
  if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
    const log = gl.getShaderInfoLog(sh) || "compile error";
    gl.deleteShader(sh);
    throw new Error(log);
  }
  return sh;
}

function link(gl: WebGLRenderingContext, vs: WebGLShader, fs: WebGLShader): WebGLProgram {
  const prog = gl.createProgram();
  if (!prog) throw new Error("program create failed");
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    const log = gl.getProgramInfoLog(prog) || "link error";
    gl.deleteProgram(prog);
    throw new Error(log);
  }
  return prog;
}

function buildSphere(seg = 72): {
  positions: Float32Array;
  uvs: Float32Array;
  normals: Float32Array;
  indices: Uint16Array;
} {
  const positions: number[] = [];
  const uvs: number[] = [];
  const normals: number[] = [];
  const indices: number[] = [];

  for (let y = 0; y <= seg; y++) {
    const v = y / seg;
    const theta = v * Math.PI;
    const sinT = Math.sin(theta);
    const cosT = Math.cos(theta);
    for (let x = 0; x <= seg; x++) {
      const u = x / seg;
      const phi = u * Math.PI * 2;
      const sinP = Math.sin(phi);
      const cosP = Math.cos(phi);
      const nx = -sinT * cosP;
      const ny = cosT;
      const nz = sinT * sinP;
      positions.push(nx, ny, nz);
      normals.push(nx, ny, nz);
      // Equirect: v=0 at north (texture top)
      uvs.push(u, v);
    }
  }

  for (let y = 0; y < seg; y++) {
    for (let x = 0; x < seg; x++) {
      const a = y * (seg + 1) + x;
      const b = a + seg + 1;
      indices.push(a, b, a + 1, b, b + 1, a + 1);
    }
  }

  return {
    positions: new Float32Array(positions),
    uvs: new Float32Array(uvs),
    normals: new Float32Array(normals),
    indices: new Uint16Array(indices),
  };
}

function phaseToLightDir(phase: number): [number, number, number] {
  // After view translate, camera-facing limb normals ≈ +Z.
  // phase 0 = new (−Z light), 0.5 = full (+Z light).
  const t = ((phase % 1) + 1) % 1;
  const angle = t * Math.PI * 2;
  const x = Math.sin(angle);
  const z = -Math.cos(angle);
  const y = 0.16;
  const len = Math.hypot(x, y, z) || 1;
  return [x / len, y / len, z / len];
}

function mat4Perspective(fovy: number, aspect: number, near: number, far: number): Float32Array {
  const f = 1 / Math.tan(fovy / 2);
  const nf = 1 / (near - far);
  const out = new Float32Array(16);
  out[0] = f / aspect;
  out[5] = f;
  out[10] = (far + near) * nf;
  out[11] = -1;
  out[14] = 2 * far * near * nf;
  return out;
}

function mat4Multiply(a: Float32Array, b: Float32Array): Float32Array {
  const o = new Float32Array(16);
  for (let c = 0; c < 4; c++) {
    for (let r = 0; r < 4; r++) {
      o[c * 4 + r] =
        a[r] * b[c * 4] + a[4 + r] * b[c * 4 + 1] + a[8 + r] * b[c * 4 + 2] + a[12 + r] * b[c * 4 + 3];
    }
  }
  return o;
}

function mat4Translate(tx: number, ty: number, tz: number): Float32Array {
  const o = new Float32Array(16);
  o[0] = o[5] = o[10] = o[15] = 1;
  o[12] = tx;
  o[13] = ty;
  o[14] = tz;
  return o;
}

function mat4RotateY(rad: number): Float32Array {
  const c = Math.cos(rad);
  const s = Math.sin(rad);
  const o = new Float32Array(16);
  o[0] = c;
  o[2] = -s;
  o[5] = 1;
  o[8] = s;
  o[10] = c;
  o[15] = 1;
  return o;
}

function mat3FromMat4(m: Float32Array): Float32Array {
  return new Float32Array([m[0], m[1], m[2], m[4], m[5], m[6], m[8], m[9], m[10]]);
}

/**
 * Lunar globe: equirect LRO map on a UV sphere.
 * Spin = yaw around the polar Y axis (true axial turn). Phase = light only.
 */
export function CelestialMoon({
  phase = 0.5,
  size = 320,
  spin = 0.035,
  longitude = 0,
  glow = 1,
  className,
  textureSrc = DEFAULT_TEXTURE,
  animated = true,
  testId = "celestial-moon",
}: CelestialMoonProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const phaseRef = useRef(phase);
  const glowRef = useRef(glow);
  const spinRef = useRef(spin);
  const lonRef = useRef(longitude);
  const drawRef = useRef<(() => void) | null>(null);

  phaseRef.current = phase;
  glowRef.current = glow;
  spinRef.current = spin;
  lonRef.current = longitude;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext("webgl", {
      alpha: true,
      antialias: true,
      premultipliedAlpha: true,
    });
    if (!gl) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const px = Math.round(size * dpr);
    canvas.width = px;
    canvas.height = px;
    gl.viewport(0, 0, px, px);

    let disposed = false;
    let raf = 0;
    let tex: WebGLTexture | null = null;

    const vs = compile(gl, gl.VERTEX_SHADER, VERT);
    const fs = compile(gl, gl.FRAGMENT_SHADER, FRAG);
    const prog = link(gl, vs, fs);
    gl.useProgram(prog);

    const sphere = buildSphere(animated ? 72 : 48);
    const bufPos = gl.createBuffer();
    const bufUv = gl.createBuffer();
    const bufN = gl.createBuffer();
    const bufIx = gl.createBuffer();

    const locPos = gl.getAttribLocation(prog, "aPosition");
    const locUv = gl.getAttribLocation(prog, "aUv");
    const locN = gl.getAttribLocation(prog, "aNormal");

    gl.bindBuffer(gl.ARRAY_BUFFER, bufPos);
    gl.bufferData(gl.ARRAY_BUFFER, sphere.positions, gl.STATIC_DRAW);
    gl.enableVertexAttribArray(locPos);
    gl.vertexAttribPointer(locPos, 3, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, bufUv);
    gl.bufferData(gl.ARRAY_BUFFER, sphere.uvs, gl.STATIC_DRAW);
    gl.enableVertexAttribArray(locUv);
    gl.vertexAttribPointer(locUv, 2, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, bufN);
    gl.bufferData(gl.ARRAY_BUFFER, sphere.normals, gl.STATIC_DRAW);
    gl.enableVertexAttribArray(locN);
    gl.vertexAttribPointer(locN, 3, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, bufIx);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, sphere.indices, gl.STATIC_DRAW);

    const uMVP = gl.getUniformLocation(prog, "uMVP");
    const uMV = gl.getUniformLocation(prog, "uMV");
    const uNormalMat = gl.getUniformLocation(prog, "uNormalMat");
    const uLightDir = gl.getUniformLocation(prog, "uLightDir");
    const uGlow = gl.getUniformLocation(prog, "uGlow");
    const uTex = gl.getUniformLocation(prog, "uTex");

    tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texImage2D(
      gl.TEXTURE_2D,
      0,
      gl.RGBA,
      1,
      1,
      0,
      gl.RGBA,
      gl.UNSIGNED_BYTE,
      new Uint8Array([160, 160, 168, 255])
    );
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);

    const proj = mat4Perspective((38 * Math.PI) / 180, 1, 0.1, 20);
    const view = mat4Translate(0, 0, -2.55);
    // Mesh +Z faces camera; equirect u=0.5 (near side) sits on +X → base −π/2.
    let yaw = -Math.PI * 0.5;
    let last = performance.now();
    const reduceMotion =
      typeof window.matchMedia === "function" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const loop = animated && !reduceMotion && spin !== 0;

    const draw = () => {
      if (disposed) return;
      const model = mat4RotateY(yaw + lonRef.current);
      const mv = mat4Multiply(view, model);
      const mvp = mat4Multiply(proj, mv);
      const nMat = mat3FromMat4(model);

      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      gl.useProgram(prog);
      gl.uniformMatrix4fv(uMVP, false, mvp);
      gl.uniformMatrix4fv(uMV, false, mv);
      gl.uniformMatrix3fv(uNormalMat, false, nMat);
      gl.uniform3fv(uLightDir, phaseToLightDir(phaseRef.current));
      gl.uniform1f(uGlow, glowRef.current);
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.uniform1i(uTex, 0);
      gl.drawElements(gl.TRIANGLES, sphere.indices.length, gl.UNSIGNED_SHORT, 0);
    };
    drawRef.current = draw;

    const img = new Image();
    img.decoding = "async";
    img.onload = () => {
      if (disposed || !tex) return;
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, 0);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.generateMipmap(gl.TEXTURE_2D);
      draw();
    };
    img.src = textureSrc;

    gl.enable(gl.DEPTH_TEST);
    gl.enable(gl.CULL_FACE);
    gl.cullFace(gl.BACK);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    gl.clearColor(0, 0, 0, 0);

    const frame = (now: number) => {
      if (disposed) return;
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      yaw += spinRef.current * dt;
      draw();
      raf = requestAnimationFrame(frame);
    };

    draw();
    if (loop) raf = requestAnimationFrame(frame);

    return () => {
      disposed = true;
      drawRef.current = null;
      cancelAnimationFrame(raf);
      if (tex) gl.deleteTexture(tex);
      gl.deleteProgram(prog);
      gl.deleteShader(vs);
      gl.deleteShader(fs);
      gl.deleteBuffer(bufPos);
      gl.deleteBuffer(bufUv);
      gl.deleteBuffer(bufN);
      gl.deleteBuffer(bufIx);
    };
  }, [size, textureSrc, animated, spin]);

  useEffect(() => {
    drawRef.current?.();
  }, [phase, glow, longitude]);

  return (
    <div
      className={[styles.wrap, className].filter(Boolean).join(" ")}
      style={
        {
          width: size,
          height: size,
          ["--moon-glow" as string]: String(glow),
        } as CSSProperties
      }
      data-testid={testId}
      aria-hidden
    >
      <div className={styles.bloom} />
      <div className={styles.halo} />
      <canvas ref={canvasRef} className={styles.canvas} style={{ width: size, height: size }} />
    </div>
  );
}
