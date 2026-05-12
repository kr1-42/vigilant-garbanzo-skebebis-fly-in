# Test Suite Summary

## Files Generated

### 1. **parser_test_cases.py** (Main Test Suite)
Comprehensive Python test suite with 60+ test cases organized by constraint.

**Contains:**
- `ParserTestSuite` class with 60+ test methods
- Each test returns validation status and expected error message
- `generate_test_report()` function for human-readable output
- Full coverage of VII.4 parser constraints

**Usage:**
```python
from parser_test_cases import ParserTestSuite, generate_test_report

# Generate readable report
print(generate_test_report())

# Run individual tests
suite = ParserTestSuite()
result = suite.test_nb_drones_valid()
print(result)
```

### 2. **TEST_EXECUTION_GUIDE.md** (Documentation)
Detailed guide with test descriptions, expected inputs/outputs, and execution strategy.

**Contains:**
- Full test specification for all 60+ tests
- Test inputs and expected error messages
- Three-phase execution strategy
- Success criteria

---

## Test Input Files (Ready to Use)

### VALID Test Cases (Should Pass Parser)

1. **test_valid_minimal.txt** (4 lines)
   - Simplest valid configuration
   - 1 drone, direct path

2. **test_valid_complex.txt** (18 lines)
   - Real-world example (03_priority_puzzle.txt equivalent)
   - 4 drones, multiple paths with restrictions

3. **test_valid_with_comments.txt** (29 lines)
   - Valid with comments (lines starting with #)
   - Valid with extra whitespace

4. **test_valid_large_coords.txt** (7 lines)
   - Large coordinate values (-999999 to 999999)

---

### INVALID Test Cases (Should Fail Parser)

**Structure Errors:**
- test_invalid_no_nb_drones.txt → Missing first line
- test_invalid_no_start_hub.txt → No start_hub defined
- test_invalid_no_end_hub.txt → No end_hub defined
- test_invalid_multiple_start.txt → 2+ start_hubs

**Zone Definition Errors:**
- test_invalid_duplicate_zones.txt → Same zone name twice
- test_invalid_float_coords.txt → Floating point coordinates
- test_invalid_space_name.txt → Space in zone name
- test_invalid_dash_name.txt → Dash in zone name

**Zone Type/Capacity Errors:**
- test_invalid_zone_type.txt → Invalid zone= value
- test_invalid_zero_capacity.txt → max_drones=0
- test_invalid_negative_capacity.txt → max_drones=-5

**Connection Errors:**
- test_invalid_undefined_connection.txt → References undefined zone
- test_invalid_duplicate_connection.txt → Same connection twice
- test_invalid_reversed_connection.txt → Reversed duplicate (a-b, b-a)
- test_invalid_self_connection.txt → Zone connected to itself

**Metadata Errors:**
- test_invalid_missing_bracket.txt → Missing ]
- test_invalid_empty_metadata.txt → Empty []

---

## Test Coverage Matrix

| Constraint | Category | # Tests | Files |
|-----------|----------|---------|-------|
| VII.4.1 | nb_drones | 8 | parser_test_cases.py |
| VII.4.2 | Start/End Hubs | 6 | parser_test_cases.py + test files |
| VII.4.3 | Zone Definition | 10 | parser_test_cases.py + test files |
| VII.4.4 | Zone Types | 3 | parser_test_cases.py + test_invalid_zone_type.txt |
| VII.4.5 | Capacities | 6 | parser_test_cases.py + test files |
| VII.4.6 | Connections | 8 | parser_test_cases.py + test files |
| VII.4.7 | Metadata | 8 | parser_test_cases.py + test_invalid_missing_bracket.txt |
| VII.4.8 | Error Reporting | 2 | parser_test_cases.py |
| VII.4.9 | Edge Cases | 9 | parser_test_cases.py + test_valid_*.txt |
| **TOTAL** | | **60** | |

---

## How to Use These Tests

### Option 1: Automated Test Execution (Python)
```bash
# Run the test suite
python parser_test_cases.py

# Generate human-readable report
python -c "from parser_test_cases import generate_test_report; print(generate_test_report())"
```

### Option 2: Manual Testing with Files
```bash
# Test your parser with each file
python your_parser.py test_valid_minimal.txt          # Should succeed
python your_parser.py test_invalid_no_nb_drones.txt   # Should fail

# For each invalid test, verify:
# - Parser rejects the input
# - Error includes line number
# - Error message is descriptive
```

### Option 3: Integration Test
Write a test wrapper that:
1. Runs your parser on each input file
2. Checks return code (0 for valid, non-0 for invalid)
3. Validates error message contains expected text
4. Reports pass/fail for each test

---

## Test Organization Structure

```
parser_test_cases.py
├── ParserTestSuite
│   ├── test_nb_drones_valid() → Test 1.1
│   ├── test_nb_drones_missing() → Test 1.2
│   ├── test_nb_drones_not_first_line() → Test 1.3
│   ├── ... (60+ methods total)
│
└── generate_test_report()
    └── Produces formatted documentation

Test Input Files (24 files)
├── test_valid_*.txt (4 files)
│   ├── test_valid_minimal.txt
│   ├── test_valid_complex.txt
│   ├── test_valid_with_comments.txt
│   └── test_valid_large_coords.txt
│
└── test_invalid_*.txt (20 files)
    ├── Structure errors (4 files)
    ├── Zone definition errors (4 files)
    ├── Capacity errors (2 files)
    ├── Connection errors (4 files)
    └── Metadata errors (6 files)
```

---

## Expected Error Messages

Your parser should produce errors matching these patterns:

| Constraint | Error Pattern |
|-----------|--------------|
| Missing nb_drones | "First line must define nb_drones" |
| nb_drones not int | "nb_drones must be a positive integer" |
| No start_hub | "Exactly one start_hub must be defined" |
| Multiple start_hubs | "Exactly one start_hub must be defined" |
| Duplicate zones | "Zone 'name' already defined" |
| Float coordinates | "Coordinates must be integers" |
| Space in name | "Zone names cannot contain spaces" |
| Invalid zone type | "Invalid zone type 'X'. Must be one of: ..." |
| Zero capacity | "Capacity values must be positive integers (> 0)" |
| Undefined in connection | "Connection references undefined zone 'X'" |
| Duplicate connection | "Connection 'X-Y' already defined" |
| Self-connection | "Self-connections not allowed" |
| Missing bracket | "Metadata block not properly closed" |

**All errors must include:**
- Line number where error occurs
- Specific cause (zone name, value, etc.)

---

## Running Full Test Suite

### Test Phases:

**Phase 1: Core Functionality (Priority)**
- All 8 nb_drones tests
- All 6 start/end hub tests
- All 10 zone definition tests

**Phase 2: Validation (Important)**
- All 3 zone type tests
- All 6 capacity tests
- All 8 metadata tests

**Phase 3: Integration (Important)**
- All 8 connection tests
- All 2 error reporting tests

**Phase 4: Robustness (Nice to have)**
- All 9 edge case tests

---

## Success Criteria

✅ Parser passes all 4 valid test files
✅ Parser fails all 20 invalid test files  
✅ All error messages include line numbers
✅ All error messages include specific causes
✅ No false positives (valid configs rejected)
✅ No false negatives (invalid configs accepted)

---

## Files Provided

```
outputs/
├── parser_test_cases.py              (Main test suite - 60+ tests)
├── TEST_EXECUTION_GUIDE.md           (Detailed test specifications)
├── test_valid_minimal.txt            (Valid: Simplest config)
├── test_valid_complex.txt            (Valid: Real-world example)
├── test_valid_with_comments.txt      (Valid: Comments + whitespace)
├── test_valid_large_coords.txt       (Valid: Large numbers)
├── test_invalid_no_nb_drones.txt     (Invalid: Missing nb_drones)
├── test_invalid_no_start_hub.txt     (Invalid: No start_hub)
├── test_invalid_no_end_hub.txt       (Invalid: No end_hub)
├── test_invalid_multiple_start.txt   (Invalid: Multiple start_hubs)
├── test_invalid_duplicate_zones.txt  (Invalid: Duplicate zone names)
├── test_invalid_float_coords.txt     (Invalid: Float coordinates)
├── test_invalid_space_name.txt       (Invalid: Space in name)
├── test_invalid_dash_name.txt        (Invalid: Dash in name)
├── test_invalid_zone_type.txt        (Invalid: Bad zone type)
├── test_invalid_zero_capacity.txt    (Invalid: Zero capacity)
├── test_invalid_negative_capacity.txt (Invalid: Negative capacity)
├── test_invalid_undefined_connection.txt (Invalid: Undefined zone in connection)
├── test_invalid_duplicate_connection.txt (Invalid: Duplicate connection)
├── test_invalid_reversed_connection.txt  (Invalid: Reversed duplicate)
├── test_invalid_self_connection.txt      (Invalid: Self-connection)
├── test_invalid_missing_bracket.txt      (Invalid: Missing ])
├── test_invalid_empty_metadata.txt       (Invalid: Empty metadata block)
└── PARSER_TEST_SUMMARY.md            (This file)
```

**Total: 24 files (3 documentation + 1 test suite + 20 test inputs)**

