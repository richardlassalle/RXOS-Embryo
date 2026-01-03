#!/usr/bin/env python3
"""
Learning Embryonic Story Generation System
Parametric cascade with evolutionary learning
"""

import json
import yaml
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

@dataclass
class PerformanceMetrics:
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


class LearningParameters:
    """Parameters that learn and evolve"""
    
    def __init__(self, initial_params: Dict[str, float]):
        self.params = initial_params.copy()
        self.effectiveness_history = {k: [] for k in self.params.keys()}
        self.adaptation_rate = 0.1
        self.successful_ranges = {k: [v-0.2, v+0.2] for k, v in self.params.items()}
        
    def record_effectiveness(self, param_name: str, value: float, performance: float):
        """Record how well a parameter value performed"""
        self.effectiveness_history[param_name].append({
            'value': value,
            'performance': performance,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update successful range based on good performance
        if performance > 0.7:
            current_range = self.successful_ranges[param_name]
            if value < current_range[0]:
                current_range[0] = value * 0.9 + current_range[0] * 0.1
            elif value > current_range[1]:
                current_range[1] = value * 0.9 + current_range[1] * 0.1
    
    def evolve_parameter(self, param_name: str) -> float:
        """Evolve parameter based on learning history"""
        if not self.effectiveness_history[param_name]:
            return self.params[param_name]
        
        history = self.effectiveness_history[param_name]
        best_performers = [h for h in history if h['performance'] > 0.7]
        
        if best_performers:
            avg_best = np.mean([h['value'] for h in best_performers])
            current_val = self.params[param_name]
            new_val = current_val * (1 - self.adaptation_rate) + avg_best * self.adaptation_rate
            
            min_val, max_val = self.successful_ranges[param_name]
            new_val = np.clip(new_val, min_val, max_val)
            
            self.params[param_name] = new_val
            return new_val
        
        return self.params[param_name]
    
    def get_optimized_params(self) -> Dict[str, float]:
        """Get current optimized parameters"""
        return {k: self.evolve_parameter(k) for k in self.params.keys()}


class LearningCell:
    """Cell that tracks its own performance for learning feedback"""
    
    def __init__(self, embryo_id: str, position: int, arc_position: str,
                 duration: float, intensity: float, temperature: float,
                 parent_dna: Dict[str, Any]):
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
        self.asset_selections = self._select_assets()
        
    def _select_assets(self) -> Dict[str, List[str]]:
        """Select assets based on current parameters"""
        return {
            'characters': [f"chr_{self.arc_position}_001"],
            'locations': [f"loc_{self.arc_position}_001"],
            'objects': [f"obj_{self.arc_position}_001"]
        }
    
    def execute_generation(self) -> Dict[str, Any]:
        """Execute content generation and track performance"""
        start_time = datetime.now()
        
        content = {
            'cell_id': self.id,
            'arc': self.arc_position,
            'duration': self.duration,
            'intensity': self.intensity,
            'temperature': self.temperature,
            'assets': self.asset_selections,
            'generated_content': f"Generated {self.arc_position} content with intensity {self.intensity}"
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
    
    def to_yaml(self) -> Dict[str, Any]:
        """Convert to YAML structure"""
        return {
            'cell': {
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
                'execution_metrics': self.execution_metrics
            }
        }


class LearningEmbryo:
    """Embryo that learns and evolves with each generation"""
    
    def __init__(self, initial_dna: Dict[str, Any], embryo_id: str = None):
        self.id = embryo_id or f"emb_{uuid.uuid4().hex[:8]}"
        self.generation = 1
        self.birth_time = datetime.now()
        self.dna = initial_dna.copy()
        
        self.learning_params = LearningParameters({
            'setup_intensity': 0.3,
            'conflict_intensity': 0.8,
            'resolution_intensity': 0.6,
            'setup_temperature': 0.7,
            'conflict_temperature': 0.5,
            'resolution_temperature': 0.4,
            'setup_duration_ratio': 0.33,
            'conflict_duration_ratio': 0.34,
            'resolution_duration_ratio': 0.33
        })
        
        self.generation_history = []
        self.offspring_count = 0
        
    def stimulate_division(self, target_duration: float, subject_hint: str = "") -> List[LearningCell]:
        """Create cells with current optimized parameters"""
        
        optimized_params = self.learning_params.get_optimized_params()
        
        if target_duration <= 30:
            cell_count = 3
        elif target_duration <= 300:
            cell_count = 9
        else:
            cell_count = int(target_duration / 20)
        
        cell_count = max(3, cell_count)
        
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
        cells_per_arc = cell_count // 3
        
        for i in range(cell_count):
            arc_index = min(i // cells_per_arc, 2)
            arc_position = arc_positions[arc_index]
            
            intensity = optimized_params[f'{arc_position}_intensity']
            temperature = optimized_params[f'{arc_position}_temperature']
            cell_duration = arc_durations[arc_position] / cells_per_arc
            
            cell = LearningCell(
                embryo_id=self.id,
                position=i,
                arc_position=arc_position,
                duration=cell_duration,
                intensity=intensity,
                temperature=temperature,
                parent_dna=self.dna
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
            'performance': asdict(metrics),
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
        offspring.generation = self.generation
        offspring.learning_params = self.learning_params
        
        return offspring
    
    def save_lineage(self, filepath: str):
        """Save entire evolutionary lineage"""
        lineage_data = {
            'embryo_id': self.id,
            'generation': self.generation,
            'birth_time': self.birth_time.isoformat(),
            'offspring_count': self.offspring_count,
            'dna': self.dna,
            'learning_history': self.generation_history,
            'parameter_evolution': {
                k: self.learning_params.effectiveness_history[k]
                for k in self.learning_params.params.keys()
            },
            'current_successful_ranges': self.learning_params.successful_ranges
        }
        
        with open(filepath, 'w') as f:
            yaml.dump(lineage_data, f, default_flow_style=False)


class StoryEvolutionEngine:
    """Main engine that manages embryo evolution"""
    
    def __init__(self):
        self.current_embryo = None
        self.evolution_history = []
        
    def initialize_embryo(self, initial_dna: Dict[str, Any]) -> LearningEmbryo:
        """Create initial embryo"""
        self.current_embryo = LearningEmbryo(initial_dna)
        return self.current_embryo
    
    def generate_story(self, target_duration: float, subject_hint: str = "") -> Tuple[List[LearningCell], Dict[str, Any]]:
        """Generate story and return cells + YAML structure"""
        
        if not self.current_embryo:
            raise ValueError("No embryo initialized")
        
        cells = self.current_embryo.stimulate_division(target_duration, subject_hint)
        
        story_content = []
        for cell in cells:
            content = cell.execute_generation()
            story_content.append(content)
        
        yaml_structure = {
            'embryo_id': self.current_embryo.id,
            'generation': self.current_embryo.generation,
            'target_duration': target_duration,
            'cell_count': len(cells),
            'cells': [cell.to_yaml() for cell in cells],
            'total_execution_time': sum(cell.execution_metrics.get('execution_time', 0) for cell in cells)
        }
        
        return cells, yaml_structure
    
    def provide_feedback(self, cells: List[LearningCell], metrics: PerformanceMetrics):
        """Provide feedback and evolve embryo"""
        
        evolved_embryo = self.current_embryo.learn_from_feedback(cells, metrics)
        
        evolution_record = {
            'parent_id': self.current_embryo.id,
            'child_id': evolved_embryo.id,
            'evolution_trigger': asdict(metrics),
            'timestamp': datetime.now().isoformat()
        }
        
        self.evolution_history.append(evolution_record)
        self.current_embryo = evolved_embryo
        
        return evolved_embryo


# Example usage
if __name__ == "__main__":
    
    # Initialize evolution engine
    engine = StoryEvolutionEngine()
    
    # Create initial DNA
    initial_dna = {
        'arc_structure': ['setup', 'conflict', 'resolution'],
        'asset_libraries': {
            'characters': ['chr_001', 'chr_002', 'chr_003'],
            'locations': ['loc_001', 'loc_002'],
            'objects': ['obj_001', 'obj_002', 'obj_003']
        }
    }
    
    # Initialize first embryo
    embryo = engine.initialize_embryo(initial_dna)
    print(f"Created embryo: {embryo.id}, Generation: {embryo.generation}")
    
    # Generate a 30-second story
    cells, yaml_structure = engine.generate_story(30.0, "car commercial")
    print(f"\nGenerated {len(cells)} cells for 30-second piece")
    
    # Simulate user feedback
    feedback = PerformanceMetrics(
        engagement_score=0.85,
        narrative_coherence=0.9,
        visual_quality=0.8,
        timing_effectiveness=0.7
    )
    
    # Evolve based on feedback
    evolved_embryo = engine.provide_feedback(cells, feedback)
    print(f"\nEvolved to: {evolved_embryo.id}, Generation: {evolved_embryo.generation}")
    
    # Generate another story with evolved parameters
    cells2, yaml_structure2 = engine.generate_story(60.0, "dog food commercial")
    print(f"Generated {len(cells2)} cells for 60-second piece")
    
    # More feedback
    feedback2 = PerformanceMetrics(
        engagement_score=0.9,
        narrative_coherence=0.85,
        visual_quality=0.88,
        timing_effectiveness=0.82
    )
    
    # Evolve again
    evolved_embryo2 = engine.provide_feedback(cells2, feedback2)
    print(f"\nEvolved to: {evolved_embryo2.id}, Generation: {evolved_embryo2.generation}")
    
    # Show learned parameters
    print("\n--- Learned Parameter Ranges ---")
    for param, range_vals in evolved_embryo2.learning_params.successful_ranges.items():
        print(f"{param}: {range_vals[0]:.3f} - {range_vals[1]:.3f}")
    
    # Output final YAML structure
    print("\n--- Final Story Structure (YAML) ---")
    print(yaml.dump(yaml_structure2, default_flow_style=False))
