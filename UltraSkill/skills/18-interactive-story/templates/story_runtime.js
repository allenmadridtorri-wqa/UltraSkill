/**
 * UltraSkill Zero-Dependency Interactive Story Runtime (`story_runtime.js`).
 *
 * Executes a validated `story_graph.json`, evaluates choice precondition guards
 * (`requires`), applies state variable mutations (`effects`), maintains a bounded
 * 50-step checkpoint history stack for instant rewind, and serializes/restores
 * deterministic JSON snapshots to `localStorage`.
 */

export class StoryRuntime {
  constructor(storyGraph, options = {}) {
    if (!storyGraph || !storyGraph.nodes || !storyGraph.start_node) {
      throw new Error("Invalid storyGraph: missing 'nodes' or 'start_node'.");
    }
    this.graph = storyGraph;
    this.storageKey = options.storageKey || `ultraskill_save_${storyGraph.story_id || "default"}`;
    this.maxHistory = options.maxHistory || 50;
    this.onStateChange = typeof options.onStateChange === "function" ? options.onStateChange : null;

    this.currentNodeId = storyGraph.start_node;
    this.variables = structuredClone(storyGraph.initial_variables || {});
    this.visitedNodes = [this.currentNodeId];
    this.historyStack = [];
  }

  getCurrentNode() {
    return this.graph.nodes[this.currentNodeId] || null;
  }

  getCameraMark() {
    const node = this.getCurrentNode();
    if (!node || !node.camera_mark || !this.graph.camera_marks) return null;
    return this.graph.camera_marks[node.camera_mark] || null;
  }

  isChoiceAvailable(choice) {
    const reqs = choice.requires || {};
    for (const [key, expectedVal] of Object.entries(reqs)) {
      if (this.variables[key] !== expectedVal) {
        return false;
      }
    }
    return true;
  }

  getAvailableChoices() {
    const node = this.getCurrentNode();
    if (!node || !Array.isArray(node.choices)) return [];
    return node.choices.map((c) => ({
      ...c,
      enabled: this.isChoiceAvailable(c),
    }));
  }

  choose(choiceId) {
    const node = this.getCurrentNode();
    if (!node) throw new Error(`Active node '${this.currentNodeId}' not found.`);
    const choice = (node.choices || []).find((c) => c.id === choiceId);
    if (!choice) throw new Error(`Choice '${choiceId}' not found on node '${this.currentNodeId}'.`);
    if (!this.isChoiceAvailable(choice)) {
      throw new Error(`Choice '${choiceId}' preconditions not satisfied.`);
    }
    const nextNode = this.graph.nodes[choice.target];
    if (!nextNode) {
      throw new Error(`Target node '${choice.target}' does not exist in story graph.`);
    }

    this.historyStack.push({
      currentNodeId: this.currentNodeId,
      variables: structuredClone(this.variables),
      visitedNodes: [...this.visitedNodes],
    });
    if (this.historyStack.length > this.maxHistory) {
      this.historyStack.shift();
    }

    const effects = choice.effects || {};
    for (const [k, v] of Object.entries(effects)) {
      this.variables[k] = v;
    }

    this.currentNodeId = choice.target;
    this.visitedNodes.push(this.currentNodeId);
    this._emitChange();
    return this.getCurrentNode();
  }

  canRewind() {
    return this.historyStack.length > 0;
  }

  rewind() {
    if (!this.canRewind()) return this.getCurrentNode();
    const prev = this.historyStack.pop();
    this.currentNodeId = prev.currentNodeId;
    this.variables = structuredClone(prev.variables);
    this.visitedNodes = [...prev.visitedNodes];
    this._emitChange();
    return this.getCurrentNode();
  }

  reset() {
    this.currentNodeId = this.graph.start_node;
    this.variables = structuredClone(this.graph.initial_variables || {});
    this.visitedNodes = [this.currentNodeId];
    this.historyStack = [];
    this._emitChange();
    return this.getCurrentNode();
  }

  exportSnapshot() {
    return {
      schema_version: "1.0.0",
      story_id: this.graph.story_id || "default",
      current_node_id: this.currentNodeId,
      turn_index: this.visitedNodes.length - 1,
      variables: structuredClone(this.variables),
      visited_nodes: [...this.visitedNodes],
      timestamp_utc: new Date().toISOString(),
    };
  }

  importSnapshot(snapshot) {
    if (!snapshot || !snapshot.current_node_id || !this.graph.nodes[snapshot.current_node_id]) {
      throw new Error("Cannot import save snapshot: unknown current_node_id.");
    }
    this.currentNodeId = snapshot.current_node_id;
    this.variables = {
      ...structuredClone(this.graph.initial_variables || {}),
      ...structuredClone(snapshot.variables || {}),
    };
    this.visitedNodes = Array.isArray(snapshot.visited_nodes)
      ? [...snapshot.visited_nodes]
      : [this.currentNodeId];
    this.historyStack = [];
    this._emitChange();
    return this.getCurrentNode();
  }

  saveToLocalStorage() {
    if (typeof localStorage === "undefined") return false;
    localStorage.setItem(this.storageKey, JSON.stringify(this.exportSnapshot()));
    return true;
  }

  loadFromLocalStorage() {
    if (typeof localStorage === "undefined") return false;
    const raw = localStorage.getItem(this.storageKey);
    if (!raw) return false;
    this.importSnapshot(JSON.parse(raw));
    return true;
  }

  _emitChange() {
    if (this.onStateChange) {
      this.onStateChange({
        node: this.getCurrentNode(),
        cameraMark: this.getCameraMark(),
        choices: this.getAvailableChoices(),
        variables: structuredClone(this.variables),
        canRewind: this.canRewind(),
      });
    }
  }
}
