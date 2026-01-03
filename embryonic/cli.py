"""
CLI Interface for Embryonic Story System
Commands to create embryos, generate stories, and provide feedback
"""

import argparse
import sys
import yaml
import json
from pathlib import Path
from typing import Optional

from .core import StoryEvolutionEngine, PerformanceMetrics, LearningEmbryo, LearningCell
from .storage import EmbryoStorage
from .assets import AssetLibrary, create_sample_library


class EmbryoCLI:
    """Command-line interface for the embryonic story system"""

    def __init__(self):
        self.storage = EmbryoStorage()
        self.asset_library = AssetLibrary()
        self.engine = StoryEvolutionEngine(
            storage=self.storage,
            asset_library=self.asset_library
        )

    def init(self, args):
        """Initialize a new embryo"""
        name = args.name

        # Check if embryo with this name already exists
        existing = self.storage.load_embryo(name=name)
        if existing and not args.force:
            print(f"Embryo '{name}' already exists. Use --force to overwrite.")
            return 1

        # Create initial DNA
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

        embryo = self.engine.initialize_embryo(initial_dna, name=name)
        self.engine.save_embryo()

        print(f"Created embryo: {embryo.name}")
        print(f"  ID: {embryo.id}")
        print(f"  Generation: {embryo.generation}")
        print(f"  Ready for story generation!")

        return 0

    def generate(self, args):
        """Generate a story"""
        duration = args.duration
        subject = args.subject or ""

        # Load current embryo
        if args.embryo:
            embryo = self.engine.load_embryo(name=args.embryo)
        else:
            embryo = self.storage.load_current_embryo()
            if embryo:
                self.engine.current_embryo = embryo
                if self.engine.asset_library:
                    embryo.set_asset_library(self.engine.asset_library)

        if not embryo:
            print("No embryo found. Create one with: embryo init --name <name>")
            return 1

        # Generate story
        cells, yaml_structure = self.engine.generate_story(duration, subject)

        print(f"\nGenerated story from embryo '{embryo.name}' (Gen {embryo.generation})")
        print(f"Duration: {duration}s | Cells: {len(cells)}")
        print("\n--- Story Structure ---")

        # Print arc breakdown
        for arc in ['setup', 'conflict', 'resolution']:
            arc_cells = [c for c in cells if c.arc_position == arc]
            if arc_cells:
                total_dur = sum(c.duration for c in arc_cells)
                avg_intensity = sum(c.intensity for c in arc_cells) / len(arc_cells)
                print(f"\n{arc.upper()} ({len(arc_cells)} cells, {total_dur:.1f}s)")
                for cell in arc_cells:
                    print(f"  [{cell.id}] dur={cell.duration:.1f}s "
                          f"int={cell.intensity:.2f} temp={cell.temperature:.2f}")
                    if cell.asset_selections.get('characters'):
                        print(f"    characters: {', '.join(cell.asset_selections['characters'])}")

        # Export if requested
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                if args.format == 'json':
                    json.dump(yaml_structure, f, indent=2)
                else:
                    yaml.dump(yaml_structure, f, default_flow_style=False, sort_keys=False)
            print(f"\nExported to: {output_path}")

        print("\nProvide feedback with: embryo feedback --engagement <0-1> --coherence <0-1> --quality <0-1> --timing <0-1>")

        return 0

    def feedback(self, args):
        """Provide feedback on the last generated story"""
        # Load current embryo
        embryo = self.storage.load_current_embryo()
        if embryo:
            self.engine.current_embryo = embryo

        if not self.engine.current_embryo:
            print("No embryo loaded. Generate a story first.")
            return 1

        # Get last generated cells from stored story
        cells = self.engine.last_generated_cells
        if not cells:
            # Reconstruct cells from stored story
            last_story = self.storage.get_last_story(self.engine.current_embryo.name)
            if not last_story:
                print("No recent story to provide feedback on. Generate a story first.")
                return 1

            # Reconstruct cells from story data
            cells = []
            for cell_data in last_story.get('cells', []):
                cell = LearningCell(
                    embryo_id=cell_data.get('embryo_id', self.engine.current_embryo.id),
                    position=cell_data.get('position', 0),
                    arc_position=cell_data.get('arc', 'setup'),
                    duration=cell_data.get('duration', 10.0),
                    intensity=cell_data.get('parameters', {}).get('intensity', 0.5),
                    temperature=cell_data.get('parameters', {}).get('temperature', 0.5),
                    parent_dna=self.engine.current_embryo.dna,
                    assets=cell_data.get('assets', {})
                )
                cell.id = cell_data.get('id', cell.id)
                cells.append(cell)

            if not cells:
                print("No cells found in last story. Generate a new story first.")
                return 1

        metrics = PerformanceMetrics(
            engagement_score=args.engagement,
            narrative_coherence=args.coherence,
            visual_quality=args.quality,
            timing_effectiveness=args.timing
        )

        old_gen = self.engine.current_embryo.generation
        evolved_embryo = self.engine.provide_feedback(metrics, cells=cells)

        print(f"\nFeedback received!")
        print(f"  Engagement: {args.engagement:.2f}")
        print(f"  Coherence: {args.coherence:.2f}")
        print(f"  Quality: {args.quality:.2f}")
        print(f"  Timing: {args.timing:.2f}")
        print(f"  Overall Score: {metrics.overall_score():.3f}")
        print(f"\nEvolved: Generation {old_gen} -> {evolved_embryo.generation}")

        # Show parameter changes
        params = evolved_embryo.learning_params.get_optimized_params()
        print("\nUpdated parameters:")
        for arc in ['setup', 'conflict', 'resolution']:
            print(f"  {arc}: intensity={params[f'{arc}_intensity']:.3f}, "
                  f"temperature={params[f'{arc}_temperature']:.3f}")

        return 0

    def status(self, args):
        """Show current embryo status"""
        if args.name:
            embryo = self.storage.load_embryo(name=args.name)
            if embryo:
                self.engine.current_embryo = embryo
        else:
            embryo = self.storage.load_current_embryo()
            if embryo:
                self.engine.current_embryo = embryo

        status = self.engine.get_status()

        if status.get('status') == 'No embryo initialized':
            print("No embryo initialized. Create one with: embryo init --name <name>")
            return 1

        print("\n=== Embryo Status ===")
        print(f"Name: {status['embryo']['name']}")
        print(f"ID: {status['embryo']['id']}")
        print(f"Generation: {status['embryo']['generation']}")
        print(f"Total Offspring: {status['embryo']['offspring_count']}")
        print(f"Created: {status['embryo']['birth_time']}")

        print("\n--- Learned Parameters ---")
        for arc in ['setup', 'conflict', 'resolution']:
            p = status['learned_parameters'][arc]
            print(f"{arc.upper()}:")
            print(f"  intensity: {p['intensity']} | temperature: {p['temperature']} | duration: {p['duration_ratio']*100:.1f}%")

        if status.get('last_performance'):
            print("\n--- Last Performance ---")
            lp = status['last_performance']
            print(f"  Engagement: {lp.get('engagement_score', 'N/A')}")
            print(f"  Coherence: {lp.get('narrative_coherence', 'N/A')}")
            print(f"  Quality: {lp.get('visual_quality', 'N/A')}")
            print(f"  Timing: {lp.get('timing_effectiveness', 'N/A')}")

        print(f"\nGeneration History: {status['generation_history_count']} entries")

        return 0

    def list_cmd(self, args):
        """List embryos or stories"""
        if args.type == 'embryos':
            embryos = self.storage.list_embryos()
            if not embryos:
                print("No embryos found. Create one with: embryo init --name <name>")
                return 0

            print("\n=== Embryos ===")
            for e in embryos:
                current = " (current)" if e.get('is_current') else ""
                print(f"  {e['name']}{current}")
                print(f"    Generation: {e['generation']} | Offspring: {e['offspring_count']}")
                print(f"    Updated: {e['updated_at']}")

        elif args.type == 'stories':
            stories = self.storage.list_stories(limit=args.limit or 10)
            if not stories:
                print("No stories found. Generate one with: embryo generate --duration <seconds>")
                return 0

            print("\n=== Stories ===")
            for s in stories:
                print(f"  [{s['id']}] {s['embryo_name']} Gen{s['generation']}")
                print(f"    Subject: {s['subject'] or '(none)'} | Duration: {s['target_duration']}s | Cells: {s['cell_count']}")
                print(f"    Generated: {s['generated_at']}")

        return 0

    def assets(self, args):
        """Manage asset library"""
        if args.characters:
            self.asset_library.load_from_directories(characters_dir=args.characters)
            print(f"Loaded characters from: {args.characters}")

        if args.locations:
            self.asset_library.load_from_directories(locations_dir=args.locations)
            print(f"Loaded locations from: {args.locations}")

        if args.objects:
            self.asset_library.load_from_directories(objects_dir=args.objects)
            print(f"Loaded objects from: {args.objects}")

        if args.sample:
            self.asset_library = create_sample_library()
            self.engine.asset_library = self.asset_library
            print("Loaded sample asset library")

        if args.list:
            assets = self.asset_library.list_assets(args.list if args.list != 'all' else None)
            if not assets:
                print("No assets loaded. Use --sample for demo or load from directories.")
                return 0

            print("\n=== Asset Library ===")
            current_type = None
            for a in assets:
                if a['asset_type'] != current_type:
                    current_type = a['asset_type']
                    print(f"\n{current_type.upper()}S:")
                print(f"  {a['id']}: {a['name']}")
                if a.get('tags'):
                    print(f"    tags: {', '.join(a['tags'])}")

        # Show stats
        stats = self.asset_library.get_stats()
        if stats['total'] > 0:
            print(f"\nAsset Library: {stats['characters']} characters, "
                  f"{stats['locations']} locations, {stats['objects']} objects")

        return 0

    def export(self, args):
        """Export story or lineage"""
        output = args.output
        fmt = args.format or 'yaml'

        if args.lineage:
            # Export embryo lineage
            name = args.lineage
            filepath = output or f"{name}_lineage.yaml"
            if self.storage.export_lineage(name, filepath):
                print(f"Exported lineage to: {filepath}")
            else:
                print(f"Embryo '{name}' not found")
                return 1

        elif args.story:
            # Export specific story
            story = self.storage.get_story(args.story)
            if not story:
                print(f"Story {args.story} not found")
                return 1

            filepath = output or f"story_{args.story}.{fmt}"
            with open(filepath, 'w') as f:
                if fmt == 'json':
                    json.dump(story, f, indent=2)
                else:
                    yaml.dump(story, f, default_flow_style=False, sort_keys=False)
            print(f"Exported story to: {filepath}")

        else:
            # Export current embryo status
            embryo = self.storage.load_current_embryo()
            if not embryo:
                print("No current embryo to export")
                return 1

            filepath = output or f"{embryo.name}_export.{fmt}"
            embryo.save_lineage(filepath)
            print(f"Exported embryo to: {filepath}")

        return 0

    def history(self, args):
        """Show evolution history"""
        name = args.name
        embryo = self.storage.load_embryo(name=name) if name else self.storage.load_current_embryo()

        if not embryo:
            print("No embryo found. Specify --name or create one.")
            return 1

        timeline = self.storage.get_evolution_timeline(embryo.name)

        if not timeline:
            print(f"No evolution history for '{embryo.name}'")
            print("Generate stories and provide feedback to build history.")
            return 0

        print(f"\n=== Evolution History: {embryo.name} ===")
        for entry in timeline:
            print(f"\nGeneration {entry['generation']} ({entry['timestamp']})")
            if entry.get('performance'):
                p = entry['performance']
                score = entry.get('overall_score', 'N/A')
                print(f"  Score: {score:.3f}" if isinstance(score, float) else f"  Score: {score}")
                print(f"  Engagement: {p.get('engagement_score', 'N/A')}")
            if entry.get('parameters'):
                print(f"  Cells: {entry.get('cell_count', 'N/A')}")

        return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='embryo',
        description='Embryonic Story System - Biological-inspired story generation with learning'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # init command
    init_parser = subparsers.add_parser('init', help='Initialize a new embryo')
    init_parser.add_argument('--name', '-n', required=True, help='Name for the embryo')
    init_parser.add_argument('--force', '-f', action='store_true', help='Overwrite if exists')

    # generate command
    gen_parser = subparsers.add_parser('generate', help='Generate a story')
    gen_parser.add_argument('--duration', '-d', type=float, required=True,
                           help='Target duration in seconds')
    gen_parser.add_argument('--subject', '-s', help='Subject hint for generation')
    gen_parser.add_argument('--embryo', '-e', help='Embryo name to use')
    gen_parser.add_argument('--output', '-o', help='Output file path')
    gen_parser.add_argument('--format', '-f', choices=['yaml', 'json'], default='yaml',
                           help='Output format')

    # feedback command
    fb_parser = subparsers.add_parser('feedback', help='Provide feedback on last story')
    fb_parser.add_argument('--engagement', type=float, required=True,
                          help='Engagement score (0-1)')
    fb_parser.add_argument('--coherence', type=float, required=True,
                          help='Narrative coherence score (0-1)')
    fb_parser.add_argument('--quality', type=float, required=True,
                          help='Visual quality score (0-1)')
    fb_parser.add_argument('--timing', type=float, required=True,
                          help='Timing effectiveness score (0-1)')

    # status command
    status_parser = subparsers.add_parser('status', help='Show embryo status')
    status_parser.add_argument('--name', '-n', help='Embryo name (default: current)')

    # list command
    list_parser = subparsers.add_parser('list', help='List embryos or stories')
    list_parser.add_argument('type', choices=['embryos', 'stories'],
                            help='What to list')
    list_parser.add_argument('--limit', '-l', type=int, help='Limit results')

    # assets command
    assets_parser = subparsers.add_parser('assets', help='Manage asset library')
    assets_parser.add_argument('--characters', '-c', help='Characters directory')
    assets_parser.add_argument('--locations', '-l', help='Locations directory')
    assets_parser.add_argument('--objects', '-o', help='Objects directory')
    assets_parser.add_argument('--sample', action='store_true', help='Load sample library')
    assets_parser.add_argument('--list', nargs='?', const='all',
                              help='List assets (optionally by type)')

    # export command
    export_parser = subparsers.add_parser('export', help='Export story or lineage')
    export_parser.add_argument('--output', '-o', help='Output file path')
    export_parser.add_argument('--format', '-f', choices=['yaml', 'json'], default='yaml',
                              help='Output format')
    export_parser.add_argument('--lineage', help='Export lineage for embryo name')
    export_parser.add_argument('--story', type=int, help='Export story by ID')

    # history command
    hist_parser = subparsers.add_parser('history', help='Show evolution history')
    hist_parser.add_argument('--name', '-n', help='Embryo name')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    cli = EmbryoCLI()

    commands = {
        'init': cli.init,
        'generate': cli.generate,
        'feedback': cli.feedback,
        'status': cli.status,
        'list': cli.list_cmd,
        'assets': cli.assets,
        'export': cli.export,
        'history': cli.history,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
