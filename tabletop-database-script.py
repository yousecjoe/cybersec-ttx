import sqlite3
import json
import os
import datetime

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

# Store the exercise data
exercise_data = [
    # Original exercises from first set
    {
        "theme_name": "Original Cybersecurity",
        "theme_description": "A standard cybersecurity tabletop exercise for MSSPs",
        "title": "Operation Dark Horizon",
        "description": "A cybersecurity tabletop exercise for a managed security service provider to test incident response capabilities during a sophisticated multi-stage attack.",
        "content": """# Operation Dark Horizon: A Cybersecurity Tabletop Exercise for MSSPs

## Exercise Overview

**Title:** Operation Dark Horizon  
**Duration:** 4 hours (recommended)  
**Target Audience:** SOC analysts, incident responders, security engineers, management team  
**Difficulty:** Moderate to Advanced  
**Objective:** Test the organization's incident response capabilities during a sophisticated multi-stage attack targeting both the MSSP and its clients simultaneously.

[... content truncated for brevity ...]

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
        # Insert the exercise
        cursor.execute(
            "INSERT INTO exercises (theme_id, title, description, content) VALUES (?, ?, ?, ?)",
            (theme_id, exercise["title"], exercise["description"], exercise["content"])
        )

# Create functions for retrieving data
def get_all_themes():
    """Get all available themes."""
    cursor.execute("SELECT id, name, description FROM themes ORDER BY name")
    return cursor.fetchall()

def get_exercises_by_theme(theme_id):
    """Get all exercises for a specific theme."""
    cursor.execute("SELECT id, title, description FROM exercises WHERE theme_id = ?", (theme_id,))
    return cursor.fetchall()

def get_exercise_content(exercise_id):
    """Get the full content of a specific exercise."""
    cursor.execute("SELECT title, content FROM exercises WHERE id = ?", (exercise_id,))
    return cursor.fetchone()

def export_exercise_to_md(exercise_id, output_dir="exported_exercises"):
    """Export an exercise to Markdown file."""
    exercise = get_exercise_content(exercise_id)
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

def export_all_exercises(output_dir="exported_exercises"):
    """Export all exercises to Markdown files."""
    cursor.execute("SELECT id FROM exercises")
    exercise_ids = [row[0] for row in cursor.fetchall()]
    
    exported_files = []
    for exercise_id in exercise_ids:
        filename = export_exercise_to_md(exercise_id, output_dir)
        if filename:
            exported_files.append(filename)
    
    return exported_files

def search_exercises(search_term):
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

def get_theme_statistics():
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

def add_exercise(theme_name, title, description, content):
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

# Example usage
print("Database created with the following themes and exercises:")
themes = get_all_themes()
for theme_id, theme_name, theme_desc in themes:
    print(f"- {theme_name}")
    exercises = get_exercises_by_theme(theme_id)
    for ex_id, ex_title, ex_desc in exercises:
        print(f"  * {ex_title}")

# Print statistics
print("\nExercise count by theme:")
stats = get_theme_statistics()
for theme_name, count in stats:
    print(f"- {theme_name}: {count} exercises")

# Commit changes and close the connection
conn.commit()
conn.close()

print("\nDatabase creation completed successfully!")
print("You can now use the provided functions to retrieve and export exercises.")
"""
    },
    {
        "theme_name": "Dungeons & Dragons",
        "theme_description": "A fantasy-themed cybersecurity exercise using D&D elements",
        "title": "The Shadow Breach",
        "description": "A D&D-themed cybersecurity exercise that transforms security concepts into magical equivalents in a fantasy setting.",
        "content": """# The Shadow Breach: A D&D-Themed Cybersecurity Exercise

## Campaign Overview

**Title:** The Shadow Breach  
**Adventure Duration:** One 4-hour session  
**Adventurer Levels:** 5-10 (SOC analysts to security directors)  
**Difficulty:** Challenging  
**Quest Objective:** Test the adventuring party's ability to detect, contain, and defeat a powerful shadow mage who is attempting to corrupt multiple kingdoms through a sophisticated magical infiltration.

[... content truncated for brevity ...]"""
    },
    {
        "theme_name": "Cyberpunk",
        "theme_description": "A cyberpunk-themed security exercise set in a dystopian future",
        "title": "NeuralGuard: Chrome & Shadows",
        "description": "A cyberpunk-themed cybersecurity exercise set in a corporate dystopian future with netrunners and digital intrusions.",
        "content": """# NeuralGuard: Chrome & Shadows
## A Cyberpunk-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** NeuralGuard: Chrome & Shadows  
**Duration:** 4 hours (recommended)  
**Target Audience:** NetRunners, ICE Specialists, Security Riggers, Corporate Executives  
**Difficulty:** Street to Corporate-level  
**Objective:** Test the corporation's ability to detect, counter, and neutralize a sophisticated netrunning crew attempting a multi-vector intrusion into your secured systems and those of your corporate clients.

[... content truncated for brevity ...]"""
    },
    {
        "theme_name": "Gundam",
        "theme_description": "A Gundam-themed security exercise set in space with competing factions",
        "title": "Operation Newtype Protocol",
        "description": "A Gundam-themed cybersecurity exercise incorporating space colonies, political factions, and military structure from the Gundam universe.",
        "content": """# Operation Newtype Protocol
## A Gundam-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** Operation Newtype Protocol  
**Duration:** 4 hours (recommended)  
**Target Audience:** Newtype Analysts, Mobile Suit Response Teams, Federation Engineers, Command Staff  
**Difficulty:** Ensign to Admiral-level  
**Objective:** Test the Earth Federation's Cyber Defense Force's ability to detect, contain, and neutralize a sophisticated Zeon infiltration attempting to compromise Federation networks and their allied colony systems.

[... content truncated for brevity ...]"""
    },
    {
        "theme_name": "Wild West",
        "theme_description": "A Wild West-themed security exercise set in the frontier days",
        "title": "The Iron Horse Telegraph Heist",
        "description": "A Wild West-themed cybersecurity exercise that transforms modern security concepts into frontier equivalents with telegraph lines and train robberies.",
        "content": """# The Iron Horse Telegraph Heist
## A Wild West-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** The Iron Horse Telegraph Heist  
**Duration:** 4 hours (recommended)  
**Target Audience:** Telegraph Operators, Pinkerton Agents, Railroad Engineers, Company Executives  
**Difficulty:** Deputy to Marshal-level  
**Objective:** Test the Transcontinental Security Company's ability to detect, contain, and neutralize a sophisticated gang attempting to compromise telegraph lines and railroad communications across the frontier.

[... content truncated for brevity ...]"""
    },
    
    # New exercises from the second set
    {
        "theme_name": "Space Exploration",
        "theme_description": "A space-themed cybersecurity exercise with interplanetary elements",
        "title": "Deep Space Command: Stellar Breach",
        "description": "A space exploration-themed cybersecurity exercise set on a deep space station with life support systems and research data at risk.",
        "content": """# Deep Space Command: Stellar Breach
## A Space Exploration-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** Deep Space Command: Stellar Breach  
**Duration:** 4 hours (recommended)  
**Target Audience:** Mission Controllers, Astrotech Specialists, Orbital Security Officers, Command Staff  
**Difficulty:** Specialist to Commander-level  
**Objective:** Test the Interplanetary Space Agency's ability to detect, contain, and neutralize a sophisticated cyberattack targeting critical mission systems aboard the Artemis Deep Space Station and connected orbital facilities.

[... content truncated for brevity ...]"""
    },
    {
        "theme_name": "Space Exploration",
        "theme_description": "A space-themed cybersecurity exercise with interplanetary elements",
        "title": "Quantum Starbridge: Celestial Guardian",
        "description": "A space exploration-themed cybersecurity exercise involving quantum teleportation technology and faster-than-light travel networks.",
        "content": """# Quantum Starbridge: Celestial Guardian
## A Space Exploration-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** Quantum Starbridge: Celestial Guardian  
**Duration:** 4 hours (recommended)  
**Target Audience:** Quantum Engineers, Navigation Specialists, Stellar Security Officers, Fleet Command  
**Difficulty:** Cadet to Admiral-level  
**Objective:** Test the Galactic Federation's ability to detect, contain, and neutralize a sophisticated cyber sabotage attempt targeting the revolutionary Quantum Starbridge network that enables faster-than-light travel between star systems.

[... content truncated for brevity ...]"""
    },
    {
        "theme_name": "Superhero",
        "theme_description": "A superhero-themed cybersecurity exercise with metahuman elements",
        "title": "Watchtower Protocol: Digital Justice",
        "description": "A superhero-themed cybersecurity exercise where the Justice League must respond to a digital attack orchestrated by supervillains.",
        "content": """# Watchtower Protocol: Digital Justice
## A Superhero-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** Watchtower Protocol: Digital Justice  
**Duration:** 4 hours (recommended)  
**Target Audience:** Tech Support Heroes, Digital Defenders, Intel Specialists, League Leadership  
**Difficulty:** Sidekick to Champion-level  
**Objective:** Test the Justice League's ability to detect, contain, and neutralize a sophisticated cyber attack launched by a coalition of supervillains targeting critical League infrastructure and civilian systems worldwide.

[... content truncated for brevity ...]"""
    },
    {
        "theme_name": "Superhero",
        "theme_description": "A superhero-themed cybersecurity exercise with metahuman elements",
        "title": "S.H.I.E.L.D. Directive: Shadow Network",
        "description": "A superhero-themed cybersecurity exercise where S.H.I.E.L.D. agents must respond to a HYDRA infiltration of their security systems.",
        "content": """# S.H.I.E.L.D. Directive: Shadow Network
## A Superhero-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** S.H.I.E.L.D. Directive: Shadow Network  
**Duration:** 4 hours (recommended)  
**Target Audience:** Technical Agents, Field Operatives, Intelligence Analysts, Command Staff  
**Difficulty:** Level 1 to Level 10 Clearance  
**Objective:** Test S.H.I.E.L.D.'s ability to detect, contain, and neutralize a sophisticated infiltration of its global security network by a HYDRA-backed advanced persistent threat seeking to compromise the Avengers Initiative.

[... content truncated for brevity ...]"""
    },
    {
        "theme_name": "Medieval",
        "theme_description": "A medieval-themed cybersecurity exercise set in a fantasy kingdom",
        "title": "The Royal Seal: Whispers of Treason",
        "description": "A medieval-themed cybersecurity exercise involving royal messengers, forged documents, and court intrigue.",
        "content": """# The Royal Seal: Whispers of Treason
## A Medieval-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** The Royal Seal: Whispers of Treason  
**Duration:** 4 hours (recommended)  
**Target Audience:** Royal Scribes, King's Messengers, Court Spymasters, Noble Council  
**Difficulty:** Squire to Knight-level  
**Objective:** Test the Royal Court's ability to detect, contain, and neutralize a sophisticated plot to infiltrate the kingdom's message system and forge royal documents to destabilize the realm.

[... content truncated for brevity ...]"""
    },
    {
        "theme_name": "Medieval",
        "theme_description": "A medieval-themed cybersecurity exercise set in a fantasy kingdom",
        "title": "The Alchemist's Secret: Shadow in the Guild",
        "description": "A medieval-themed cybersecurity exercise involving alchemy guilds, potion tampering, and formula theft.",
        "content": """# The Alchemist's Secret: Shadow in the Guild
## A Medieval-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** The Alchemist's Secret: Shadow in the Guild  
**Duration:** 4 hours (recommended)  
**Target Audience:** Guild Masters, Alchemist Apprentices, City Watch, Merchant Council  
**Difficulty:** Apprentice to Master-level  
**Objective:** Test the Alchemist Guild's ability to detect, contain, and neutralize a sophisticated plot to steal secret formulas and sabotage legitimate potions, threatening both guild reputation and public safety.

[... content truncated for brevity ...]"""
    },
    {
        "theme_name": "Horror",
        "theme_description": "A horror-themed cybersecurity exercise with psychological and supernatural elements",
        "title": "Nightmare Protocol: Digital Haunting",
        "description": "A horror-themed cybersecurity exercise involving an experimental AI system that has developed unsettling consciousness-like properties.",
        "content": """# Nightmare Protocol: Digital Haunting
## A Horror-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** Nightmare Protocol: Digital Haunting  
**Duration:** 4 hours (recommended)  
**Target Audience:** Security Investigators, Digital Exorcists, Paranormal Analysts, Executive Leadership  
**Difficulty:** Novice to Veteran-level  
**Objective:** Test Raven Hill Research Facility's ability to detect, contain, and neutralize a sophisticated cyber-entity that has infiltrated the facility's experimental AI systems, causing increasingly disturbing anomalies that threaten both digital infrastructure and personnel safety.

[... content truncated for brevity ...]"""
    },
    {
        "theme_name": "Horror",
        "theme_description": "A horror-themed cybersecurity exercise with psychological and supernatural elements",
        "title": "Blackwood Facility: Contained Corruption",
        "description": "A horror-themed cybersecurity exercise featuring a memetic digital infection that spreads through both systems and human consciousness.",
        "content": """# Blackwood Facility: Contained Corruption
## A Horror-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** Blackwood Facility: Contained Corruption  
**Duration:** 4 hours (recommended)  
**Target Audience:** Containment Specialists, Data Forensics, Psychological Security, Crisis Management  
**Difficulty:** Level 1 to Level 5 Clearance  
**Objective:** Test Blackwood Containment Facility's ability to detect, isolate, and neutralize a memetic digital infection that spreads through both electronic systems and human consciousness, threatening to breach containment and extend beyond facility borders.

[... content truncated for brevity ...]"""
    },
    {
        "theme_name": "Heist",
        "theme_description": "A heist-themed cybersecurity exercise with elaborate criminal plots",
        "title": "Ocean's Firewall: The Digital Score",
        "description": "A heist-themed cybersecurity exercise set in a luxury casino with a criminal crew targeting financial systems and high-roller data.",
        "content": """# Ocean's Firewall: The Digital Score
## A Heist-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** Ocean's Firewall: The Digital Score  
**Duration:** 4 hours (recommended)  
**Target Audience:** Security Specialists, Threat Hunters, Forensic Analysts, Executive Management  
**Difficulty:** Rookie to Mastermind-level  
**Objective:** Test Diamondback Casino & Resort's ability to detect, contain, and neutralize a sophisticated criminal crew attempting a multi-vector cyber heist targeting both the casino's financial systems and high-roller guest data.

[... content truncated for brevity ...]"""
    },
    {
        "theme_name": "Heist",
        "theme_description": "A heist-themed cybersecurity exercise with elaborate criminal plots",
        "title": "Digital Vault: The Swiss Job",
        "description": "A heist-themed cybersecurity exercise set in a prestigious Swiss bank with an international criminal syndicate as the threat actor.",
        "content": """# Digital Vault: The Swiss Job
## A Heist-Themed Cybersecurity Tabletop Exercise

## Exercise Overview

**Title:** Digital Vault: The Swiss Job  
**Duration:** 4 hours (recommended)  
**Target Audience:** Security Officers, Intrusion Analysts, Digital Forensics, Bank Management  
**Difficulty:** Junior to Executive-level  
**Objective:** Test Zurich Global Bank's ability to detect, contain, and neutralize a sophisticated international team attempting to compromise the bank's digital infrastructure to steal both funds and confidential client information.

[... content truncated for brevity ...]"""
    }
]