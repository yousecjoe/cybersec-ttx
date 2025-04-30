import sqlite3
import os
from tabletop_database_script import export_exercise_to_md, get_all_themes, get_exercises_by_theme, get_exercise_content

def main():
    # Connect to the database
    conn = sqlite3.connect('tabletop_exercises.db')
    cursor = conn.cursor()
    
    # Export an exercise
    print("Exporting exercises...")
    
    # List all themes and exercises
    themes = get_all_themes(cursor)
    for theme_id, theme_name, theme_desc in themes:
        print(f"Theme: {theme_name}")
        exercises = get_exercises_by_theme(cursor, theme_id)
        
        for ex_id, ex_title, ex_desc in exercises:
            # Export the exercise
            filename = export_exercise_to_md(cursor, ex_id, 'exports')
            if filename:
                file_size = os.path.getsize(filename)
                print(f"  * Exported: {ex_title} (ID: {ex_id}) to {filename} ({file_size} bytes)")
    
    # Close the connection
    conn.close()
    print("\nExport completed successfully!")

if __name__ == "__main__":
    main()
