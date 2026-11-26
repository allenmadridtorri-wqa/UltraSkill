# Ragdolls and Raycast Vehicles

Dynamic multi-body physics constraints (ragdoll bone chains and multi-wheel suspensions) are notorious for exploding into NaN velocities or eating the entire physics budget if left unguarded.

---

## 1. Stable 9-Bone Ragdoll Setup

Never build a 65-bone ragdoll including individual finger and toe rigid bodies. Use at most **9–11 rigid bodies** for humanoid ragdolls:
1. `Pelvis` (Root body, `16 kg`)
2. `Spine_Upper` (`18 kg`)
3. `Head` (`5 kg`)
4. `UpperArm_L` / `UpperArm_R` (`2.5 kg` each)
5. `LowerArm_L` / `LowerArm_R` (`1.8 kg` each)
6. `UpperLeg_L` / `UpperLeg_R` (`7.0 kg` each)
7. `LowerLeg_L` / `LowerLeg_R` (`4.5 kg` each)

### Four Rules that Prevent Ragdoll Jitter
1. **Mass Ratio Constraint**: Adjacent connected bodies must have a mass ratio **`<= 4:1`**. Connecting a `20 kg` torso directly to a `0.5 kg` hand causes constraint solver oscillation.
2. **Disable Adjacent Self-Collision**: Adjacent limbs sharing a joint must never collide with each other.
3. **Anatomical Cone/Twist Limits + Joint Damping**:
   - Elbows and knees: Hinge constraints (`[0°, 130°]`) with `angular_damping = 8.0`.
   - Shoulders and hips: Cone-twist (`swing <= 60°`, `twist <= 35°`).
4. **Hard Sleep Cap & Budget**:
   - Cap active ragdolls to **`3`** on the `LOW` preset (`8` on `HIGH`).
   - After **`2.5 seconds`** (or once all bone linear velocities drop `< 0.08 m/s`), freeze the ragdoll bodies and stop bone simulation entirely.

---

## 2. Raycast Vehicle Suspension Math

Standard rigid-body cylinder wheels attached with hinge joints snag on mesh triangle seams at high speed. Use a **4-Wheel Raycast Suspension** on a single `RigidBody3D` chassis (`mass = 1200 kg`, center of mass lowered to `y = -0.35 m` to prevent rollovers):

For each wheel $i \in \{FL, FR, RL, RR\}$ casting a ray downward of length $L_{rest} + R_{wheel}$:
1. **Compression ($x$)**: $x = L_{rest} - L_{hit}$ (clamped to $[0, L_{max}]$).
2. **Compression Velocity ($v_{susp}$)**: $v_{susp} = \frac{x - x_{prev}}{\Delta t}$.
3. **Spring-Damper Vertical Force ($F_y$)**:
   $$F_y = \max(0, \; k_{spring} \cdot x + c_{damper} \cdot v_{susp})$$
   - Given natural frequency $f_n = 2.0\text{ Hz}$ ($\omega_n = 2\pi f_n$) and quarter-car mass $m_q = 300\text{ kg}$:
     - $k_{spring} = m_q \cdot \omega_n^2 \approx 47,374\text{ N/m}$
     - $c_{damper} = 2 \cdot \zeta \cdot \sqrt{k_{spring} \cdot m_q} \approx 5,650\text{ N}\cdot\text{s/m}$ (at damping ratio $\zeta = 0.75$).
4. **Lateral Tire Grip (Slip Suppression)**:
   - Measure lateral velocity at wheel contact patch: $v_{lat} = \vec{v}_{wheel} \cdot \vec{right}_{wheel}$.
   - Apply counter-impulse $J_{lat} = -m_q \cdot v_{lat} \cdot \text{grip\_factor}$, reducing `grip_factor` from `0.85` (tarmac grip) to `0.35` when handbrake drifting is engaged.
