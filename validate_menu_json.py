#!/usr/bin/env python3
import json
import sys

def validate_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            json.loads(content)
        print("✅ JSON is valid!")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {e}")
        print(f"Line: {e.lineno}, Column: {e.colno}")
        print(f"Position: {e.pos}")
        
        # Show context around the error
        lines = content.split('\n')
        start_line = max(0, e.lineno - 3)
        end_line = min(len(lines), e.lineno + 2)
        
        print("\nContext around error:")
        for i in range(start_line, end_line):
            marker = ">>> " if i == e.lineno - 1 else "    "
            print(f"{marker}{i+1:3d}: {lines[i]}")
        
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

if __name__ == "__main__":
    file_path = "templates/layout/partials/menu/vertical/json/vertical_menu.json"
    validate_json_file(file_path)