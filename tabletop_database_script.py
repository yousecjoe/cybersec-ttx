import sqlite3
import os
import pathlib
from typing import Dict, List, Optional, Tuple, Any, Union


def get_all_themes(cursor):
    """Get all available themes."""
    cursor.execute("SELECT id, name, description FROM themes ORDER BY name")
    return cursor.fetchall()


def get_exercises_by_theme(cursor, theme_id):
    """Get all exercises for a specific theme."""
    cursor.execute("SELECT id, title, description FROM exercises WHERE theme_id = ?", (theme_id,))
    return cursor.fetchall()


def get_exercise_content(cursor, exercise_id):
    """Get the full content of a specific exercise."""
    cursor.execute("SELECT title, content FROM exercises WHERE id = ?", (exercise_id,))
    return cursor.fetchone()


def export_exercise_to_md(cursor, exercise_id, output_dir="exports"):
    """Export an exercise to Markdown file."""
    exercise = get_exercise_content(cursor, exercise_id)
    if not exercise:
        return False
    
    title, content = exercise
    
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a safe filename
    safe_title = title.replace(" ", "_").replace(":", "").replace("&", "and")
    filename = os.path.join(output_dir, f"{safe_title}.md")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename


def export_all_exercises(cursor, output_dir="exports"):
    """Export all exercises to Markdown files."""
    cursor.execute("SELECT id FROM exercises")
    exercise_ids = [row[0] for row in cursor.fetchall()]
    
    exported_files = []
    for exercise_id in exercise_ids:
        filename = export_exercise_to_md(cursor, exercise_id, output_dir)
        if filename:
            exported_files.append(filename)
    
    return exported_files


def search_exercises(cursor, search_term):
    """Search for exercises by title or content."""
    cursor.execute(
        """
        SELECT e.id, e.title, e.description, t.name as theme
        FROM exercises e
        JOIN themes t ON e.theme_id = t.id
        WHERE e.title LIKE ? OR e.description LIKE ? OR e.content LIKE ?
        """,
        (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
    )
    return cursor.fetchall()


def get_theme_statistics(cursor):
    """Get statistics about themes and exercise counts."""
    cursor.execute(
        """
        SELECT t.name, COUNT(e.id) as exercise_count
        FROM themes t
        LEFT JOIN exercises e ON t.id = e.theme_id
        GROUP BY t.name
        ORDER BY exercise_count DESC
        """
    )
    return cursor.fetchall()


def add_exercise(conn, cursor, theme_name, title, description, content):
    """Add a new exercise to the database."""
    # Check if theme exists, create if not
    cursor.execute("SELECT id FROM themes WHERE name = ?", (theme_name,))
    theme_result = cursor.fetchone()
    
    if theme_result:
        theme_id = theme_result[0]
    else:
        # Need theme description
        theme_description = f"A {theme_name.lower()}-themed cybersecurity exercise"
        cursor.execute(
            "INSERT INTO themes (name, description) VALUES (?, ?)",
            (theme_name, theme_description)
        )
        theme_id = cursor.lastrowid
    
    # Insert the exercise
    cursor.execute(
        "INSERT INTO exercises (theme_id, title, description, content) VALUES (?, ?, ?, ?)",
        (theme_id, title, description, content)
    )
    conn.commit()
    return cursor.lastrowid


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


def create_exercise_data_from_files() -> List[Dict[str, Any]]:
    """Create exercise data by reading content from files."""
    exercise_data = []
    theme_map = map_exercise_files()
    kb_dir = "assets/kb"
    
    for theme_key, theme_info in theme_map.items():
        for file_name in theme_info["files"]:
            file_path = os.path.join(kb_dir, file_name)
            
            if os.path.exists(file_path):
                content = read_markdown_file(file_path)
                if content:
                    metadata = extract_exercise_metadata(content)
                    
                    theme_name = theme_info.get("name", "")
                    theme_description = theme_info.get("description", "")
                    
                    exercise_data.append({
                        "theme_name": theme_name,
                        "theme_description": theme_description,
                        "title": metadata["title"],
                        "description": metadata["description"],
                        "content": content,
                        "file_path": file_path  # Store source file for reference
                    })
            else:
                print(f"Warning: File not found: {file_path}")
    
    return exercise_data


def main():
    """Main function to create and populate the database."""
    # Create or connect to the SQLite database
    conn = sqlite3.connect('tabletop_exercises.db')
    cursor = conn.cursor()

    # Create the tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS themes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create exercises table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        theme_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (theme_id) REFERENCES themes (id)
    )
    ''')
    
    # Check if source_file column exists, add it if it doesn't
    cursor.execute("PRAGMA table_info(exercises)")
    columns = [info[1] for info in cursor.fetchall()]
    if "source_file" not in columns:
        try:
            cursor.execute("ALTER TABLE exercises ADD COLUMN source_file TEXT")
            print("Added 'source_file' column to exercises table")
        except sqlite3.OperationalError as e:
            print(f"Note: {e}")

    # Generate exercise data by reading from markdown files
    exercise_data = create_exercise_data_from_files()

    # Insert the data
    for exercise in exercise_data:
        # First, check if the theme already exists
        cursor.execute("SELECT id FROM themes WHERE name = ?", (exercise["theme_name"],))
        theme_result = cursor.fetchone()
        
        if theme_result:
            theme_id = theme_result[0]
        else:
            # Insert the theme
            cursor.execute(
                "INSERT INTO themes (name, description) VALUES (?, ?)",
                (exercise["theme_name"], exercise["theme_description"])
            )
            theme_id = cursor.lastrowid
        
        # Check if this exercise already exists to avoid duplicates
        cursor.execute(
            "SELECT id FROM exercises WHERE theme_id = ? AND title = ?", 
            (theme_id, exercise["title"])
        )
        existing_exercise = cursor.fetchone()
        
        if not existing_exercise:
            # Check if source_file column exists before inserting
            cursor.execute("PRAGMA table_info(exercises)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if "source_file" in columns:
                # Insert with source_file
                cursor.execute(
                    "INSERT INTO exercises (theme_id, title, description, content, source_file) VALUES (?, ?, ?, ?, ?)",
                    (
                        theme_id, 
                        exercise["title"], 
                        exercise["description"], 
                        exercise["content"],
                        exercise.get("file_path", "")
                    )
                )
            else:
                # Insert without source_file
                cursor.execute(
                    "INSERT INTO exercises (theme_id, title, description, content) VALUES (?, ?, ?, ?)",
                    (
                        theme_id, 
                        exercise["title"], 
                        exercise["description"], 
                        exercise["content"]
                    )
                )
    
    # After ALL data is inserted and processed, print information ONCE
    print("Database created with the following themes and exercises:")
    themes = get_all_themes(cursor)
    for theme_id, theme_name, theme_desc in themes:
        print(f"- {theme_name}")
        exercises = get_exercises_by_theme(cursor, theme_id)
        for ex_id, ex_title, ex_desc in exercises:
            print(f"  * {ex_title}")

    # Print statistics ONLY ONCE after all operations
    print("\nExercise count by theme:")
    stats = get_theme_statistics(cursor)
    for theme_name, count in stats:
        print(f"- {theme_name}: {count} exercises")

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("\nDatabase creation completed successfully!")
    print("You can now use the provided functions to retrieve and export exercises.")


if __name__ == "__main__":
    main()
