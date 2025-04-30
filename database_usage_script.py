import sqlite3
import os
import json
import sys

def connect_to_database(db_name='tabletop_exercises.db'):
    """Connect to the SQLite database."""
    if not os.path.exists(db_name):
        print(f"Error: Database file '{db_name}' not found. Please run the database creation script first.")
        sys.exit(1)
        
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def theme_exists(conn, theme_id):
    """Check if a theme exists in the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM themes WHERE id = ?", (theme_id,))
    return cursor.fetchone() is not None

def get_theme_name(conn, theme_id):
    """Get the name of a theme by ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM themes WHERE id = ?", (theme_id,))
    theme = cursor.fetchone()
    return theme['name'] if theme else None

def create_safe_filename(title):
    """Create a safe filename from a title."""
    return title.replace(" ", "_").replace(":", "").replace("&", "and")

def ensure_directory_exists(directory):
    """Create a directory if it does not exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_exercise_data(conn, exercise_id):
    """Get exercise data by ID."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.title, e.content, t.name as theme_name
        FROM exercises e
        JOIN themes t ON e.theme_id = t.id
        WHERE e.id = ?
    """, (exercise_id,))
    return cursor.fetchone()

def export_exercise_content(exercise, output_path, format='md'):
    """Export exercise content to a file in the specified format."""
    if format.lower() == 'md':
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(exercise['content'])
    elif format.lower() == 'json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'id': exercise['id'],
                'title': exercise['title'],
                'theme': exercise['theme_name'],
                'content': exercise['content']
            }, f, indent=2)
    else:
        return None
    
    return output_path

def list_all_themes(conn):
    """List all available themes in the database."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.name, t.description, COUNT(e.id) as exercise_count 
        FROM themes t
        LEFT JOIN exercises e ON t.id = e.theme_id
        GROUP BY t.id
        ORDER BY t.name
    """)
    themes = cursor.fetchall()
    
    print("\n=== AVAILABLE THEMES ===")
    for theme in themes:
        print(f"ID: {theme['id']} - {theme['name']} ({theme['exercise_count']} exercises)")
        print(f"   Description: {theme['description']}")
    return themes

def list_exercises_by_theme(conn, theme_id):
    """List all exercises for a specific theme."""
    theme_name = get_theme_name(conn, theme_id)
    if not theme_name:
        print(f"Theme with ID {theme_id} not found.")
        return []
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, description 
        FROM exercises 
        WHERE theme_id = ? 
        ORDER BY title
    """, (theme_id,))
    exercises = cursor.fetchall()
    
    print(f"\n=== EXERCISES FOR THEME: {theme_name} ===")
    if not exercises:
        print("No exercises found for this theme.")
    else:
        for exercise in exercises:
            print(f"ID: {exercise['id']} - {exercise['title']}")
            print(f"   Description: {exercise['description']}\n")
    return exercises

def view_exercise_content(conn, exercise_id):
    """View the full content of a specific exercise."""
    exercise = get_exercise_data(conn, exercise_id)
    
    if not exercise:
        print(f"Exercise with ID {exercise_id} not found.")
        return None
    
    print(f"\n=== EXERCISE: {exercise['title']} (Theme: {exercise['theme_name']}) ===")
    print("First 500 characters of content:")
    content_preview = exercise['content'][:500]
    if len(exercise['content']) > 500:
        content_preview += "..."
    print(content_preview + "\n")
    return exercise

def export_exercise_to_file(conn, exercise_id, format='md'):
    """Export an exercise to a file (markdown or JSON)."""
    exercise = get_exercise_data(conn, exercise_id)
    
    if not exercise:
        print(f"Exercise with ID {exercise_id} not found.")
        return None
    
    # Create exports directory if it doesn't exist
    ensure_directory_exists('exports')
    
    # Create a safe filename
    safe_title = create_safe_filename(exercise['title'])
    output_path = f"exports/{safe_title}.{format.lower()}"
    
    if export_exercise_content(exercise, output_path, format):
        print(f"Exercise exported to {output_path}")
        return output_path
    else:
        print(f"Unsupported format: {format}")
        return None

def search_exercises(conn, search_term):
    """Search for exercises by title, description, or content."""
    cursor = conn.cursor()
    search_pattern = f"%{search_term}%"
    cursor.execute("""
        SELECT e.id, e.title, e.description, t.name as theme_name
        FROM exercises e
        JOIN themes t ON e.theme_id = t.id
        WHERE e.title LIKE ? 
           OR e.description LIKE ? 
           OR e.content LIKE ?
        ORDER BY t.name, e.title
    """, (search_pattern, search_pattern, search_pattern))
    results = cursor.fetchall()
    
    print(f"\n=== SEARCH RESULTS FOR: '{search_term}' ===")
    if not results:
        print("No matching exercises found.")
    else:
        for result in results:
            print(f"ID: {result['id']} - {result['title']} (Theme: {result['theme_name']})")
            print(f"   Description: {result['description']}\n")
    return results

def export_all_exercises(conn, format='md'):
    """Export all exercises to individual files."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM exercises")
    exercise_ids = [row['id'] for row in cursor.fetchall()]
    
    exported_files = []
    for exercise_id in exercise_ids:
        filename = export_exercise_to_file(conn, exercise_id, format)
        if filename:
            exported_files.append(filename)
    
    print(f"\nExported {len(exported_files)} exercises to the 'exports' directory.")
    return exported_files

def export_theme_exercises(conn, theme_id, format='md'):
    """Export all exercises for a specific theme."""
    theme_name = get_theme_name(conn, theme_id)
    if not theme_name:
        print(f"Theme with ID {theme_id} not found.")
        return []
    
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM exercises WHERE theme_id = ?", (theme_id,))
    exercise_ids = [row['id'] for row in cursor.fetchall()]
    
    if not exercise_ids:
        print(f"No exercises found for theme: {theme_name}")
        return []
    
    # Create theme-specific directory
    theme_dir = f"exports/{theme_name.replace(' ', '_')}"
    ensure_directory_exists(theme_dir)
    
    exported_files = []
    for exercise_id in exercise_ids:
        exercise = get_exercise_data(conn, exercise_id)
        
        if exercise:
            safe_title = create_safe_filename(exercise['title'])
            output_path = f"{theme_dir}/{safe_title}.{format.lower()}"
            
            if export_exercise_content(exercise, output_path, format):
                exported_files.append(output_path)
                print(f"Exported: {output_path}")
    
    print(f"\nExported {len(exported_files)} exercises for theme '{theme_name}' to '{theme_dir}'")
    return exported_files

def add_new_exercise(conn, theme_id, title, description, content):
    """Add a new exercise to the database."""
    if not theme_exists(conn, theme_id):
        print(f"Theme with ID {theme_id} not found.")
        return False
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO exercises (theme_id, title, description, content)
        VALUES (?, ?, ?, ?)
    """, (theme_id, title, description, content))
    conn.commit()
    
    print(f"New exercise '{title}' added successfully with ID {cursor.lastrowid}")
    return cursor.lastrowid

def add_new_theme(conn, name, description):
    """Add a new theme to the database."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO themes (name, description)
        VALUES (?, ?)
    """, (name, description))
    conn.commit()
    
    print(f"New theme '{name}' added successfully with ID {cursor.lastrowid}")
    return cursor.lastrowid

def generate_statistics(conn):
    """Generate and display statistics about the database contents."""
    cursor = conn.cursor()
    
    # Count themes and exercises
    cursor.execute("SELECT COUNT(*) FROM themes")
    theme_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM exercises")
    exercise_count = cursor.fetchone()[0]
    
    # Get exercises per theme
    cursor.execute("""
        SELECT t.name, COUNT(e.id) as count
        FROM themes t
        LEFT JOIN exercises e ON t.id = e.theme_id
        GROUP BY t.id
        ORDER BY count DESC
    """)
    theme_stats = cursor.fetchall()
    
    # Find most common words in exercise titles
    cursor.execute("SELECT title FROM exercises")
    titles = cursor.fetchall()
    
    # Simple word frequency analysis
    words = {}
    for title in titles:
        for word in title['title'].lower().split():
            # Skip small words
            if len(word) <= 3:
                continue
            # Remove punctuation
            word = word.strip('.:,;!?()-')
            if word in words:
                words[word] += 1
            else:
                words[word] = 1
    
    # Sort by frequency
    common_words = sorted(words.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("\n=== DATABASE STATISTICS ===")
    print(f"Total Themes: {theme_count}")
    print(f"Total Exercises: {exercise_count}")
    
    if theme_count > 0:
        print(f"Average Exercises per Theme: {exercise_count/theme_count:.1f}")
    
    print("\nExercises by Theme:")
    for theme in theme_stats:
        print(f"- {theme['name']}: {theme['count']} exercises")
    
    print("\nMost Common Words in Exercise Titles:")
    for word, count in common_words:
        print(f"- {word}: {count} occurrences")
    
    return {
        'theme_count': theme_count,
        'exercise_count': exercise_count,
        'theme_stats': theme_stats,
        'common_words': common_words
    }

def get_multiline_content():
    """Get multiline content from user input."""
    print("Enter content (type '###END###' on a new line when finished):")
    content_lines = []
    while True:
        line = input()
        if line == '###END###':
            break
        content_lines.append(line)
    return '\n'.join(content_lines)

def get_file_content(filename):
    """Get content from a file."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print(f"File not found: {filename}")
        return None

def handle_command_arguments(args):
    """Handle command line arguments."""
    commands = {
        "list-themes": lambda conn, args: list_all_themes(conn),
        "list-exercises": lambda conn, args: list_exercises_by_theme(conn, args[2]) if len(args) > 2 else print("Missing theme_id argument"),
        "search": lambda conn, args: search_exercises(conn, args[2]) if len(args) > 2 else print("Missing search_term argument"),
        "export-all": lambda conn, args: export_all_exercises(conn, args[2] if len(args) > 2 else "md"),
        "export-theme": lambda conn, args: export_theme_exercises(conn, args[2], args[3] if len(args) > 3 else "md") if len(args) > 2 else print("Missing theme_id argument"),
        "stats": lambda conn, args: generate_statistics(conn),
        "view": lambda conn, args: view_exercise_content(conn, args[2]) if len(args) > 2 else print("Missing exercise_id argument"),
        "help": lambda conn, args: print_help(),
    }
    
    if len(args) > 1:
        command = args[1].lower()
        if command in commands:
            conn = connect_to_database()
            commands[command](conn, args)
            conn.close()
        else:
            print(f"Unknown command: {command}")
            print_help()
    else:
        interactive_menu()

def print_help():
    """Display command line usage help."""
    print("Usage examples:")
    print("  python database_usage.py list-themes")
    print("  python database_usage.py list-exercises <theme_id>")
    print("  python database_usage.py search <search_term>")
    print("  python database_usage.py view <exercise_id>")
    print("  python database_usage.py export-all [md|json]")
    print("  python database_usage.py export-theme <theme_id> [md|json]")
    print("  python database_usage.py stats")
    print("  python database_usage.py help")

def interactive_menu():
    """Run an interactive menu for the database."""
    conn = connect_to_database()
    
    menu_options = {
        '0': {'text': 'Exit', 'handler': lambda: None},
        '1': {'text': 'List all themes', 'handler': lambda: list_all_themes(conn)},
        '2': {'text': 'List exercises for a theme', 'handler': lambda: list_exercises_by_theme(conn, input("Enter theme ID: "))},
        '3': {'text': 'View exercise content', 'handler': lambda: view_exercise_content(conn, input("Enter exercise ID: "))},
        '4': {'text': 'Export exercise to file', 'handler': lambda: export_exercise_to_file(
                conn, 
                input("Enter exercise ID: "), 
                input("Export format (md/json): ").lower()
            )},
        '5': {'text': 'Export all exercises for a theme', 'handler': lambda: export_theme_exercises(
                conn, 
                input("Enter theme ID: "), 
                input("Export format (md/json): ").lower()
            )},
        '6': {'text': 'Export all exercises', 'handler': lambda: export_all_exercises(
                conn, 
                input("Export format (md/json): ").lower()
            )},
        '7': {'text': 'Search exercises', 'handler': lambda: search_exercises(
                conn, 
                input("Enter search term: ")
            )},
        '8': {'text': 'Add new theme', 'handler': lambda: add_new_theme(
                conn, 
                input("Enter theme name: "), 
                input("Enter theme description: ")
            )},
        '9': {'text': 'Add new exercise', 'handler': lambda: add_new_exercise_interactive(conn)},
        '10': {'text': 'Generate database statistics', 'handler': lambda: generate_statistics(conn)}
    }
    
    while True:
        print("\n=== TABLETOP EXERCISE DATABASE MENU ===")
        for key, option in menu_options.items():
            print(f"{key}. {option['text']}")
        
        choice = input(f"\nEnter your choice (0-{max([int(k) for k in menu_options.keys()])}): ")
        
        if choice in menu_options:
            if choice == '0':
                break
            menu_options[choice]['handler']()
        else:
            print("Invalid choice. Please try again.")
    
    conn.close()
    print("Database connection closed. Goodbye!")

def add_new_exercise_interactive(conn):
    """Interactive function to add a new exercise."""
    list_all_themes(conn)
    theme_id = input("Enter theme ID: ")
    title = input("Enter exercise title: ")
    description = input("Enter exercise description: ")
    
    content_choice = input("Enter content directly (d) or from file (f)? ").lower()
    if content_choice == 'f':
        filename = input("Enter filename to import content from: ")
        content = get_file_content(filename)
        if content is None:
            return
    else:
        content = get_multiline_content()
    
    add_new_exercise(conn, theme_id, title, description, content)

# Main entry point
if __name__ == "__main__":
    handle_command_arguments(sys.argv)
