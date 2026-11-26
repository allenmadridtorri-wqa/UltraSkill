# The Living Tabular Game Design Document (GDD)

## 1. Nobody Reads a 100-Page Wall-of-Prose GDD

Giant monolithic prose GDDs rot within two weeks of pre-production because engineers and artists do not read 40 paragraphs of fiction to find out whether the dash cooldown is `0.6 s` or `1.2 s`.

### The Three Rules of a Living Studio GDD
1. **Start With the One-Pager (`GDD_ONE_PAGER.md`)**:
   - Captures the 3 Razor Pillars, the 3 Time-Horizon Loops, the Complete Input Map (never exceed `6–8` core actions!), and the Hard Scope Ceiling (exact count of levels, enemy archetypes, and weapons for v1.0).
2. **Express Mechanics as State Tables and Parameter Sheets (`<= 15 pages` total)**:
   - Every mechanic is defined by:
     - **Trigger / Input** (e.g., `Action_Dash` pressed while grounded or airborne with `dash_charges >= 1`).
     - **State Transition & Frame Data** (`Startup = 2f`, `Active = 10f @ 16.0 m/s + i-frames`, `Recovery = 6f`, `Cooldown = 45f / 0.75s`).
     - **Audio / Visual Feedback Contract** (FOV pulse `+4 deg`, dash trail ribbon, whoosh transient `-8 dBFS`, stamina bar flash).
     - **Edge-Case Rules** (what happens if hitting a wall mid-dash? What if pressing attack on frame 8 of dash?).
3. **Single Source of Truth Between GDD and Data Files**:
   - Store numeric tuning parameters (HP, damage, cooldowns, speeds, drop weights) in JSON or Resource tables validated by `skills/22-gameplay-systems/scripts/verify_stat_tables.py` and simulated by [`../scripts/balance_simulator.py`](../scripts/balance_simulator.py) so design changes update both the documentation and the running build simultaneously.
