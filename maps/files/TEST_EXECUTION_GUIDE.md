# Parser Test Suite - Execution Guide

## Overview
This document provides comprehensive testing guidance for the drone maze parser. All tests are organized by constraint section VII.4 from your specification.

---

## Test Organization

### Total Tests: 60+

**By Category:**
- VII.4.1 nb_drones Definition: 8 tests
- VII.4.2 Start/End Hubs: 6 tests
- VII.4.3 Zone Definition: 10 tests
- VII.4.4 Zone Types: 3 tests
- VII.4.5 Capacity Values: 6 tests
- VII.4.6 Connections: 8 tests
- VII.4.7 Metadata Syntax: 8 tests
- VII.4.8 Error Reporting: 2 tests
- VII.4.9 Edge Cases: 9 tests

---

## VII.4.1: nb_drones Definition (8 tests)

### Test 1.1: Valid nb_drones ✓
**Input:**
```
nb_drones: 4
start_hub: start 0 0 [color=green]
end_hub: goal 1 0 [color=green]
connection: start-goal
```
**Expected:** Parse successfully

### Test 1.2: Missing nb_drones ✗
**Input:** File without nb_drones line
**Expected Error:** "First line must define nb_drones"

### Test 1.3: nb_drones Not First Line ✗
**Input:** nb_drones on line 2
**Expected Error:** "nb_drones must be first line"

### Test 1.4: Invalid Format ✗
**Input:** `nb_drones = 4` (using = instead of :)
**Expected Error:** "Invalid nb_drones format (expected 'nb_drones: <int>')"

### Test 1.5: Non-Integer Value ✗
**Input:** `nb_drones: four`
**Expected Error:** "nb_drones must be a positive integer"

### Test 1.6: Zero Value ✗
**Input:** `nb_drones: 0`
**Expected Error:** "nb_drones must be a positive integer (> 0)"

### Test 1.7: Negative Value ✗
**Input:** `nb_drones: -5`
**Expected Error:** "nb_drones must be a positive integer"

### Test 1.8: Large Valid Value ✓
**Input:** `nb_drones: 1000`
**Expected:** Parse successfully

---

## VII.4.2: Start and End Hubs (6 tests)

### Test 2.1: Exactly One Start Hub ✓
**Expected:** File with one start_hub parses
**Input:** Standard file with `start_hub: name x y`

### Test 2.2: No Start Hub ✗
**Expected Error:** "Exactly one start_hub must be defined"
**Input:** File using only `hub:` instead of `start_hub:`

### Test 2.3: Multiple Start Hubs ✗
**Expected Error:** "Exactly one start_hub must be defined"
**Input:** 
```
start_hub: start1 0 0
start_hub: start2 1 0
```

### Test 2.4: Exactly One End Hub ✓
**Expected:** File with one end_hub parses
**Input:** Standard file with `end_hub: name x y`

### Test 2.5: No End Hub ✗
**Expected Error:** "Exactly one end_hub must be defined"
**Input:** File using only `hub:` instead of `end_hub:`

### Test 2.6: Multiple End Hubs ✗
**Expected Error:** "Exactly one end_hub must be defined"
**Input:** 
```
end_hub: goal1 1 0
end_hub: goal2 2 0
```

---

## VII.4.3: Zone Definition (10 tests)

### Test 3.1: Unique Zone Names ✓
**Input:** All zones have different names
**Expected:** Parse successfully

### Test 3.2: Duplicate Zone Names ✗
**Input:** 
```
hub: zone1 1 0
hub: zone1 2 0
```
**Expected Error:** "Zone 'zone1' already defined at line 2"

### Test 3.3: Valid Integer Coordinates ✓
**Input:** Coordinates including negative values (-5, -10, 0, 100, 999999)
**Expected:** Parse successfully

### Test 3.4: Floating Point Coordinates ✗
**Input:** `hub: zone1 1.5 2.5`
**Expected Error:** "Coordinates must be integers"

### Test 3.5: Missing Y Coordinate ✗
**Input:** `hub: zone1 1`
**Expected Error:** "Zone definition requires name, x, and y coordinates"

### Test 3.6: Extra Coordinate ✗
**Input:** `hub: zone1 1 0 5`
**Expected Error:** "Zone definition has too many elements"

### Test 3.7: Valid Character Names ✓
**Input:** `hub: zone_1b 1 0` and `hub: zone2_c 2 0`
**Expected:** Parse successfully

### Test 3.8: Space in Zone Name ✗
**Input:** `hub: start hub 0 0`
**Expected Error:** "Zone names cannot contain spaces"

### Test 3.9: Dash in Zone Name ✗
**Input:** `hub: start-hub 0 0`
**Expected Error:** "Zone names cannot contain dashes"

### Test 3.10: Special Characters in Zone Name ✗
**Input:** `hub: zone@1 1 0` or `hub: zone#1 1 0`
**Expected Error:** "Invalid character in zone name"

---

## VII.4.4: Zone Types (3 tests)

### Test 4.1: Valid Zone Types ✓
**Input:** Zones with zone=normal, zone=blocked, zone=restricted, zone=priority
**Expected:** Parse successfully

### Test 4.2: Invalid Zone Type ✗
**Input:** `hub: zone1 1 0 [zone=fast]`
**Expected Error:** "Invalid zone type 'fast'. Must be one of: normal, blocked, restricted, priority"

### Test 4.3: Multiple Invalid Types ✗
**Input:** Multiple zones with invalid types
**Expected Error:** Reports first/all invalid types

---

## VII.4.5: Capacity Values (6 tests)

### Test 5.1: Valid Capacities ✓
**Input:** 
```
hub: zone1 1 0 [max_drones=4]
connection: start-zone1 [max_link_capacity=2]
```
**Expected:** Parse successfully

### Test 5.2: Zone Capacity Zero ✗
**Input:** `hub: zone1 1 0 [max_drones=0]`
**Expected Error:** "Capacity values must be positive integers (> 0)"

### Test 5.3: Zone Capacity Negative ✗
**Input:** `hub: zone1 1 0 [max_drones=-5]`
**Expected Error:** "Capacity values must be positive integers"

### Test 5.4: Zone Capacity Non-Integer ✗
**Input:** `hub: zone1 1 0 [max_drones=2.5]`
**Expected Error:** "Capacity must be an integer"

### Test 5.5: Link Capacity Zero ✗
**Input:** `connection: start-goal [max_link_capacity=0]`
**Expected Error:** "Link capacity must be a positive integer"

### Test 5.6: Link Capacity Negative ✗
**Input:** `connection: start-goal [max_link_capacity=-2]`
**Expected Error:** "Link capacity must be a positive integer"

---

## VII.4.6: Connections (8 tests)

### Test 6.1: Valid Connections ✓
**Input:**
```
start_hub: start 0 0
hub: zone1 1 0
end_hub: goal 2 0
connection: start-zone1
connection: zone1-goal
```
**Expected:** Parse successfully

### Test 6.2: Connection to Undefined Zone ✗
**Input:** `connection: start-undefined`
**Expected Error:** "Connection references undefined zone 'undefined'"

### Test 6.3: Both Zones Undefined ✗
**Input:** `connection: zone1-zone2` (neither defined)
**Expected Error:** "Connection references undefined zone"

### Test 6.4: Exact Duplicate ✗
**Input:**
```
connection: start-zone1
connection: start-zone1
```
**Expected Error:** "Connection 'start-zone1' already defined"

### Test 6.5: Reversed Duplicate ✗
**Input:**
```
connection: start-zone1
connection: zone1-start
```
**Expected Error:** "Connection already defined (start-zone1 and zone1-start are duplicates)"

### Test 6.6: Self-Connection ✗
**Input:** `connection: zone1-zone1`
**Expected Error:** "Self-connections not allowed"

### Test 6.7: Missing Hyphen ✗
**Input:** `connection: start zone1`
**Expected Error:** "Invalid connection format (expected 'connection: zone1-zone2')"

### Test 6.8: Extra Spaces in Connection ✗
**Input:** `connection: start - zone1` (spaces around hyphen)
**Expected Error:** "Invalid connection format"

---

## VII.4.7: Metadata Syntax (8 tests)

### Test 7.1: Valid Metadata ✓
**Input:**
```
hub: zone1 1 0 [color=blue max_drones=4 zone=priority]
connection: start-zone1 [max_link_capacity=3]
```
**Expected:** Parse successfully

### Test 7.2: Missing Closing Bracket ✗
**Input:** `hub: zone1 1 0 [color=green`
**Expected Error:** "Metadata block not properly closed (missing ']')"

### Test 7.3: Missing Opening Bracket ✗
**Input:** `hub: zone1 1 0 color=green]`
**Expected Error:** "Metadata block not properly opened (missing '[')"

### Test 7.4: Wrong Separator ✗
**Input:** `hub: zone1 1 0 [color:green]`
**Expected Error:** "Invalid metadata format (expected 'key=value')"

### Test 7.5: Empty Value ✗
**Input:** `hub: zone1 1 0 [color=]`
**Expected Error:** "Metadata value cannot be empty"

### Test 7.6: Empty Key ✗
**Input:** `hub: zone1 1 0 [=green]`
**Expected Error:** "Invalid metadata format (expected 'key=value')"

### Test 7.7: Empty Metadata Block ✗
**Input:** `hub: zone1 1 0 []`
**Expected Error:** "Empty metadata block"

### Test 7.8: Unknown Metadata Keys ✓ (with warning)
**Input:** `hub: zone1 1 0 [custom_key=value]`
**Expected:** Should parse (unknown keys may be warned about but not fatal)

---

## VII.4.8: Error Reporting (2 tests)

### Test 8.1: Line Number Reporting ✗
**Input:** Invalid data on line 5
**Expected Error:** Must include "line 5" in error message

### Test 8.2: Specific Cause ✗
**Input:** Connection to undefined zone "missing_zone"
**Expected Error:** Must include "missing_zone" in error message

---

## VII.4.9: Edge Cases (9 tests)

### Test 9.1: Minimal Valid File ✓
```
nb_drones: 1
start_hub: start 0 0
end_hub: goal 1 0
connection: start-goal
```
**Expected:** Parse successfully

### Test 9.2: Large Coordinates ✓
**Input:** Coordinates like -999999, 1000000
**Expected:** Parse successfully

### Test 9.3: Many Zones (50+) ✓
**Input:** File with 50+ zones properly connected
**Expected:** Parse successfully

### Test 9.4: Extra Whitespace ✓
**Input:** Multiple spaces between tokens
```
nb_drones:    4
hub:    zone1    1    0
```
**Expected:** Parse successfully

### Test 9.5: Comment Lines ✓
**Input:** Lines starting with # before/between/after definitions
**Expected:** Parse successfully (comments ignored)

### Test 9.6: Empty Lines ✓
**Input:** Empty lines between definitions
**Expected:** Parse successfully

### Test 9.7: Real-World Example ✓
**Input:** The provided 03_priority_puzzle.txt
**Expected:** Parse successfully

### Test 9.8: All Valid Zone Attributes ✓
**Input:** Zone with all possible attributes
```
hub: zone1 1 0 [color=blue zone=priority max_drones=5]
```
**Expected:** Parse successfully

### Test 9.9: Connection Ordering ✓
**Input:** Connections in any order (not dependent on definition order)
**Expected:** Parse successfully

---

## Execution Strategy

### Phase 1: Unit Tests (Core Functionality)
1. Run tests for VII.4.1-4.5 (basic structure and values)
2. Validate error messages match specification
3. Ensure line numbers are reported

### Phase 2: Integration Tests (Relationships)
1. Run tests for VII.4.6-7 (connections and metadata)
2. Validate inter-zone dependencies
3. Check duplicate detection logic

### Phase 3: Robustness Tests (Edge Cases)
1. Run tests for VII.4.9 (edge cases)
2. Stress test with large files
3. Validate whitespace and comment handling

### Phase 4: Regression Tests
1. Run all tests on updated code
2. Ensure no previously passing tests now fail
3. Document any intentional behavior changes

---

## Test Data Files

Create these test input files for manual/integration testing:

### valid_minimal.txt (should pass)
```
nb_drones: 1
start_hub: start 0 0
end_hub: goal 1 0
connection: start-goal
```

### valid_complex.txt (should pass)
```
nb_drones: 4
start_hub: start 0 0 [color=green max_drones=4]
hub: slow_path1 1 -1 [zone=restricted color=red]
hub: slow_path2 2 -1 [zone=restricted color=red]
hub: slow_path3 3 -1 [zone=restricted color=red]
hub: fast_junction 1 0 [zone=priority color=blue max_drones=2]
hub: fast_path 2 0 [zone=priority color=blue]
hub: merge_point 3 0 [color=yellow max_drones=3]
end_hub: goal 4 0 [color=green max_drones=4]
connection: start-slow_path1
connection: start-fast_junction
connection: slow_path1-slow_path2
connection: slow_path2-slow_path3
connection: slow_path3-merge_point
connection: fast_junction-fast_path
connection: fast_path-merge_point
connection: merge_point-goal
```

### invalid_no_start.txt (should fail)
```
nb_drones: 4
hub: start 0 0 [color=green]
end_hub: goal 1 0 [color=green]
connection: start-goal
```
**Expected Error:** "Exactly one start_hub must be defined"

### invalid_bad_capacity.txt (should fail)
```
nb_drones: 4
start_hub: start 0 0 [max_drones=0]
end_hub: goal 1 0
connection: start-goal
```
**Expected Error:** "Capacity values must be positive integers (> 0)" on line 2

### invalid_duplicate_connection.txt (should fail)
```
nb_drones: 4
start_hub: start 0 0
hub: zone1 1 0
end_hub: goal 2 0
connection: start-zone1
connection: start-zone1
connection: zone1-goal
```
**Expected Error:** "Connection 'start-zone1' already defined" on line 6

---

## Success Criteria

✓ Parser accepts all valid test cases
✓ Parser rejects all invalid test cases
✓ Error messages include line numbers
✓ Error messages include specific causes
✓ Parser handles edge cases (whitespace, comments, large values)
✓ All 60+ test cases pass
