# Cybersecurity Tabletop Exercise Database

A comprehensive SQLite database solution for storing and managing cybersecurity tabletop exercises across multiple themes.

## Project Overview

This project provides two main scripts:

### 1. Database Creator Script (`tabletop-database-script.py`)

Creates and populates a SQLite database with:

- 8 distinct themes (Original Cybersecurity, Dungeons & Dragons, Cyberpunk, Gundam, Wild West, Space Exploration, Superhero, Medieval, Horror, and Heist)
- 15 tabletop exercises distributed across themes with their full content

The script provides core functions for:

- Creating the database structure
- Populating with initial themed content
- Retrieving exercises by theme
- Searching across all content
- Exporting exercises to Markdown
- Basic database statistics

### 2. Advanced Database Usage Script (`database-usage-script.py`)

Provides a comprehensive set of tools to interact with the database:

1. **Browse and View Features**:
   - List all themes with exercise counts
   - List exercises by theme
   - View detailed exercise content
   - Search across all exercises by keyword

2. **Export Functions**:
   - Export individual exercises (MD or JSON format)
   - Export all exercises from a specific theme
   - Export the entire collection to a designated directory

3. **Management Functions**:
   - Add new themes with descriptions
   - Add new exercises with content from files or direct input
   - Generate comprehensive statistics about database contents

4. **User Interface Options**:
   - Interactive menu for guided usage
   - Command-line interface for scripted operations

## Usage Examples

### Interactive Mode

Run the script without arguments to access the menu-driven interface:

```bash
python database-usage-script.py
```

This launches an interactive menu where you can select operations.

### Command Line Mode

Execute specific operations directly from the command line:

```bash
python database-usage-script.py list-themes
python database-usage-script.py list-exercises <theme_id>
python database-usage-script.py search "horror"
python database-usage-script.py view <exercise_id>
python database-usage-script.py export-all md
python database-usage-script.py export-theme <theme_id> json
python database-usage-script.py stats
```

### Available Commands

- `list-themes`: Display all available themes
- `list-exercises <theme_id>`: Show exercises for a specific theme
- `search <search_term>`: Find exercises by content or title
- `view <exercise_id>`: Display exercise content
- `export-all [md|json]`: Export all exercises (default: md)
- `export-theme <theme_id> [md|json]`: Export theme exercises (default: md)
- `stats`: Generate database statistics
- `help`: Display usage information

## Project Structure

```
cybersec-ttx/
├── tabletop-database-script.py    # Database creation script
├── database-usage-script.py       # Database management tool
├── tabletop_exercises.db          # SQLite database (generated)
├── exports/                       # Export directory (created on demand)
└── assets/                        # Exercise content sources
    └── kb/                        # Knowledge base with exercise content
        ├── cyberpunk-security-exercise.md
        ├── cybersecurity-tabletop-exercise.md
        ├── dnd-cybersecurity-exercise.md
        └── ...
```

## Key Features

- **Organized Storage**: All themed exercises properly categorized
- **Easy Retrieval**: Find exercises by theme, title, or content
- **Flexible Export**: Generate output in your preferred format
- **Extensible**: Add new themes and exercises as needed
- **Statistical Analysis**: Understand your collection's composition
- **Multiple Interfaces**: Command-line or menu-driven operation

This solution enables efficient management of cybersecurity tabletop exercises with diverse themes, making it easier to organize, find, and utilize content for security training and testing.
