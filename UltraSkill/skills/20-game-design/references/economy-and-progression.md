# Game Economy, Faucets, Sinks & Progression Curves

## 1. Closed-Loop Faucet-to-Sink Conservation

An in-game resource (Gold, Scrap, Mana, Ammo) only forces meaningful player decisions when **Scarcity = Faucets - Sinks** is tightly bounded.
- **If Faucets >> Sinks**: By mid-game the player has `99,999 Gold` and `50 Health Potions`, making all chest rewards meaningless and trivializing combat damage.
- **If Sinks >> Faucets**: A player who misses 3 shots or dies twice enters an unwinnable **Death Spiral** (zero ammo/repair money to defeat the enemies that drop ammo/money).

### Anti-Death-Spiral Floor Rule
Always provide a **Zero-Cost Baseline Floor**:
- A basic melee attack or regenerating primary pistol shot costs `0` resources.
- Or ammo/health drop probability dynamically scales inversely with current player reserves:
  $$P_{\text{drop}}(\text{reserve}) = P_{\text{base}} + (P_{\max} - P_{\text{base}}) \cdot \left(1 - \text{clamp}\left(\frac{\text{reserve}}{\text{target\_reserve}}, 0, 1\right)\right)^2$$

## 2. Standard Mathematical Progression Curves (Starting Values)

| Curve Type | Formula ($L = \text{Level } 1..N$) | Best Use Case | Why It Works |
|---|---|---|---|
| **XP Required for Next Level (`Polynomial`)** | $\text{XP}(L) = \text{round}\left(100 \cdot L^{1.65}\right)$ | Character level milestones | Grows faster than linear enemy XP drops (`100 * L^1.15`), requiring slightly more encounters per level without hitting an exponential brick wall. |
| **Player Stat Growth (`Linear + Soft Cap`)** | $\text{Damage}(L) = D_0 + 4.5 \cdot (L - 1)$ | Weapon base damage and max HP | Predictable Time-to-Kill (`TTK`); doubling exponential player stats (`1.15^L`) turns Level 1 enemies into 1-hit dust and Level 20 enemies into 1-shot killers. |
| **Armor / Damage Reduction (`Hyperbolic Diminishing Returns`)** | $\text{DR}(\text{Armor}) = \frac{\text{Armor}}{\text{Armor} + K_{\text{half}}}$ ($K_{\text{half}} = 100$) | Defense rating, cooldown reduction | Each point of Armor increases **Effective HP (`EHP`)** linearly ($\text{EHP} = \text{HP} \cdot (1 + \frac{\text{Armor}}{100})$) while never reaching `100%` invulnerability! |
| **Permanent Upgrade Cost (`Exponential Sink`)** | $\text{Cost}(\text{Tier } T) = C_0 \cdot 1.85^{(T - 1)}$ | Workshop / meta-progression upgrades | Absorbs late-game wealth surplus while keeping Tier 1–2 upgrades affordable in the first 15 minutes. |
