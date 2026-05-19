# Runtime Error Analysis: MultiPathDroneScheduler Bug Report

## Executive Summary

A **critical IndexError** occurs when running simulations with multiple paths (e.g., `linear_path.txt`). The error manifests as "Runtime Error: " with an empty or minimal message because it's a bare IndexError being caught by the generic exception handler.

---

## 🔴 PRIMARY BUG: Path Index Mismatch in SimulationWithMultiPath

### Location
**File:** `src/simulation/integration.py`
**Lines:** 113-138 (SimulationWithMultiPath class)

### Root Cause

The `SimulationWithMultiPath` class has a fundamental architectural flaw:

1. **Line 113:** The movement tracker is initialized with only the **primary path** (first path):
   ```python
   self.primary_path = paths[0] if paths else []
   self.tracker = DroneMovementTracker(self.primary_path, data.nb_drones)
   ```

2. **Lines 125-138:** But drones are assigned to **multiple different paths** by the scheduler:
   ```python
   for drone in self.scheduler.drones:
       old_pos = positions_before[drone.drone_id]
       new_pos = drone.path_index  # ← Index on drone's ASSIGNED path

       if new_pos > old_pos:
           self.tracker.record_movement(drone.drone_id, old_pos, new_pos)
   ```

3. **Movement Tracker (line 40):** Tries to access the wrong path:
   ```python
   destination = self.path[new_path_index]  # ← Uses primary_path, not drone's path!
   ```

### Why This Causes IndexError

**Scenario with `linear_path.txt`:**

When `find_multiple_paths()` generates multiple paths for a single-hub layout:
- **Path 0:** `[start, waypoint1, waypoint2, goal]` (length 4)
- **Path 1:** `[start, waypoint2, goal]` (length 3)
- Tracker initialized with Path 0 only

When a drone assigned to Path 1 reaches index 2:
- `drone.path_index = 2` (valid: Path 1 has indices 0, 1, 2)
- `tracker.record_movement(..., old_pos=1, new_pos=2)` called
- Inside `movement_tracker.py:40`: `destination = self.path[2]`
- **Path 0 has indices 0, 1, 2, 3** ✓ This works
- BUT: What if Path 1 is longer? → **IndexError!**

**Better scenario demonstrating the bug:**
- Path 0: `[start, hub1, end]` (length 3)
- Path 1: `[start, hub1, hub2, hub3, end]` (length 5)
- Drone on Path 1 moves to position 3
- Tracker tries: `self.path[3]` where `self.path` is Path 0 with length 3
- **Result:** `IndexError: list index out of range`

---

## 🟡 SECONDARY BUG: Hardcoded Path Assignment

### Location
**File:** `src/algo/multi_path_scheduler.py`
**Line:** 247 (in `_spawn_new_drones()` method)

### Problem
```python
def _spawn_new_drones(self) -> None:
    ...
    while (
        self.next_drone_id < self.total_drones_to_spawn
        and start_hub_occupancy < start_hub_capacity
    ):
        # Assign to best path
        best_path_idx = 0  # ← HARDCODED! Always path 0
        ...
        self.drone_path_assignment[self.next_drone_id] = best_path_idx
```

**Issue:** All spawned drones are always assigned to path 0, regardless of:
- Path capacities
- Path costs
- Load balancing opportunities

**Impact:** Suboptimal performance, but doesn't directly cause RuntimeError (unless paths[0] doesn't exist or is empty)

---

## 🟡 TERTIARY BUG: Empty Path Validation

### Location
**File:** `src/algo/multi_path_scheduler.py`
**Lines:** 42-46 (in `_distribute_initial_drones()`)

### Problem
```python
for path_idx, path in enumerate(self.paths):
    if drone_idx >= num_drones:
        break
    # Calculate how many drones can use this path
    # Limited by the smallest hub capacity along the path
    min_hub_capacity = min(
        self.data.hubs[hub].max_drones for hub in path
    )  # ← If path is empty list, min() raises ValueError
```

**Error if triggered:** `ValueError: min() arg is an empty sequence`
**Likelihood:** Low (pathfinding should validate), but possible edge case

---

## Detailed Call Stack

When running with `linear_path.txt`:

```
visualizer.py:96 - optimize_path_strategy() returns multiple paths
visualizer.py:113 - SimulationWithMultiPath created with paths list
integration.py:113 - DroneMovementTracker initialized with paths[0] only
integration.py:127-138 - advance_turn() records movements
integration.py:138 - tracker.record_movement() called with wrong path index
movement_tracker.py:40 - self.path[new_path_index] → IndexError!
__main__.py:36 - Exception caught: print(f"Runtime Error: {e}")
```

---

## 📋 Summary of Issues

| Issue | Severity | Location | Error | Fix Type |
|-------|----------|----------|-------|----------|
| Path index mismatch in tracker | **CRITICAL** | `integration.py:113-138` | IndexError | Architectural redesign |
| Hardcoded path 0 assignment | Medium | `multi_path_scheduler.py:247` | Suboptimal routing | Logic improvement |
| Empty path min() call | Low | `multi_path_scheduler.py:42-46` | ValueError | Input validation |

---

## 🔧 Recommended Fixes

### Fix 1: Track Drone Paths Properly (Priority: CRITICAL)
**Option A:** Store drone-to-path mappings and use correct path when recording:
```python
# In SimulationWithMultiPath.advance_turn()
for drone in self.scheduler.drones:
    drone_path = self.paths[self.scheduler.drone_path_assignment[drone.drone_id]]
    # Use drone_path instead of primary_path for tracking
```

**Option B:** Modify tracker to accept multi-path drones and look up correct path dynamically

### Fix 2: Improve Path Assignment Logic (Priority: MEDIUM)
Replace hardcoded `best_path_idx = 0` with:
```python
# Load balance across paths or choose based on capacity
path_occupancies = [
    self.get_hub_occupancy(path[0]) for path in self.paths
]
best_path_idx = path_occupancies.index(min(path_occupancies))
```

### Fix 3: Validate Paths (Priority: LOW)
Add validation in `_distribute_initial_drones()`:
```python
if not path or len(path) < 2:
    continue  # Skip empty or invalid paths
```

---

## Files Affected
- `src/simulation/integration.py` (lines 113-138)
- `src/algo/multi_path_scheduler.py` (lines 42-46, 247)
- `src/simulation/movement_tracker.py` (line 40 - affected by bug, not root cause)

---

## Test Case
File: `maps/easy/01_linear_path.txt`
- 6 drones
- 4 hubs in linear arrangement
- Reproduces the error when multiple paths are found
