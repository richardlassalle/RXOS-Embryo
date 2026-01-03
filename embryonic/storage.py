"""
Persistent Storage Layer for Embryonic Story System
SQLite-based storage for embryos, stories, and learning history
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class EmbryoStorage:
    """SQLite-based persistent storage for embryos and stories"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "embryonic.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS embryos (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE,
                    generation INTEGER,
                    birth_time TEXT,
                    offspring_count INTEGER,
                    dna TEXT,
                    learning_params TEXT,
                    generation_history TEXT,
                    updated_at TEXT,
                    is_current INTEGER DEFAULT 0
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    embryo_id TEXT,
                    embryo_name TEXT,
                    generation INTEGER,
                    subject TEXT,
                    target_duration REAL,
                    cell_count INTEGER,
                    structure TEXT,
                    generated_at TEXT,
                    FOREIGN KEY (embryo_id) REFERENCES embryos(id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_id TEXT,
                    child_id TEXT,
                    engagement_score REAL,
                    narrative_coherence REAL,
                    visual_quality REAL,
                    timing_effectiveness REAL,
                    overall_score REAL,
                    timestamp TEXT
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_embryo_name ON embryos(name)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_story_embryo ON stories(embryo_id)
            """)

            conn.commit()

    def save_embryo(self, embryo, set_current: bool = True):
        """Save embryo to database"""
        from .core import LearningEmbryo

        data = embryo.to_dict()

        with sqlite3.connect(self.db_path) as conn:
            # If setting as current, unset all others
            if set_current:
                conn.execute("UPDATE embryos SET is_current = 0")

            conn.execute("""
                INSERT OR REPLACE INTO embryos
                (id, name, generation, birth_time, offspring_count, dna,
                 learning_params, generation_history, updated_at, is_current)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['id'],
                data['name'],
                data['generation'],
                data['birth_time'],
                data['offspring_count'],
                json.dumps(data['dna']),
                json.dumps(data['learning_params']),
                json.dumps(data['generation_history']),
                datetime.now().isoformat(),
                1 if set_current else 0
            ))
            conn.commit()

    def load_embryo(self, embryo_id: str = None, name: str = None,
                   load_current: bool = False):
        """Load embryo from database"""
        from .core import LearningEmbryo

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if embryo_id:
                row = conn.execute(
                    "SELECT * FROM embryos WHERE id = ?", (embryo_id,)
                ).fetchone()
            elif name:
                row = conn.execute(
                    "SELECT * FROM embryos WHERE name = ?", (name,)
                ).fetchone()
            elif load_current:
                row = conn.execute(
                    "SELECT * FROM embryos WHERE is_current = 1"
                ).fetchone()
            else:
                return None

            if not row:
                return None

            data = {
                'id': row['id'],
                'name': row['name'],
                'generation': row['generation'],
                'birth_time': row['birth_time'],
                'offspring_count': row['offspring_count'],
                'dna': json.loads(row['dna']),
                'learning_params': json.loads(row['learning_params']),
                'generation_history': json.loads(row['generation_history'])
            }

            return LearningEmbryo.from_dict(data)

    def load_current_embryo(self):
        """Load the current active embryo"""
        return self.load_embryo(load_current=True)

    def list_embryos(self) -> List[Dict[str, Any]]:
        """List all embryos"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT id, name, generation, birth_time, offspring_count,
                       is_current, updated_at
                FROM embryos
                ORDER BY updated_at DESC
            """).fetchall()

            return [dict(row) for row in rows]

    def delete_embryo(self, embryo_id: str = None, name: str = None) -> bool:
        """Delete an embryo"""
        with sqlite3.connect(self.db_path) as conn:
            if embryo_id:
                conn.execute("DELETE FROM embryos WHERE id = ?", (embryo_id,))
            elif name:
                conn.execute("DELETE FROM embryos WHERE name = ?", (name,))
            else:
                return False
            conn.commit()
            return conn.total_changes > 0

    def save_story(self, story_data: Dict[str, Any]):
        """Save generated story"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO stories
                (embryo_id, embryo_name, generation, subject, target_duration,
                 cell_count, structure, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                story_data.get('embryo_id'),
                story_data.get('embryo_name'),
                story_data.get('generation'),
                story_data.get('subject', ''),
                story_data.get('target_duration'),
                story_data.get('cell_count'),
                json.dumps(story_data),
                story_data.get('generated_at', datetime.now().isoformat())
            ))
            conn.commit()

    def list_stories(self, embryo_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """List generated stories"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if embryo_id:
                rows = conn.execute("""
                    SELECT id, embryo_id, embryo_name, generation, subject,
                           target_duration, cell_count, generated_at
                    FROM stories
                    WHERE embryo_id = ?
                    ORDER BY generated_at DESC
                    LIMIT ?
                """, (embryo_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT id, embryo_id, embryo_name, generation, subject,
                           target_duration, cell_count, generated_at
                    FROM stories
                    ORDER BY generated_at DESC
                    LIMIT ?
                """, (limit,)).fetchall()

            return [dict(row) for row in rows]

    def get_story(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Get full story structure by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT structure FROM stories WHERE id = ?", (story_id,)
            ).fetchone()

            if row:
                return json.loads(row['structure'])
            return None

    def save_feedback(self, feedback_data: Dict[str, Any]):
        """Save feedback/evolution record"""
        metrics = feedback_data.get('evolution_trigger', {})

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO feedback
                (parent_id, child_id, engagement_score, narrative_coherence,
                 visual_quality, timing_effectiveness, overall_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback_data.get('parent_id'),
                feedback_data.get('child_id'),
                metrics.get('engagement_score'),
                metrics.get('narrative_coherence'),
                metrics.get('visual_quality'),
                metrics.get('timing_effectiveness'),
                feedback_data.get('overall_score'),
                feedback_data.get('timestamp', datetime.now().isoformat())
            ))
            conn.commit()

    def get_feedback_history(self, embryo_name: str = None,
                            limit: int = 50) -> List[Dict[str, Any]]:
        """Get feedback history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            query = """
                SELECT f.*, e.name as embryo_name
                FROM feedback f
                LEFT JOIN embryos e ON f.child_id = e.id
                ORDER BY f.timestamp DESC
                LIMIT ?
            """
            rows = conn.execute(query, (limit,)).fetchall()
            return [dict(row) for row in rows]

    def get_evolution_timeline(self, name: str) -> List[Dict[str, Any]]:
        """Get evolution timeline for an embryo lineage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Get the embryo's generation history
            embryo = self.load_embryo(name=name)
            if not embryo:
                return []

            timeline = []
            for gen_data in embryo.generation_history:
                timeline.append({
                    'generation': gen_data.get('generation'),
                    'timestamp': gen_data.get('timestamp'),
                    'performance': gen_data.get('performance'),
                    'overall_score': gen_data.get('overall_score'),
                    'cell_count': gen_data.get('cell_count'),
                    'parameters': gen_data.get('parameters_used')
                })

            return timeline

    def export_lineage(self, name: str, filepath: str):
        """Export full lineage data to file"""
        embryo = self.load_embryo(name=name)
        if embryo:
            embryo.save_lineage(filepath)
            return True
        return False

    def get_last_story(self, embryo_name: str = None) -> Optional[Dict[str, Any]]:
        """Get the most recent story, optionally for a specific embryo"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if embryo_name:
                row = conn.execute("""
                    SELECT structure FROM stories
                    WHERE embryo_name = ?
                    ORDER BY generated_at DESC
                    LIMIT 1
                """, (embryo_name,)).fetchone()
            else:
                row = conn.execute("""
                    SELECT structure FROM stories
                    ORDER BY generated_at DESC
                    LIMIT 1
                """).fetchone()

            if row:
                return json.loads(row['structure'])
            return None
