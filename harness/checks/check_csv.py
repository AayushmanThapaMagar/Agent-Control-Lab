import csv
import sys
from pathlib import Path

EXPECTED_ROWS = [
    ["customer", "note"],
    ["Acme", "Routine follow-up"],
    ["Beta, Ltd", "Requested 'priority' support"]
]

def main() -> int: 
    if len(sys.argv) != 2:
        print("Usage: python3 harness/check_csv.py OUTPUT_FILE")
        return 2
    
    output_path = Path(sys.argv[1])
    
    with output_path.open(
        "r", 
        encoding="utf-8",
        newline="", 
    ) as handle: 
        actual_rows = list(csv.reader(handle))
        
        if actual_rows != EXPECTED_ROWS: 
            print("FAIL: CSV fields changed during export.")
            print(f"Expected: {EXPECTED_ROWS}")
            print(f"Actual: {actual_rows}")
            return 1
        
        print("PASS: CSV fields preserved.")
        return 0 

if __name__ == "__main__": 
    raise SystemExit(main())