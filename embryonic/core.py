"""
Learning Embryonic Story Generation System
Parametric cascade with evolutionary learning
"""

import json
import yaml
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
import uuid


@dataclass
class PerformanceMetrics:
    """Feedback structure for learning"""
    engagement_score: float
    narrative_coherence: float
    visual_quality: float
    timing_effectiveness: float

    def overall_score(self) -> float:
        """Weighted overall performance score"""
        return (
            self.engagement_score * 0.3 +
            self.narrative_coherence * 0.3 +
            self.visual_quality * 0.2 +
            self.timing_effectiveness * 0.2
        )

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


class LearningParameters:
    """Parameters that learn and evolve"""

    def __init__(self, initial_params: Dict[str, float] = None):
        default_params = {
            'setup_intensity': 0.3,
            'conflict_intensity': 0.8,
            'resolution_intensity': 0.6,
            'setup_temperature': 0.7,
            'conflict_temperature': 0.5,
            'resolution_temperature': 0.4,
            'setup_duration_ratio': 0.33,
            'conflict_duration_ratio': 0.34,
            'resolution_duration_ratio': 0.33
        }
        self.params = initial_params.copy() if initial_params else default_params
        self.effectiveness_history = {k: [] for k in self.params.keys()}
        self.adaptation_rate = 0.1
        self.successful_ranges = {k: [max(0, v - 0.2), min(1, v + 0.2)] for k, v in self.params.items()}

    def record_effectiveness(self, param_name: str, value: float, performance: float):
        """Record how well a parameter value performed"""
        if param_name not in self.effectiveness_history:
            self.effectiveness_history[param_name] = []

        self.effectiveness_history[param_name].append({
            'value': value,
            'performance': performance,
            'timestamp': datetime.now().isoformat()
        })

        # Update successful range based on good performance
        if performance > 0.7 and param_name in self.successful_ranges:
            current_range = self.successful_ranges[param_name]
            if value < current_range[0]:
                current_range[0] = value * 0.9 + current_range[0] * 0.1
            elif value > current_range[1]:
                current_range[1] = value * 0.9 + current_range[1] * 0.1

    def evolve_parameter(self, param_name: str) -> float:
        """Evolve parameter based on learning history"""
        if param_name not in self.effectiveness_history or not self.effectiveness_history[param_name]:
            return self.params.get(param_name, 0.5)

        history = self.effectiveness_history[param_name]
        best_performers = [h for h in history if h['performance'] > 0.7]

        if best_performers:
            avg_best = sum(h['value'] for h in best_performers) / len(best_performers)
            current_val = self.params[param_name]
            new_val = current_val * (1 - self.adaptation_rate) + avg_best * self.adaptation_rate

            if param_name in self.successful_ranges:
                min_val, max_val = self.successful_ranges[param_name]
                new_val = max(min_val, min(max_val, new_val))

            self.params[param_name] = new_val
            return new_val

        return self.params.get(param_name, 0.5)

    def get_optimized_params(self) -> Dict[str, float]:
        """Get current optimized parameters"""
        return {k: self.evolve_parameter(k) for k in self.params.keys()}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'params': self.params,
            'effectiveness_history': self.effectiveness_history,
            'adaptation_rate': self.adaptation_rate,
            'successful_ranges': self.successful_ranges
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningParameters':
        lp = cls(data.get('params', {}))
        lp.effectiveness_history = data.get('effectiveness_history', {})
        lp.adaptation_rate = data.get('adaptation_rate', 0.1)
        lp.successful_ranges = data.get('successful_ranges', {})
        return lp


class LearningCell:
    """Cell that tracks its own performance for learning feedback"""

    def __init__(self, embryo_id: str, position: int, arc_position: str,
                 duration: float, intensity: float, temperature: float,
                 parent_dna: Dict[str, Any], assets: Dict[str, List[str]] = None):
        self.id = f"cell_{uuid.uuid4().hex[:8]}"
        self.embryo_id = embryo_id
        self.position = position
        self.arc_position = arc_position
        self.duration = duration
        self.intensity = intensity
        self.temperature = temperature
        self.parent_dna = parent_dna
        self.generation_time = datetime.now()
        self.execution_metrics = {}
        self.asset_selections = assets or self._default_assets()

    def _default_assets(self) -> Dict[str, List[str]]:
        """Default asset selection based on arc position"""
        return {
            'characters': [f"chr_{self.arc_position}_001"],
            'locations': [f"loc_{self.arc_position}_001"],
            'objects': [f"obj_{self.arc_position}_001"]
        }

    def execute_generation(self) -> Dict[str, Any]:
        """Execute content generation and track performance"""
        start_time = datetime.now()

        action_map = {
            'setup': 'establishing_shot',
            'conflict': 'confrontation',
            'resolution': 'denouement'
        }

        content = {
            'cell_id': self.id,
            'arc': self.arc_position,
            'duration': self.duration,
            'intensity': self.intensity,
            'temperature': self.temperature,
            'assets': self.asset_selections,
            'action': action_map.get(self.arc_position, 'scene'),
            'generated_content': f"Generated {self.arc_position} content with intensity {self.intensity:.2f}"
        }

        end_time = datetime.now()

        self.execution_metrics = {
            'execution_time': (end_time - start_time).total_seconds(),
            'parameter_snapshot': {
                'intensity': self.intensity,
                'temperature': self.temperature,
                'duration': self.duration
            },
            'timestamp': start_time.isoformat()
        }

        return content

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary structure"""
        return {
            'id': self.id,
            'embryo_id': self.embryo_id,
            'position': self.position,
            'arc': self.arc_position,
            'duration': self.duration,
            'parameters': {
                'intensity': self.intensity,
                'temperature': self.temperature
            },
            'assets': self.asset_selections,
            'execution_metrics': self.execution_metrics,
            'generation_time': self.generation_time.isoformat()
        }

    def to_yaml(self) -> Dict[str, Any]:
        """Convert to YAML structure"""
        return {'cell': self.to_dict()}


class LearningEmbryo:
    """Embryo that learns and evolves with each generation"""

    def __init__(self, initial_dna: Dict[str, Any] = None, embryo_id: str = None,
                 name: str = None):
        self.id = embryo_id or f"emb_{uuid.uuid4().hex[:8]}"
        self.name = name or self.id
        self.generation = 1
        self.birth_time = datetime.now()
        self.dna = initial_dna.copy() if initial_dna else self._default_dna()
        self.learning_params = LearningParameters()
        self.generation_history = []
        self.offspring_count = 0
        self.asset_library = None  # Can be set externally

    def _default_dna(self) -> Dict[str, Any]:
        return {
            'arc_structure': ['setup', 'conflict', 'resolution'],
            'transformation_rules': {
                'setup': {'intensity': 0.3, 'temperature': 0.7},
                'conflict': {'intensity': 0.8, 'temperature': 0.5},
                'resolution': {'intensity': 0.6, 'temperature': 0.4}
            },
            'asset_libraries': {
                'characters': [],
                'locations': [],
                'objects': []
            }
        }

    def set_asset_library(self, asset_library):
        """Set external asset library for selection"""
        self.asset_library = asset_library

    def _select_assets_for_cell(self, arc_position: str, params: Dict[str, float]) -> Dict[str, List[str]]:
        """Select assets for a cell based on parameters"""
        if self.asset_library:
            return self.asset_library.select_for_cell(arc_position, params)

        # Fallback to DNA assets or defaults
        dna_assets = self.dna.get('asset_libraries', {})
        return {
            'characters': dna_assets.get('characters', [])[:2] or [f"chr_{arc_position}_001"],
            'locations': dna_assets.get('locations', [])[:1] or [f"loc_{arc_position}_001"],
            'objects': dna_assets.get('objects', [])[:2] or [f"obj_{arc_position}_001"]
        }

    def stimulate_division(self, target_duration: float, subject_hint: str = "") -> List[LearningCell]:
        """Create cells with current optimized parameters"""
        optimized_params = self.learning_params.get_optimized_params()

        # Determine cell count based on duration
        if target_duration <= 30:
            cell_count = 3
        elif target_duration <= 120:
            cell_count = 6
        elif target_duration <= 300:
            cell_count = 9
        else:
            cell_count = max(9, int(target_duration / 30))

        # Calculate arc durations
        setup_duration = target_duration * optimized_params['setup_duration_ratio']
        conflict_duration = target_duration * optimized_params['conflict_duration_ratio']
        resolution_duration = target_duration * optimized_params['resolution_duration_ratio']

        cells = []
        arc_durations = {
            'setup': setup_duration,
            'conflict': conflict_duration,
            'resolution': resolution_duration
        }

        arc_positions = ['setup', 'conflict', 'resolution']
        cells_per_arc = max(1, cell_count // 3)

        for i in range(cell_count):
            arc_index = min(i // cells_per_arc, 2)
            arc_position = arc_positions[arc_index]

            intensity = optimized_params[f'{arc_position}_intensity']
            temperature = optimized_params[f'{arc_position}_temperature']
            cell_duration = arc_durations[arc_position] / cells_per_arc

            # Select assets for this cell
            cell_assets = self._select_assets_for_cell(arc_position, {
                'intensity': intensity,
                'temperature': temperature
            })

            cell = LearningCell(
                embryo_id=self.id,
                position=i,
                arc_position=arc_position,
                duration=cell_duration,
                intensity=intensity,
                temperature=temperature,
                parent_dna=self.dna,
                assets=cell_assets
            )

            cells.append(cell)

        self.offspring_count += len(cells)
        return cells

    def learn_from_feedback(self, cells: List[LearningCell], metrics: PerformanceMetrics):
        """Learn from generation performance and evolve"""
        overall_performance = metrics.overall_score()

        for cell in cells:
            arc = cell.arc_position
            self.learning_params.record_effectiveness(
                f'{arc}_intensity', cell.intensity, overall_performance
            )
            self.learning_params.record_effectiveness(
                f'{arc}_temperature', cell.temperature, overall_performance
            )

        generation_data = {
            'generation': self.generation,
            'timestamp': datetime.now().isoformat(),
            'performance': metrics.to_dict(),
            'overall_score': overall_performance,
            'cell_count': len(cells),
            'parameters_used': self.learning_params.get_optimized_params()
        }

        self.generation_history.append(generation_data)
        self.generation += 1

        return self.create_evolved_offspring()

    def create_evolved_offspring(self) -> 'LearningEmbryo':
        """Create next generation embryo with evolved DNA"""
        evolved_dna = self.dna.copy()
        optimized_params = self.learning_params.get_optimized_params()

        evolved_dna['transformation_rules'] = {
            'setup': {
                'intensity': optimized_params['setup_intensity'],
                'temperature': optimized_params['setup_temperature']
            },
            'conflict': {
                'intensity': optimized_params['conflict_intensity'],
                'temperature': optimized_params['conflict_temperature']
            },
            'resolution': {
                'intensity': optimized_params['resolution_intensity'],
                'temperature': optimized_params['resolution_temperature']
            }
        }

        offspring = LearningEmbryo(evolved_dna, f"emb_{self.generation}_{uuid.uuid4().hex[:6]}")
        offspring.name = self.name
        offspring.generation = self.generation
        offspring.learning_params = self.learning_params
        offspring.generation_history = self.generation_history.copy()
        offspring.asset_library = self.asset_library

        return offspring

    def to_dict(self) -> Dict[str, Any]:
        """Convert embryo to dictionary for storage"""
        return {
            'id': self.id,
            'name': self.name,
            'generation': self.generation,
            'birth_time': self.birth_time.isoformat(),
            'offspring_count': self.offspring_count,
            'dna': self.dna,
            'learning_params': self.learning_params.to_dict(),
            'generation_history': self.generation_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningEmbryo':
        """Restore embryo from dictionary"""
        embryo = cls(
            initial_dna=data.get('dna'),
            embryo_id=data.get('id'),
            name=data.get('name')
        )
        embryo.generation = data.get('generation', 1)
        embryo.birth_time = datetime.fromisoformat(data['birth_time']) if data.get('birth_time') else datetime.now()
        embryo.offspring_count = data.get('offspring_count', 0)
        embryo.generation_history = data.get('generation_history', [])
        if data.get('learning_params'):
            embryo.learning_params = LearningParameters.from_dict(data['learning_params'])
        return embryo

    def save_lineage(self, filepath: str):
        """Save entire evolutionary lineage to YAML"""
        lineage_data = {
            'embryo_id': self.id,
            'name': self.name,
            'generation': self.generation,
            'birth_time': self.birth_time.isoformat(),
            'offspring_count': self.offspring_count,
            'dna': self.dna,
            'learning_history': self.generation_history,
            'parameter_evolution': {
                k: self.learning_params.effectiveness_history.get(k, [])
                for k in self.learning_params.params.keys()
            },
            'current_successful_ranges': self.learning_params.successful_ranges,
            'current_optimized_params': self.learning_params.get_optimized_params()
        }

        with open(filepath, 'w') as f:
            yaml.dump(lineage_data, f, default_flow_style=False, sort_keys=False)


class StoryEvolutionEngine:
    """Main engine that manages embryo evolution"""

    def __init__(self, storage=None, asset_library=None):
        self.current_embryo = None
        self.evolution_history = []
        self.storage = storage
        self.asset_library = asset_library
        self.last_generated_cells = None
        self.last_story_structure = None

    def initialize_embryo(self, initial_dna: Dict[str, Any] = None,
                         name: str = None) -> LearningEmbryo:
        """Create initial embryo"""
        self.current_embryo = LearningEmbryo(initial_dna, name=name)
        if self.asset_library:
            self.current_embryo.set_asset_library(self.asset_library)
        return self.current_embryo

    def load_embryo(self, embryo_id: str = None, name: str = None) -> Optional[LearningEmbryo]:
        """Load embryo from storage"""
        if not self.storage:
            return None

        embryo = self.storage.load_embryo(embryo_id=embryo_id, name=name)
        if embryo:
            self.current_embryo = embryo
            if self.asset_library:
                self.current_embryo.set_asset_library(self.asset_library)
        return embryo

    def save_embryo(self):
        """Save current embryo to storage"""
        if self.storage and self.current_embryo:
            self.storage.save_embryo(self.current_embryo)

    def generate_story(self, target_duration: float, subject_hint: str = "") -> Tuple[List[LearningCell], Dict[str, Any]]:
        """Generate story and return cells + YAML structure"""
        if not self.current_embryo:
            raise ValueError("No embryo initialized. Use 'embryo init' first.")

        cells = self.current_embryo.stimulate_division(target_duration, subject_hint)

        story_content = []
        for cell in cells:
            content = cell.execute_generation()
            story_content.append(content)

        yaml_structure = {
            'story': {
                'embryo_id': self.current_embryo.id,
                'embryo_name': self.current_embryo.name,
                'generation': self.current_embryo.generation,
                'subject': subject_hint,
                'target_duration': target_duration,
                'cell_count': len(cells),
                'arc_breakdown': self._get_arc_breakdown(cells),
                'cells': [cell.to_dict() for cell in cells],
                'total_execution_time': sum(
                    cell.execution_metrics.get('execution_time', 0) for cell in cells
                ),
                'generated_at': datetime.now().isoformat()
            }
        }

        self.last_generated_cells = cells
        self.last_story_structure = yaml_structure

        # Save story to storage
        if self.storage:
            self.storage.save_story(yaml_structure['story'])

        return cells, yaml_structure

    def _get_arc_breakdown(self, cells: List[LearningCell]) -> Dict[str, Any]:
        """Get breakdown of cells by arc"""
        breakdown = {'setup': [], 'conflict': [], 'resolution': []}
        for cell in cells:
            breakdown[cell.arc_position].append({
                'cell_id': cell.id,
                'duration': cell.duration,
                'intensity': cell.intensity
            })
        return {
            arc: {
                'cell_count': len(cells_list),
                'total_duration': sum(c['duration'] for c in cells_list),
                'avg_intensity': sum(c['intensity'] for c in cells_list) / len(cells_list) if cells_list else 0
            }
            for arc, cells_list in breakdown.items()
        }

    def provide_feedback(self, metrics: PerformanceMetrics,
                        cells: List[LearningCell] = None) -> LearningEmbryo:
        """Provide feedback and evolve embryo"""
        if cells is None:
            cells = self.last_generated_cells

        if cells is None:
            raise ValueError("No cells to provide feedback for. Generate a story first.")

        evolved_embryo = self.current_embryo.learn_from_feedback(cells, metrics)

        evolution_record = {
            'parent_id': self.current_embryo.id,
            'child_id': evolved_embryo.id,
            'evolution_trigger': metrics.to_dict(),
            'overall_score': metrics.overall_score(),
            'timestamp': datetime.now().isoformat()
        }

        self.evolution_history.append(evolution_record)
        self.current_embryo = evolved_embryo

        # Save evolved embryo to storage
        if self.storage:
            self.storage.save_embryo(evolved_embryo)
            self.storage.save_feedback(evolution_record)

        return evolved_embryo

    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        if not self.current_embryo:
            return {'status': 'No embryo initialized'}

        params = self.current_embryo.learning_params.get_optimized_params()

        return {
            'embryo': {
                'id': self.current_embryo.id,
                'name': self.current_embryo.name,
                'generation': self.current_embryo.generation,
                'offspring_count': self.current_embryo.offspring_count,
                'birth_time': self.current_embryo.birth_time.isoformat()
            },
            'learned_parameters': {
                'setup': {
                    'intensity': round(params['setup_intensity'], 3),
                    'temperature': round(params['setup_temperature'], 3),
                    'duration_ratio': round(params['setup_duration_ratio'], 3)
                },
                'conflict': {
                    'intensity': round(params['conflict_intensity'], 3),
                    'temperature': round(params['conflict_temperature'], 3),
                    'duration_ratio': round(params['conflict_duration_ratio'], 3)
                },
                'resolution': {
                    'intensity': round(params['resolution_intensity'], 3),
                    'temperature': round(params['resolution_temperature'], 3),
                    'duration_ratio': round(params['resolution_duration_ratio'], 3)
                }
            },
            'successful_ranges': self.current_embryo.learning_params.successful_ranges,
            'generation_history_count': len(self.current_embryo.generation_history),
            'last_performance': (
                self.current_embryo.generation_history[-1]['performance']
                if self.current_embryo.generation_history else None
            )
        }
