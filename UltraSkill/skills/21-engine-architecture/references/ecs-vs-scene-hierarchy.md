# ECS vs Scene Hierarchy & Component Composition

## 1. Banning Deep Inheritance Trees (`Entity -> Actor -> Character -> Enemy -> FlyingEnemy`)

In month 2 of game development, a 5-level class inheritance hierarchy always collapses when the designer asks for a *"Destructible Turret that cannot move like a Character, has Health and Armor like an Enemy, and can be pushed like a PhysicsCrate."*

### The Composition Rule (Godot Nodes & Custom Components)
Limit class inheritance to **at most 1 level** above the engine base (`CharacterBody3D` or `Node3D`) and assemble capabilities by attaching orthogonal child/peer components:

```text
Enemy_Suppressor (CharacterBody3D)
 ├── HealthComponent (Node)         # Tracks HP, armor mitigation, emits `damaged` / `died`
 ├── HurtboxComponent (Area3D)      # Receives incoming Hitbox overlaps, forwards to HealthComponent
 ├── WeaponComponent (Node3D)       # Pulls projectiles from ObjectPool, enforces fire cooldown
 ├── VelocityComponent (Node)       # Accelerates/decelerates parent CharacterBody3D and calls move_and_slide()
 └── StateMachine (Node)            # Transitions between Idle,Reposition, Telegraph, Fire, Stagger
```

Now creating a *Destructible Explosive Barrel* requires zero new inheritance classes—attach `HealthComponent` + `HurtboxComponent` + `ExplosionOnDeathComponent` to a `StaticBody3D`!

## 2. Data-Oriented SoA (Struct of Arrays) for High-Count Entities (`N >= 250`)

Scene-tree node objects carry per-node memory and virtual dispatch overhead. Choose the representation based on active instance count:

| Entity Count (`N`) | Recommended Architecture | Why |
|---|---|---|
| **`1 – 150` Entities** (Player, squad companions, active arena enemies, doors, bosses) | **Component-Composed Scene Nodes** (`CharacterBody3D` + modular child component nodes + `StateMachine`) | High readability, easy inspector debugging, negligible CPU cost (`< 0.8 ms` per frame for 50 enemies). |
| **`150 – 10,000` Entities** (Bullet-hell projectiles, swarm particles, RTS crowds, debris) | **Data-Oriented Flat Typed Arrays / ECS** (`Float32Array` positions, velocities, lifetimes + `1` `MultiMeshInstance3D` / `THREE.InstancedMesh`) | Zero per-entity node overhead, contiguous L1/L2 CPU cache iteration, and **`1` GPU draw call** for all 5,000 bullets! |

## 3. Separate Data Definitions (`Resource` / JSON) from Runtime State

Keep immutable design tuning data (max HP, move speed, attack startup frames, loot table ID) inside read-only configuration tables or Godot `Resource` objects (`EnemyStatsData`), and store mutable per-instance state (`current_hp`, `cooldown_timer`, `stun_remaining`) on the runtime component.
