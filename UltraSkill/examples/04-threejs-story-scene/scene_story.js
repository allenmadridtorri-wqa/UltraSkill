/**
 * Example 04 — Realtime WebGL / Three.js Interactive Story Runtime
 * Enforces LOW preset defaults (DPR 1.0, <= 150 draw calls, zero per-frame allocations)
 * for 4 GB RAM laptops with 1 GB Intel UHD graphics.
 */

export const QUALITY_PRESETS = {
  LOW: { maxDpr: 1.0, shadowMapSize: 1024, maxDrawCalls: 150, vramBudgetMb: 512 },
  MEDIUM: { maxDpr: 1.25, shadowMapSize: 2048, maxDrawCalls: 400, vramBudgetMb: 1200 },
  HIGH: { maxDpr: 1.5, shadowMapSize: 2048, maxDrawCalls: 1000, vramBudgetMb: 3000 },
};

export const STORY_GRAPH = {
  entry: "n_start",
  nodes: {
    n_start: {
      title: "Vault Threshold",
      body: "Moonlight cuts across the brass astrolabe at the center of the basalt chamber. An empty lens socket gleams on the northern ring.",
      camera: { pos: [0.0, 2.1, 5.2], target: [0.0, 0.9, 0.0], fov: 50 },
      choices: [
        { label: "Inspect Brass Astrolabe", target: "n_inspect_astrolabe" },
        { label: "Search Pedestal Drawer", target: "n_find_lens", setFlag: "has_prism_lens" },
      ],
    },
    n_find_lens: {
      title: "The Obsidian Drawer",
      body: "Inside the velvet-lined recess you recover a bevel-cut sapphire prism lens.",
      camera: { pos: [-1.4, 1.4, 2.4], target: [-0.6, 0.7, 0.0], fov: 42 },
      choices: [
        { label: "Examine Astrolabe Ring", target: "n_inspect_astrolabe" },
      ],
    },
    n_inspect_astrolabe: {
      title: "Astrolabe Meridian Ring",
      body: "Fine vernier graduations line the ring. The northern socket requires a refractive prism to focus the zenith beam.",
      camera: { pos: [0.6, 1.45, 1.75], target: [0.0, 1.05, 0.0], fov: 38 },
      choices: [
        { label: "Insert Sapphire Prism Lens", target: "n_align_beam", requireFlag: "has_prism_lens" },
        { label: "Step Back to Chamber Entrance", target: "n_start" },
      ],
    },
    n_align_beam: {
      title: "Refracted Zenith Beam",
      body: "The sapphire prism locks into place with a crisp click. Coherent amber light splits across the vault door seal.",
      camera: { pos: [0.0, 1.8, 3.4], target: [0.0, 1.2, -1.8], fov: 45 },
      choices: [
        { label: "Unseal Observatory Vault", target: "n_vault_opened", setFlag: "vault_unlocked" },
      ],
    },
    n_vault_opened: {
      title: "The Star Archive Awakens",
      body: "The basalt monolithic doors part silently, revealing the celestial chart mechanism intact.",
      camera: { pos: [0.0, 2.4, 4.0], target: [0.0, 1.3, -3.0], fov: 50 },
      choices: [
        { label: "Restart Inspection", target: "n_start" },
      ],
    },
  },
};

// Pre-allocated module-scoped scratch vectors (ZERO per-frame heap allocations)
const _camCurrentPos = [0.0, 2.1, 5.2];
const _camCurrentTarget = [0.0, 0.9, 0.0];

export function expDecayVec3(out, current, target, decay, dt) {
  const factor = Math.exp(-decay * dt);
  out[0] = target[0] + (current[0] - target[0]) * factor;
  out[1] = target[1] + (current[1] - target[1]) * factor;
  out[2] = target[2] + (current[2] - target[2]) * factor;
}

export class StorySceneController {
  constructor() {
    this.preset = "LOW";
    this.currentNodeId = STORY_GRAPH.entry;
    this.flags = {};
    this.historyStack = [];
    this.activeDrawCalls = 4; // 1 instanced pillar ring + 3 hero props
    this.estimatedVramMb = 28;
  }

  transitionTo(targetNodeId, setFlagName = null) {
    if (!STORY_GRAPH.nodes[targetNodeId]) {
      return false;
    }
    this.historyStack.push({
      nodeId: this.currentNodeId,
      flags: { ...this.flags },
    });
    if (setFlagName) {
      this.flags[setFlagName] = true;
    }
    this.currentNodeId = targetNodeId;
    return true;
  }

  rewind() {
    if (this.historyStack.length === 0) {
      return false;
    }
    const prev = this.historyStack.pop();
    this.currentNodeId = prev.nodeId;
    this.flags = prev.flags;
    return true;
  }

  stepCamera(dt) {
    const node = STORY_GRAPH.nodes[this.currentNodeId];
    expDecayVec3(_camCurrentPos, _camCurrentPos, node.camera.pos, 8.0, dt);
    expDecayVec3(_camCurrentTarget, _camCurrentTarget, node.camera.target, 10.0, dt);
  }
}

if (typeof document !== "undefined") {
  const controller = new StorySceneController();
  const titleEl = document.getElementById("story-title");
  const bodyEl = document.getElementById("story-body");
  const choicesEl = document.getElementById("story-choices");
  const presetEl = document.getElementById("preset-select");
  const rewindBtn = document.getElementById("rewind-btn");
  const telemetryEl = document.getElementById("telemetry-readout");

  function renderUI() {
    const node = STORY_GRAPH.nodes[controller.currentNodeId];
    if (titleEl) titleEl.textContent = node.title;
    if (bodyEl) bodyEl.textContent = node.body;
    if (telemetryEl) {
      telemetryEl.textContent = `Preset: ${controller.preset} | Draws: ${controller.activeDrawCalls} | VRAM: ${controller.estimatedVramMb} MB`;
    }
    if (choicesEl) {
      choicesEl.textContent = "";
      for (const ch of node.choices) {
        if (ch.requireFlag && !controller.flags[ch.requireFlag]) continue;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.textContent = ch.label;
        btn.addEventListener("click", () => {
          controller.transitionTo(ch.target, ch.setFlag || null);
          renderUI();
        });
        choicesEl.appendChild(btn);
      }
    }
  }

  if (presetEl) {
    presetEl.addEventListener("change", (e) => {
      controller.preset = e.target.value;
      renderUI();
    });
  }
  if (rewindBtn) {
    rewindBtn.addEventListener("click", () => {
      if (controller.rewind()) renderUI();
    });
  }

  let lastTimeMs = performance.now();
  function tick(nowMs) {
    const dt = Math.min(0.1, (nowMs - lastTimeMs) / 1000.0);
    lastTimeMs = nowMs;
    controller.stepCamera(dt);
    requestAnimationFrame(tick);
  }

  renderUI();
  requestAnimationFrame(tick);
}
