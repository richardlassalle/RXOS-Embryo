# Embryonic Story System

A biological-inspired parametric cascade system for video production. Uses a three-point story arc (Setup, Conflict, Resolution) as its fundamental DNA, with parameters that learn and evolve based on feedback.

## Concept

Think of it like biological cell division:

- **Embryo** = Universal template holding the story DNA
- **Seed** = Target duration that triggers cell division
- **Cells** = Individual story units that inherit DNA but specialize
- **Learning** = System gets smarter with each generation based on feedback

A 30-second commercial creates 3 cells. A 10-minute film creates many more. Same DNA, different division patterns.

## Installation

```bash
git clone git@github.com:richardlassalle/RXOS-Embryo.git
cd RXOS-Embryo
pip install -r requirements.txt
```

## Quick Start

```bash
# Initialize a new embryo
./embryo init --name "my_project"

# Generate a 30-second story
./embryo generate --duration 30 --subject "coffee commercial"

# Provide feedback to trigger evolution
./embryo feedback --engagement 0.85 --coherence 0.9 --quality 0.8 --timing 0.7

# Check current status and learned parameters
./embryo status
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `embryo init --name <name>` | Create a new embryo |
| `embryo generate --duration <secs>` | Generate story cells |
| `embryo feedback --engagement <0-1> ...` | Provide feedback to evolve |
| `embryo status` | View embryo and learned parameters |
| `embryo list embryos` | List all embryos |
| `embryo list stories` | List generated stories |
| `embryo assets --sample` | Load sample asset library |
| `embryo assets --characters <dir>` | Load assets from directory |
| `embryo export --lineage <name>` | Export evolution history |
| `embryo history` | View evolution timeline |

## Cell Division Pattern

Duration determines how many cells are created:

| Duration | Cells | Pattern |
|----------|-------|---------|
| ≤30s | 3 | 1 per arc |
| ≤120s | 6 | 2 per arc |
| ≤300s | 9 | 3 per arc |
| >300s | n | ~1 per 30s |

Each cell inherits the embryo's DNA but specializes based on its arc position:

```
SETUP      → Low intensity (0.3), High temperature (0.7)
CONFLICT   → High intensity (0.8), Medium temperature (0.5)
RESOLUTION → Medium intensity (0.6), Low temperature (0.4)
```

## Learning System

The system learns from feedback and evolves parameters over generations:

```
Generate Story → User Feedback → Learn → Evolve → Next Generation
```

Feedback metrics:
- **Engagement** (0-1): How engaging was the content?
- **Coherence** (0-1): Did the narrative flow well?
- **Quality** (0-1): Visual/production quality
- **Timing** (0-1): Was the pacing effective?

Parameters that consistently perform well expand their "successful range" and influence future generations.

## Asset Library

Load characters, locations, and objects from YAML files:

```yaml
# assets/characters/cast.yaml
assets:
  - id: chr_detective
    name: Detective Noir
    tags: [protagonist, mysterious]
    metadata:
      description: A world-weary detective
```

Or use the built-in sample library:

```bash
./embryo assets --sample --list
```

## Architecture

```
embryonic/
├── core.py      # LearningEmbryo, LearningCell, StoryEvolutionEngine
├── storage.py   # SQLite persistence layer
├── assets.py    # Asset library management
└── cli.py       # Command-line interface
```

### Core Classes

- **LearningEmbryo**: Holds DNA and learning parameters, creates cells through division
- **LearningCell**: Individual story unit with arc position, duration, intensity, temperature
- **LearningParameters**: Tracks parameter effectiveness and evolves toward optimal values
- **StoryEvolutionEngine**: Orchestrates generation, feedback, and evolution
- **EmbryoStorage**: SQLite persistence for embryos, stories, and feedback history

## Data Flow

```
User Input (duration, subject)
        ↓
    Embryo DNA
        ↓
  Stimulate Division
        ↓
    Create Cells
   (inherit + specialize)
        ↓
  Generate Content
        ↓
   User Feedback
        ↓
  Learn & Evolve
        ↓
  Next Generation Embryo
```

## Example Output

```bash
$ ./embryo generate --duration 60 --subject "dog food commercial"

Generated story from embryo 'commercial_v1' (Gen 2)
Duration: 60.0s | Cells: 6

--- Story Structure ---

SETUP (2 cells, 19.8s)
  [cell_080f1284] dur=9.9s int=0.30 temp=0.70
  [cell_2cc974fe] dur=9.9s int=0.30 temp=0.70

CONFLICT (2 cells, 20.4s)
  [cell_370f0b38] dur=10.2s int=0.80 temp=0.50
  [cell_4da07ded] dur=10.2s int=0.80 temp=0.50

RESOLUTION (2 cells, 19.8s)
  [cell_a7a2d90c] dur=9.9s int=0.60 temp=0.40
  [cell_363832e6] dur=9.9s int=0.60 temp=0.40
```

## Export Formats

Export stories or lineage history to YAML or JSON:

```bash
# Export specific story
./embryo export --story 1 --format yaml --output story.yaml

# Export full lineage history
./embryo export --lineage my_project --output lineage.yaml
```

## Future Extensions

- **Web Interface**: Dashboard for visualization and interaction
- **AI Integration**: Connect cells to image/video generation
- **Automatic Feedback**: Use AI to evaluate coherence and quality
- **Asset Generation**: Create consistent characters/locations with AI

## License

MIT
