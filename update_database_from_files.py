import sqlite3
import os
import pathlib
from typing import Dict, List, Any


def read_markdown_file(file_path: str) -> str:
    """Read content from a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""


def extract_exercise_metadata(content: str) -> Dict[str, str]:
    """Extract metadata (title, description) from exercise content."""
    metadata = {"title": "", "description": ""}
    
    # Extract title from the first heading
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            metadata["title"] = line[2:].strip()
            break
    
    # Extract description from objective line if available
    for i, line in enumerate(lines):
        if "objective:" in line.lower():
            metadata["description"] = line.split(":", 1)[1].strip()
            break
    
    # If no explicit description found, use first few lines
    if not metadata["description"] and len(lines) > 5:
        # Find first non-empty line after title as fallback description
        for line in lines[1:10]:
            if line.strip() and not line.startswith('#') and len(line) > 20:
                metadata["description"] = line.strip()
                break
    
    return metadata


def map_exercise_files() -> Dict[str, Dict[str, Any]]:
    """Map exercise files to themes."""
    kb_dir = "assets/kb"
    theme_map = {
        "original_cybersecurity": {
            "name": "Original Cybersecurity",
            "description": "A standard cybersecurity tabletop exercise for MSSPs",
            "files": ["cybersecurity-tabletop-exercise.md"]
        },
        "dungeons_dragons": {
            "name": "Dungeons & Dragons",
            "description": "A fantasy-themed cybersecurity exercise using D&D elements",
            "files": ["dnd-cybersecurity-exercise.md"]
        },
        "cyberpunk": {
            "name": "Cyberpunk",
            "description": "A cyberpunk-themed security exercise set in a dystopian future",
            "files": ["cyberpunk-security-exercise.md"]
        },
        "gundam": {
            "name": "Gundam",
            "description": "A Gundam-themed security exercise set in space with competing factions",
            "files": ["gundam-security-exercise.md"]
        },
        "wild_west": {
            "name": "Wild West",
            "description": "A Wild West-themed security exercise set in the frontier days",
            "files": ["wildwest-security-exercise.md"]
        },
        "space_exploration": {
            "name": "Space Exploration",
            "description": "A space-themed cybersecurity exercise with interplanetary elements",
            "files": ["space-exploration-exercise1.md", "space-exploration-exercise2.md"]
        },
        "superhero": {
            "name": "Superhero",
            "description": "A superhero-themed cybersecurity exercise with metahuman elements",
            "files": ["superhero-exercise1.md", "superhero-exercise2.md"]
        },
        "medieval": {
            "name": "Medieval",
            "description": "A medieval-themed cybersecurity exercise set in a fantasy kingdom",
            "files": ["medieval-exercise1.md", "medieval-exercise2.md"]
        },
        "horror": {
            "name": "Horror",
            "description": "A horror-themed cybersecurity exercise with psychological and supernatural elements",
            "files": ["horror-exercise1.md", "horror-exercise2.md"]
        },
        "heist": {
            "name": "Heist",
            "description": "A heist-themed cybersecurity exercise with elaborate criminal plots",
            "files": ["heist-exercise1.md", "heist-exercise2.md"]
        }
    }
    
    return theme_map


def update_database_from_files():
    """Update the database with content from markdown files."""
    # Connect to the database
    conn = sqlite3.connect('tabletop_exercises.db')
    cursor = conn.cursor()
    
    # Get theme mapping
    theme_map = map_exercise_files()
    kb_dir = "assets/kb"
    
    # Store updates for reporting
    updates = {
        "full_content_updates": 0,
        "new_exercises": 0,
        "truncated_exercises": []
    }
    
    print("Checking for exercises with truncated content...")
    
    # Find all exercises with truncated content
    cursor.execute("""
        SELECT id, theme_id, title, LENGTH(content) as content_length
        FROM exercises
        WHERE content LIKE '%[... content truncated for brevity ...]%'
    """)
    truncated_exercises = cursor.fetchall()
    
    if truncated_exercises:
        print(f"Found {len(truncated_exercises)} exercises with truncated content.")
        for ex_id, _, title, length in truncated_exercises:
            updates["truncated_exercises"].append({"id": ex_id, "title": title})
            print(f"  ID {ex_id}: {title} ({length} bytes)")
    else:
        print("No truncated content found in the database.")
    
    print("\nUpdating database from markdown files...")
    
    # Process all theme files
    for theme_key, theme_info in theme_map.items():
        theme_name = theme_info.get("name", "")
        print(f"\nProcessing theme: {theme_name}")
        
        # Get or create theme
        cursor.execute("SELECT id FROM themes WHERE name = ?", (theme_name,))
        theme_result = cursor.fetchone()
        
        if theme_result:
            theme_id = theme_result[0]
        else:
            theme_description = theme_info.get("description", "")
            cursor.execute(
                "INSERT INTO themes (name, description) VALUES (?, ?)",
                (theme_name, theme_description)
            )
            theme_id = cursor.lastrowid
            print(f"  Created new theme: {theme_name}")
        
        # Process each file for this theme
        for file_name in theme_info.get("files", []):
            file_path = os.path.join(kb_dir, file_name)
            
            if not os.path.exists(file_path):
                print(f"  Warning: File not found: {file_path}")
                continue
            
            # Read file content
            content = read_markdown_file(file_path)
            if not content:
                print(f"  Error: Could not read content from {file_path}")
                continue
            
            # Extract metadata
            metadata = extract_exercise_metadata(content)
            title = metadata["title"]
            description = metadata["description"]
            
            print(f"  Processing: {title}")
            
            # Check if this exercise exists
            cursor.execute(
                "SELECT id, content FROM exercises WHERE theme_id = ? AND title = ?", 
                (theme_id, title)
            )
            existing_exercise = cursor.fetchone()
            
            if existing_exercise:
                exercise_id, existing_content = existing_exercise
                
                # Check if content is truncated
                if "[... content truncated for brevity ...]" in existing_content:
                    cursor.execute(
                        "UPDATE exercises SET content = ?, description = ?, source_file = ? WHERE id = ?",
                        (content, description, file_path, exercise_id)
                    )
                    conn.commit()
                    updates["full_content_updates"] += 1
                    print(f"    Updated with full content: {title} (ID: {exercise_id})")
            else:
                # Insert new exercise
                cursor.execute(
                    """
                    INSERT INTO exercises 
                    (theme_id, title, description, content, source_file) 
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (theme_id, title, description, content, file_path)
                )
                conn.commit()
                new_id = cursor.lastrowid
                updates["new_exercises"] += 1
                print(f"    Added new exercise: {title} (ID: {new_id})")
    
    # Print summary
    print("\nDatabase update completed:")
    print(f"  - {updates['full_content_updates']} exercises updated with full content")
    print(f"  - {updates['new_exercises']} new exercises added")
    
    remaining_truncated = []
    if updates["truncated_exercises"]:
        # Check which truncated exercises still exist
        for ex in updates["truncated_exercises"]:
            cursor.execute(
                "SELECT id FROM exercises WHERE id = ? AND content LIKE '%[... content truncated for brevity ...]%'",
                (ex["id"],)
            )
            if cursor.fetchone():
                remaining_truncated.append(ex)
    
    if remaining_truncated:
        print(f"\nWarning: {len(remaining_truncated)} exercises still have truncated content:")
        for ex in remaining_truncated:
            print(f"  - ID {ex['id']}: {ex['title']}")
    
    # Close connection
    conn.close()


if __name__ == "__main__":
    update_database_from_files()
