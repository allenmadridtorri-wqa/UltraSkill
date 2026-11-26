/**
 * UltraSkill Production Three.js Scene Bootstrap (`scene_bootstrap.js`).
 *
 * Features:
 *   1. Automatic hardware detection defaulting to the LOW preset on 4 GB RAM /
 *      1 GB Intel UHD integrated GPUs or software WebGL renderers.
 *   2. Dynamic preset switching (`applyQualityPreset("LOW" | "MEDIUM" | "HIGH")`)
 *      updating pixel ratio, internal resolution clamping, and shadow maps live.
 *   3. AgX / ACESFilmic tone mapping and sRGB output color space.
 *   4. Full recursive GPU memory disposal (`disposeHierarchy`) and context-loss survival.
 */

import * as THREE from "three";

export const QUALITY_PRESETS = {
  LOW: {
    maxRenderHeightPx: 720,
    maxPixelRatio: 1.0,
    antialias: false,
    shadowsEnabled: false,
    shadowMapSize: 0,
    maxDrawCalls: 50,
    onDemandRendering: true,
  },
  MEDIUM: {
    maxRenderHeightPx: 1080,
    maxPixelRatio: 1.5,
    antialias: true,
    shadowsEnabled: true,
    shadowMapSize: 1024,
    maxDrawCalls: 150,
    onDemandRendering: false,
  },
  HIGH: {
    maxRenderHeightPx: 2160,
    maxPixelRatio: 2.0,
    antialias: true,
    shadowsEnabled: true,
    shadowMapSize: 2048,
    maxDrawCalls: 350,
    onDemandRendering: false,
  },
};

export function detectHardwarePreset(gl) {
  const deviceMem = typeof navigator !== "undefined" ? navigator.deviceMemory || 4 : 4;
  let rendererName = "";
  if (gl) {
    const ext = gl.getExtension("WEBGL_debug_renderer_info");
    if (ext) {
      rendererName = String(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) || "");
    }
  }
  const isLowSpecGpu = /Intel|UHD|HD Graphics|Iris|SwiftShader|llvmpipe|Mesa|Software/i.test(
    rendererName
  );
  if (deviceMem <= 4 || isLowSpecGpu) {
    return "LOW";
  }
  if (/RTX|Radeon RX|Apple M[2-9]\s*(Pro|Max|Ultra)/i.test(rendererName)) {
    return "HIGH";
  }
  return "MEDIUM";
}

export function disposeHierarchy(rootObject) {
  if (!rootObject) return;
  rootObject.traverse((node) => {
    if (node.geometry && typeof node.geometry.dispose === "function") {
      node.geometry.dispose();
    }
    if (node.material) {
      const mats = Array.isArray(node.material) ? node.material : [node.material];
      for (const mat of mats) {
        for (const key of Object.keys(mat)) {
          const prop = mat[key];
          if (prop && typeof prop === "object" && typeof prop.dispose === "function") {
            prop.dispose();
          }
        }
        if (typeof mat.dispose === "function") {
          mat.dispose();
        }
      }
    }
  });
}

export function createManagedScene(containerEl, initialPresetName = null) {
  const probeCanvas = document.createElement("canvas");
  const probeGl = probeCanvas.getContext("webgl2") || probeCanvas.getContext("webgl");
  const detectedPreset = initialPresetName || detectHardwarePreset(probeGl);
  let activePresetKey = QUALITY_PRESETS[detectedPreset] ? detectedPreset : "LOW";
  let activeConfig = QUALITY_PRESETS[activePresetKey];

  const renderer = new THREE.WebGLRenderer({
    antialias: activeConfig.antialias,
    powerPreference: activePresetKey === "LOW" ? "low-power" : "high-performance",
  });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.AgXToneMapping ?? THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;

  containerEl.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0c0e12);

  const camera = new THREE.PerspectiveCamera(45, 16 / 9, 0.1, 100.0);
  camera.position.set(0, 1.6, 4.2);

  function resize() {
    const clientW = Math.max(1, containerEl.clientWidth || window.innerWidth);
    const clientH = Math.max(1, containerEl.clientHeight || window.innerHeight);
    const scaleDown =
      clientH > activeConfig.maxRenderHeightPx ? activeConfig.maxRenderHeightPx / clientH : 1.0;
    const dpr = Math.min(window.devicePixelRatio || 1.0, activeConfig.maxPixelRatio) * scaleDown;

    renderer.setPixelRatio(dpr);
    renderer.setSize(clientW, clientH, true);
    camera.aspect = clientW / clientH;
    camera.updateProjectionMatrix();
  }

  function applyQualityPreset(presetKey) {
    if (!QUALITY_PRESETS[presetKey]) return activePresetKey;
    activePresetKey = presetKey;
    activeConfig = QUALITY_PRESETS[presetKey];
    renderer.shadowMap.enabled = activeConfig.shadowsEnabled;
    scene.traverse((obj) => {
      if (obj.isLight && obj.shadow) {
        obj.castShadow = activeConfig.shadowsEnabled;
      }
    });
    resize();
    return activePresetKey;
  }

  applyQualityPreset(activePresetKey);
  window.addEventListener("resize", resize);

  let contextLost = false;
  renderer.domElement.addEventListener("webglcontextlost", (e) => {
    e.preventDefault();
    contextLost = true;
  });
  renderer.domElement.addEventListener("webglcontextrestored", () => {
    contextLost = false;
    applyQualityPreset("LOW");
  });

  function renderFrame() {
    if (contextLost) return;
    renderer.render(scene, camera);
  }

  function destroy() {
    window.removeEventListener("resize", resize);
    disposeHierarchy(scene);
    renderer.dispose();
    if (renderer.domElement && renderer.domElement.parentNode) {
      renderer.domElement.parentNode.removeChild(renderer.domElement);
    }
  }

  return {
    renderer,
    scene,
    camera,
    getPreset: () => activePresetKey,
    applyQualityPreset,
    renderFrame,
    resize,
    destroy,
  };
}
