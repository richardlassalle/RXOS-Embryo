#!/usr/bin/env python3
"""
Embryonic Story System - Web Interface
Simple Flask dashboard for story generation and evolution tracking
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify, redirect, url_for
from embryonic import (
    StoryEvolutionEngine,
    EmbryoStorage,
    AssetLibrary,
    PerformanceMetrics,
    LearningCell,
)
from embryonic.assets import create_sample_library

app = Flask(__name__)

# Initialize components
storage = EmbryoStorage()
asset_library = create_sample_library()
engine = StoryEvolutionEngine(storage=storage, asset_library=asset_library)

# Load current embryo if exists
current_embryo = storage.load_current_embryo()
if current_embryo:
    engine.current_embryo = current_embryo
    current_embryo.set_asset_library(asset_library)


def get_engine():
    """Get engine with current embryo loaded"""
    global engine
    embryo = storage.load_current_embryo()
    if embryo:
        engine.current_embryo = embryo
        embryo.set_asset_library(asset_library)
    return engine


@app.route('/')
def dashboard():
    """Main dashboard showing embryo status"""
    eng = get_engine()

    embryos = storage.list_embryos()
    stories = storage.list_stories(limit=5)

    status = None
    if eng.current_embryo:
        status = eng.get_status()

    return render_template('dashboard.html',
                         status=status,
                         embryos=embryos,
                         stories=stories)


@app.route('/init', methods=['POST'])
def init_embryo():
    """Initialize a new embryo"""
    name = request.form.get('name', 'embryo_1')

    initial_dna = {
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

    eng = get_engine()
    embryo = eng.initialize_embryo(initial_dna, name=name)
    eng.save_embryo()

    return redirect(url_for('dashboard'))


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    """Story generator page"""
    eng = get_engine()

    if not eng.current_embryo:
        return redirect(url_for('dashboard'))

    story_structure = None
    cells_data = None

    if request.method == 'POST':
        duration = float(request.form.get('duration', 30))
        subject = request.form.get('subject', '')

        cells, yaml_structure = eng.generate_story(duration, subject)

        story_structure = yaml_structure.get('story', yaml_structure)
        cells_data = [cell.to_dict() for cell in cells]

    assets = asset_library.list_assets()
    status = eng.get_status()

    return render_template('generate.html',
                         status=status,
                         assets=assets,
                         story=story_structure,
                         cells=cells_data)


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Feedback UI for rating content"""
    eng = get_engine()

    if not eng.current_embryo:
        return redirect(url_for('dashboard'))

    result = None

    if request.method == 'POST':
        engagement = float(request.form.get('engagement', 0.5))
        coherence = float(request.form.get('coherence', 0.5))
        quality = float(request.form.get('quality', 0.5))
        timing = float(request.form.get('timing', 0.5))

        # Get last story and reconstruct cells
        last_story = storage.get_last_story(eng.current_embryo.name)

        if last_story:
            cells = []
            for cell_data in last_story.get('cells', []):
                cell = LearningCell(
                    embryo_id=cell_data.get('embryo_id', eng.current_embryo.id),
                    position=cell_data.get('position', 0),
                    arc_position=cell_data.get('arc', 'setup'),
                    duration=cell_data.get('duration', 10.0),
                    intensity=cell_data.get('parameters', {}).get('intensity', 0.5),
                    temperature=cell_data.get('parameters', {}).get('temperature', 0.5),
                    parent_dna=eng.current_embryo.dna,
                    assets=cell_data.get('assets', {})
                )
                cells.append(cell)

            if cells:
                metrics = PerformanceMetrics(
                    engagement_score=engagement,
                    narrative_coherence=coherence,
                    visual_quality=quality,
                    timing_effectiveness=timing
                )

                old_gen = eng.current_embryo.generation
                evolved = eng.provide_feedback(metrics, cells=cells)

                result = {
                    'success': True,
                    'old_generation': old_gen,
                    'new_generation': evolved.generation,
                    'overall_score': metrics.overall_score(),
                    'metrics': metrics.to_dict()
                }

    status = eng.get_status()
    last_story = storage.get_last_story(eng.current_embryo.name) if eng.current_embryo else None

    return render_template('feedback.html',
                         status=status,
                         last_story=last_story,
                         result=result)


@app.route('/lineage')
def lineage():
    """Lineage viewer showing parameter evolution"""
    eng = get_engine()

    if not eng.current_embryo:
        return redirect(url_for('dashboard'))

    timeline = storage.get_evolution_timeline(eng.current_embryo.name)
    status = eng.get_status()

    # Prepare chart data
    chart_data = {
        'generations': [],
        'scores': [],
        'engagement': [],
        'coherence': [],
        'setup_intensity': [],
        'conflict_intensity': [],
        'resolution_intensity': []
    }

    for entry in timeline:
        chart_data['generations'].append(entry.get('generation', 0))
        chart_data['scores'].append(entry.get('overall_score', 0))

        perf = entry.get('performance', {})
        chart_data['engagement'].append(perf.get('engagement_score', 0))
        chart_data['coherence'].append(perf.get('narrative_coherence', 0))

        params = entry.get('parameters', {})
        chart_data['setup_intensity'].append(params.get('setup_intensity', 0.3))
        chart_data['conflict_intensity'].append(params.get('conflict_intensity', 0.8))
        chart_data['resolution_intensity'].append(params.get('resolution_intensity', 0.6))

    return render_template('lineage.html',
                         status=status,
                         timeline=timeline,
                         chart_data=chart_data)


@app.route('/api/status')
def api_status():
    """API endpoint for current status"""
    eng = get_engine()
    if eng.current_embryo:
        return jsonify(eng.get_status())
    return jsonify({'error': 'No embryo initialized'})


@app.route('/api/stories')
def api_stories():
    """API endpoint for stories list"""
    stories = storage.list_stories(limit=20)
    return jsonify(stories)


@app.route('/select/<name>')
def select_embryo(name):
    """Select a different embryo as current"""
    embryo = storage.load_embryo(name=name)
    if embryo:
        storage.save_embryo(embryo, set_current=True)
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    print("\n  Embryonic Story System - Web Interface")
    print("  http://localhost:5000\n")
    app.run(debug=True, port=5000)
