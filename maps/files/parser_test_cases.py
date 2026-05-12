"""
Comprehensive test cases for the drone maze parser
Tests all constraints from VII.4 Parser Constraints
"""

import pytest
from pathlib import Path
import tempfile
import os


class ParserTestSuite:
    """Test suite for parser constraint validation"""

    # ========== VII.4.1: nb_drones Definition ==========

    @staticmethod
    def test_nb_drones_valid():
        """Valid: First line defines nb_drones correctly"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
end_hub: goal 1 0 [color=green]
connection: start-goal
"""
        # Should parse successfully
        return {"valid": True, "description": "Valid nb_drones definition"}

    @staticmethod
    def test_nb_drones_missing():
        """Invalid: Missing nb_drones declaration"""
        content = """start_hub: start 0 0 [color=green]
end_hub: goal 1 0 [color=green]
connection: start-goal
"""
        return {
            "valid": False,
            "error": "First line must define nb_drones",
            "description": "Missing nb_drones declaration",
        }

    @staticmethod
    def test_nb_drones_not_first_line():
        """Invalid: nb_drones not on first line"""
        content = """start_hub: start 0 0 [color=green]
nb_drones: 4
end_hub: goal 1 0 [color=green]
connection: start-goal
"""
        return {
            "valid": False,
            "error": "nb_drones must be first line",
            "description": "nb_drones not on first line",
        }

    @staticmethod
    def test_nb_drones_invalid_format():
        """Invalid: nb_drones format incorrect"""
        content = """nb_drones = 4
start_hub: start 0 0 [color=green]
end_hub: goal 1 0 [color=green]
connection: start-goal
"""
        return {
            "valid": False,
            "error": "Invalid nb_drones format (expected 'nb_drones: <int>')",
            "line": 1,
            "description": "Wrong separator (= instead of :)",
        }

    @staticmethod
    def test_nb_drones_non_integer():
        """Invalid: nb_drones is not an integer"""
        content = """nb_drones: four
start_hub: start 0 0 [color=green]
end_hub: goal 1 0 [color=green]
connection: start-goal
"""
        return {
            "valid": False,
            "error": "nb_drones must be a positive integer",
            "line": 1,
            "description": "Non-integer value for nb_drones",
        }

    @staticmethod
    def test_nb_drones_zero():
        """Invalid: nb_drones is zero"""
        content = """nb_drones: 0
start_hub: start 0 0 [color=green]
end_hub: goal 1 0 [color=green]
connection: start-goal
"""
        return {
            "valid": False,
            "error": "nb_drones must be a positive integer (> 0)",
            "line": 1,
            "description": "Zero drones",
        }

    @staticmethod
    def test_nb_drones_negative():
        """Invalid: nb_drones is negative"""
        content = """nb_drones: -5
start_hub: start 0 0 [color=green]
end_hub: goal 1 0 [color=green]
connection: start-goal
"""
        return {
            "valid": False,
            "error": "nb_drones must be a positive integer (> 0)",
            "line": 1,
            "description": "Negative number of drones",
        }

    @staticmethod
    def test_nb_drones_large_value():
        """Valid: Large but valid nb_drones"""
        content = """nb_drones: 1000
start_hub: start 0 0 [color=green]
end_hub: goal 1 0 [color=green]
connection: start-goal
"""
        return {"valid": True, "description": "Large number of drones (1000)"}

    # ========== VII.4.2: Start and End Hubs ==========

    @staticmethod
    def test_exactly_one_start_hub():
        """Valid: Exactly one start_hub"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: mid 1 0
end_hub: goal 2 0 [color=green]
connection: start-mid
connection: mid-goal
"""
        return {"valid": True, "description": "Exactly one start_hub"}

    @staticmethod
    def test_no_start_hub():
        """Invalid: No start_hub defined"""
        content = """nb_drones: 4
hub: start 0 0 [color=green]
hub: goal 1 0 [color=green]
connection: start-goal
"""
        return {
            "valid": False,
            "error": "Exactly one start_hub must be defined",
            "description": "Missing start_hub",
        }

    @staticmethod
    def test_multiple_start_hubs():
        """Invalid: Multiple start_hubs"""
        content = """nb_drones: 4
start_hub: start1 0 0 [color=green]
start_hub: start2 1 0 [color=green]
end_hub: goal 2 0 [color=green]
connection: start1-goal
connection: start2-goal
"""
        return {
            "valid": False,
            "error": "Exactly one start_hub must be defined",
            "description": "Multiple start_hubs",
        }

    @staticmethod
    def test_exactly_one_end_hub():
        """Valid: Exactly one end_hub"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: mid 1 0
end_hub: goal 2 0 [color=green]
connection: start-mid
connection: mid-goal
"""
        return {"valid": True, "description": "Exactly one end_hub"}

    @staticmethod
    def test_no_end_hub():
        """Invalid: No end_hub defined"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: goal 1 0 [color=green]
connection: start-goal
"""
        return {
            "valid": False,
            "error": "Exactly one end_hub must be defined",
            "description": "Missing end_hub",
        }

    @staticmethod
    def test_multiple_end_hubs():
        """Invalid: Multiple end_hubs"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
end_hub: goal1 1 0 [color=green]
end_hub: goal2 2 0 [color=green]
connection: start-goal1
connection: start-goal2
"""
        return {
            "valid": False,
            "error": "Exactly one end_hub must be defined",
            "description": "Multiple end_hubs",
        }

    # ========== VII.4.3: Zone Definition ==========

    @staticmethod
    def test_unique_zone_names():
        """Valid: All zone names are unique"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: zone1 1 0
hub: zone2 2 0
end_hub: goal 3 0 [color=green]
connection: start-zone1
connection: zone1-zone2
connection: zone2-goal
"""
        return {"valid": True, "description": "All zones have unique names"}

    @staticmethod
    def test_duplicate_zone_names():
        """Invalid: Duplicate zone names"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: zone1 1 0
hub: zone1 2 0
end_hub: goal 3 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Zone 'zone1' already defined",
            "line": 4,
            "description": "Duplicate zone name",
        }

    @staticmethod
    def test_valid_coordinates():
        """Valid: Valid integer coordinates"""
        content = """nb_drones: 4
start_hub: start -5 -10 [color=green]
hub: zone1 0 0
hub: zone2 100 200
end_hub: goal -99 99 [color=green]
connection: start-zone1
connection: zone1-zone2
connection: zone2-goal
"""
        return {
            "valid": True,
            "description": "Valid integer coordinates (including negative)",
        }

    @staticmethod
    def test_floating_point_coordinates():
        """Invalid: Floating point coordinates"""
        content = """nb_drones: 4
start_hub: start 0.5 1.5 [color=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Coordinates must be integers",
            "line": 2,
            "description": "Floating point coordinates",
        }

    @staticmethod
    def test_missing_coordinates():
        """Invalid: Missing y coordinate"""
        content = """nb_drones: 4
start_hub: start 0 [color=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Zone definition requires name, x, and y coordinates",
            "line": 2,
            "description": "Missing y coordinate",
        }

    @staticmethod
    def test_extra_coordinates():
        """Invalid: Too many coordinates"""
        content = """nb_drones: 4
start_hub: start 0 0 5 [color=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Zone definition has too many elements",
            "line": 2,
            "description": "Extra coordinate value",
        }

    @staticmethod
    def test_zone_names_with_valid_characters():
        """Valid: Zone names with underscores, numbers, letters"""
        content = """nb_drones: 4
start_hub: start_hub_1 0 0 [color=green]
hub: zone_2b 1 0
hub: zone3_c 2 0
end_hub: goal_final_hub 3 0 [color=green]
connection: start_hub_1-zone_2b
connection: zone_2b-zone3_c
connection: zone3_c-goal_final_hub
"""
        return {
            "valid": True,
            "description": "Zone names with underscores and alphanumerics",
        }

    @staticmethod
    def test_zone_names_with_invalid_characters():
        """Invalid: Zone names with spaces or dashes"""
        content = """nb_drones: 4
start_hub: start hub 0 0 [color=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Zone names cannot contain spaces or dashes",
            "line": 2,
            "description": "Zone name with space",
        }

    @staticmethod
    def test_zone_name_with_dash():
        """Invalid: Zone name with dash"""
        content = """nb_drones: 4
start_hub: start-hub 0 0 [color=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-hub-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Zone names cannot contain dashes",
            "line": 2,
            "description": "Zone name with dash",
        }

    # ========== VII.4.4: Zone Types ==========

    @staticmethod
    def test_valid_zone_types():
        """Valid: All zone type values"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green zone=normal]
hub: zone1 1 0 [zone=blocked]
hub: zone2 2 0 [zone=restricted]
hub: zone3 3 0 [zone=priority]
end_hub: goal 4 0 [color=green zone=normal]
connection: start-zone1
connection: zone1-zone2
connection: zone2-zone3
connection: zone3-goal
"""
        return {
            "valid": True,
            "description": "All valid zone types (normal, blocked, restricted, priority)",
        }

    @staticmethod
    def test_invalid_zone_type():
        """Invalid: Unknown zone type"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green zone=fast]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Invalid zone type 'fast'. Must be one of: normal, blocked, restricted, priority",
            "line": 2,
            "description": "Invalid zone type",
        }

    @staticmethod
    def test_multiple_invalid_zone_types():
        """Invalid: Multiple invalid zone types"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green zone=super_fast]
hub: zone1 1 0 [zone=ultra]
end_hub: goal 2 0 [color=green zone=slow]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Invalid zone type",
            "description": "Multiple invalid zone types",
        }

    # ========== VII.4.5: Capacity Values ==========

    @staticmethod
    def test_valid_capacity_values():
        """Valid: Valid positive integer capacities"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green max_drones=4]
hub: zone1 1 0 [max_drones=2]
hub: zone2 2 0 [max_drones=1]
end_hub: goal 3 0 [color=green max_drones=10]
connection: start-zone1
connection: zone1-zone2 [max_link_capacity=3]
connection: zone2-goal [max_link_capacity=1]
"""
        return {
            "valid": True,
            "description": "Valid positive integer capacities",
        }

    @staticmethod
    def test_capacity_zero():
        """Invalid: Capacity value of zero"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green max_drones=0]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Capacity values must be positive integers (> 0)",
            "line": 2,
            "description": "Zone capacity of zero",
        }

    @staticmethod
    def test_capacity_negative():
        """Invalid: Negative capacity value"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green max_drones=-5]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Capacity values must be positive integers",
            "line": 2,
            "description": "Negative zone capacity",
        }

    @staticmethod
    def test_capacity_non_integer():
        """Invalid: Non-integer capacity"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green max_drones=2.5]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Capacity must be an integer",
            "line": 2,
            "description": "Floating point capacity",
        }

    @staticmethod
    def test_link_capacity_negative():
        """Invalid: Negative link capacity"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1 [max_link_capacity=-2]
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Link capacity must be a positive integer",
            "line": 5,
            "description": "Negative link capacity",
        }

    # ========== VII.4.6: Connections ==========

    @staticmethod
    def test_valid_connections():
        """Valid: Valid connections between defined zones"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: zone1 1 0
hub: zone2 2 0
end_hub: goal 3 0 [color=green]
connection: start-zone1
connection: zone1-zone2
connection: zone2-goal
"""
        return {"valid": True, "description": "Valid connections"}

    @staticmethod
    def test_connection_to_undefined_zone():
        """Invalid: Connection to undefined zone"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: zone1 1 0
end_hub: goal 3 0 [color=green]
connection: start-undefined_zone
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Connection references undefined zone 'undefined_zone'",
            "line": 5,
            "description": "Connection to undefined zone",
        }

    @staticmethod
    def test_connection_both_undefined():
        """Invalid: Both zones in connection undefined"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
end_hub: goal 1 0 [color=green]
connection: zone1-zone2
connection: start-goal
"""
        return {
            "valid": False,
            "error": "Connection references undefined zone",
            "description": "Both zones undefined in connection",
        }

    @staticmethod
    def test_duplicate_connection():
        """Invalid: Same connection defined twice"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Connection 'start-zone1' already defined",
            "line": 6,
            "description": "Duplicate connection",
        }

    @staticmethod
    def test_duplicate_connection_reversed():
        """Invalid: Reversed duplicate connection (a-b and b-a)"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-start
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Connection already defined (start-zone1 and zone1-start are duplicates)",
            "line": 6,
            "description": "Reversed duplicate connection",
        }

    @staticmethod
    def test_self_connection():
        """Invalid: Zone connected to itself"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-start
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Self-connections not allowed",
            "line": 5,
            "description": "Zone connected to itself",
        }

    @staticmethod
    def test_connection_missing_hyphen():
        """Invalid: Connection without hyphen separator"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Invalid connection format (expected 'connection: zone1-zone2')",
            "line": 5,
            "description": "Connection without hyphen",
        }

    # ========== VII.4.7: Metadata Syntax ==========

    @staticmethod
    def test_valid_metadata_syntax():
        """Valid: Valid metadata block syntax"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green max_drones=4 zone=priority]
hub: zone1 1 0 [color=blue zone=restricted]
end_hub: goal 2 0 [color=green max_drones=2]
connection: start-zone1 [max_link_capacity=3]
connection: zone1-goal
"""
        return {"valid": True, "description": "Valid metadata block syntax"}

    @staticmethod
    def test_metadata_missing_closing_bracket():
        """Invalid: Missing closing bracket"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Metadata block not properly closed (missing ']')",
            "line": 2,
            "description": "Missing closing bracket",
        }

    @staticmethod
    def test_metadata_missing_opening_bracket():
        """Invalid: Missing opening bracket"""
        content = """nb_drones: 4
start_hub: start 0 0 color=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Metadata block not properly opened (missing '[')",
            "line": 2,
            "description": "Missing opening bracket",
        }

    @staticmethod
    def test_metadata_invalid_key_value_format():
        """Invalid: Invalid key=value syntax"""
        content = """nb_drones: 4
start_hub: start 0 0 [color:green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Invalid metadata format (expected 'key=value')",
            "line": 2,
            "description": "Wrong separator in metadata (: instead of =)",
        }

    @staticmethod
    def test_metadata_missing_value():
        """Invalid: Key without value"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Metadata value cannot be empty",
            "line": 2,
            "description": "Empty metadata value",
        }

    @staticmethod
    def test_metadata_missing_key():
        """Invalid: Value without key"""
        content = """nb_drones: 4
start_hub: start 0 0 [=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Invalid metadata format (expected 'key=value')",
            "line": 2,
            "description": "Empty metadata key",
        }

    @staticmethod
    def test_empty_metadata_block():
        """Invalid: Empty metadata block"""
        content = """nb_drones: 4
start_hub: start 0 0 []
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error": "Empty metadata block",
            "line": 2,
            "description": "Empty metadata block",
        }

    # ========== VII.4.8: Line and Error Reporting ==========

    @staticmethod
    def test_error_reporting_with_line_number():
        """Valid: Errors should include line number"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: zone1 1 0 [zone=invalid_type]
end_hub: goal 2 0 [color=green]
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": False,
            "error_must_include": "line 3",
            "description": "Error reporting includes line number",
        }

    @staticmethod
    def test_error_reporting_includes_cause():
        """Valid: Errors should include specific cause"""
        content = """nb_drones: 4
start_hub: start 0 0 [color=green]
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
connection: start-undefined_zone
connection: zone1-goal
"""
        return {
            "valid": False,
            "error_must_include": "undefined_zone",
            "description": "Error reporting includes specific cause",
        }

    # ========== VII.4.9: Edge Cases ==========

    @staticmethod
    def test_minimal_valid_file():
        """Valid: Minimal valid configuration"""
        content = """nb_drones: 1
start_hub: start 0 0
end_hub: goal 1 0
connection: start-goal
"""
        return {"valid": True, "description": "Minimal valid configuration"}

    @staticmethod
    def test_large_coordinate_values():
        """Valid: Large coordinate values"""
        content = """nb_drones: 4
start_hub: start -999999 -999999 [color=green]
hub: zone1 0 0
hub: zone2 999999 999999
end_hub: goal 1000000 1000000 [color=green]
connection: start-zone1
connection: zone1-zone2
connection: zone2-goal
"""
        return {"valid": True, "description": "Very large coordinate values"}

    @staticmethod
    def test_many_zones():
        """Valid: Many zones"""
        content = """nb_drones: 10
start_hub: start 0 0 [color=green]
"""
        # Add 50 zones
        zones = "\n".join([f"hub: zone{i} {i} 0" for i in range(1, 50)])
        content += zones
        content += "\nend_hub: goal 50 0 [color=green]\n"
        # Add connections
        content += "connection: start-zone1\n"
        for i in range(1, 50):
            content += f"connection: zone{i}-zone{i + 1}\n"
        content += "connection: zone50-goal\n"
        return {"valid": True, "description": "Configuration with 50+ zones"}

    @staticmethod
    def test_whitespace_handling():
        """Valid: Extra whitespace should be handled"""
        content = """nb_drones:    4
start_hub:    start    0    0    [color=green]
hub:    zone1    1    0
end_hub:    goal    2    0    [color=green]
connection:    start-zone1
connection:    zone1-goal
"""
        return {
            "valid": True,
            "description": "Extra whitespace handled correctly",
        }

    @staticmethod
    def test_comment_lines():
        """Valid: Comments should be ignored"""
        content = """# This is a comment
nb_drones: 4
# Another comment
start_hub: start 0 0 [color=green]
# Mid-file comment
hub: zone1 1 0
end_hub: goal 2 0 [color=green]
# Comments at end
connection: start-zone1
connection: zone1-goal
"""
        return {
            "valid": True,
            "description": "Comment lines are properly ignored",
        }

    @staticmethod
    def test_empty_lines():
        """Valid: Empty lines should be handled"""
        content = """nb_drones: 4

start_hub: start 0 0 [color=green]

hub: zone1 1 0

end_hub: goal 2 0 [color=green]

connection: start-zone1

connection: zone1-goal

"""
        return {
            "valid": True,
            "description": "Empty lines are properly handled",
        }

    @staticmethod
    def test_real_world_example():
        """Valid: Real-world example from provided file"""
        content = """nb_drones: 4
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
"""
        return {
            "valid": True,
            "description": "Real-world priority puzzle example",
        }


def generate_test_report():
    """Generate a formatted report of all test cases"""
    suite = ParserTestSuite()
    test_methods = [
        method for method in dir(suite) if method.startswith("test_")
    ]

    report = []
    report.append("=" * 80)
    report.append("PARSER TEST SUITE - Comprehensive Test Cases")
    report.append("=" * 80)
    report.append(f"\nTotal Tests: {len(test_methods)}\n")

    current_section = None
    for method_name in sorted(test_methods):
        method = getattr(suite, method_name)
        result = method()

        # Determine section
        section = None
        if "nb_drones" in method_name:
            section = "VII.4.1: nb_drones Definition"
        elif "start_hub" in method_name or "end_hub" in method_name:
            section = "VII.4.2: Start and End Hubs"
        elif "zone" in method_name and "type" not in method_name:
            section = "VII.4.3: Zone Definition"
        elif (
            "type" in method_name
            or "invalid" in method_name
            and "zone" in method_name
        ):
            section = "VII.4.4: Zone Types"
        elif "capacity" in method_name:
            section = "VII.4.5: Capacity Values"
        elif "connection" in method_name:
            section = "VII.4.6: Connections"
        elif "metadata" in method_name:
            section = "VII.4.7: Metadata Syntax"
        elif "error" in method_name:
            section = "VII.4.8: Error Reporting"
        else:
            section = "VII.4.9: Edge Cases"

        if section != current_section:
            report.append(f"\n{section}")
            report.append("-" * 80)
            current_section = section

        status = "✓ VALID" if result.get("valid") else "✗ INVALID"
        report.append(f"\n{method_name}")
        report.append(f"  Status: {status}")
        report.append(f"  Description: {result.get('description', 'N/A')}")
        if result.get("error"):
            report.append(f"  Expected Error: {result.get('error')}")
        if result.get("line"):
            report.append(f"  Line: {result.get('line')}")

    report.append("\n" + "=" * 80)
    return "\n".join(report)


if __name__ == "__main__":
    print(generate_test_report())
