# Examples

The `Config/Examples/` folder in the plugin contains 5 complete `.llmstate` files demonstrating different AI patterns.

---

## SimpleAI

Basic AI behavior with Idle, Patrol, Chase, and Attack states.

**File:** `Config/Examples/SimpleAI.llmstate`

**States:** Idle → Patrol → Chase → Attack → Idle

**Parameters:**
- `PatrolRadius` (float) - Radius for patrol behavior
- `ChaseSpeed` (float) - Movement speed when chasing
- `IdleDuration` (float) - Time to wait in idle state

---

## GuardAI

Guard NPC with patrol, investigate, chase, and return home states.

**File:** `Config/Examples/GuardAI.llmstate`

**States:** Idle → Patrol → Investigate → Chase → ReturnHome → Idle

**Parameters:**
- `AlertRadius` (float) - Distance at which guard becomes alerted
- `ChaseSpeed` (float) - Movement speed when chasing intruder
- `VisionAngle` (float) - Cone angle for vision detection
- `ReturnHomeRadius` (float) - Distance from home before returning

---

## UtilityAI

Utility AI with considerations for action selection based on health, ammo, and distance.

**File:** `Config/Examples/UtilityAI.llmstate`

**States:** Idle → SelectAction (UtilityMax selection) → Flee/Attack/Reload/Approach

**Parameters:**
- `MaxHealth` (float) - Maximum health value
- `LowHealthThreshold` (float) - Health threshold for flee consideration
- `OptimalAttackRange` (float) - Ideal distance for attacking
- `MaxAmmo` (float) - Maximum ammo count

**Considerations:**
- `HealthScore` - Higher score when health is low (flee优先)
- `AttackScore` - Constant high score (always viable)
- `AmmoScore` - Higher score when ammo is low (reload优先)
- `DistanceScore` - Closer to target = higher score

---

## StealthAI

Stealth AI with hide, sneak, detect, and escape states.

**File:** `Config/Examples/StealthAI.llmstate`

**States:** Idle → Sneak → Detected → Escape → Hide → Idle

**Parameters:**
- `DetectionThreshold` (float) - Alert level to trigger detection (default: 0.7)
- `SafeZoneRadius` (float) - Distance to safe hiding spot (default: 300.0)
- `SneakSpeed` (float) - Movement speed while sneaking (default: 150.0)
- `EscapeSpeed` (float) - Movement speed while escaping (default: 600.0)

---

## BossAI

Boss AI with multiple phases based on health thresholds.

**File:** `Config/Examples/BossAI.llmstate`

**States:** Phase1 → Phase2 → Phase3 → Enraged (loops)

**Phase Details:**

| Phase | States | Attack Pattern |
|-------|--------|----------------|
| Phase1 | Phase1_Attack, Phase1_Wait | Basic attack, 2s cooldown |
| Phase2 | Phase2_Attack, Phase2_Move | Faster attack, 1.5s cooldown |
| Phase3 | Phase3_RageAttack, Phase3_Slam, Phase3_Recovery | Combo attack, 0.8s cooldown |
| Enraged | Enraged | Continuous attack, 0.3s cooldown |

**Parameters:**
- `Phase2HealthThreshold` (float) - Health % to trigger Phase 2 (default: 0.66)
- `Phase3HealthThreshold` (float) - Health % to trigger Phase 3 (default: 0.33)
- `EnrageDuration` (float) - Time before boss becomes enraged (default: 10.0s)
- `Phase2AttackCooldown` (float) - Attack cooldown in Phase 2 (default: 1.5s)
- `Phase3AttackCooldown` (float) - Attack cooldown in Phase 3 (default: 0.8s)

---

## Using Examples

1. Open the LLMStateTree Editor Panel
2. Click "Load File" and navigate to `Config/Examples/`
3. Select any `.llmstate` file
4. Click "Generate StateTree"
5. The StateTree Blueprint will be created in your project's Content folder
