# EMBRYONIC STORY SYSTEM - Claude Code Brief

## Overview

Build a video production application based on a biological "embryonic" architecture. The system uses a three-point story arc (Setup, Conflict, Resolution) as its fundamental DNA, with parametric cascade that learns and evolves over time.

## Core Concept

Think of it like biological cell division:
- **Embryo** = Universal template holding the story DNA
- **Seed** = Target duration that triggers cell division
- **Cells** = Individual story units that inherit DNA but specialize
- **Learning** = System gets smarter with each generation based on feedback

A 30-second commercial creates 3 cells. A 10-minute film creates many more. Same DNA, different division patterns.

## Foundation Files

Two files are provided as the foundation:

### 1. learning_embryonic_system.py
Complete Python implementation including:
- `LearningEmbryo` - Holds DNA and learns from feedback
- `LearningCell` - Individual story units with performance tracking
- `LearningParameters` - Parameters that evolve toward what works
- `StoryEvolutionEngine` - Manages the full lifecycle
- `PerformanceMetrics` - Feedback structure for learning

### 2. embryonic_story_structure.yaml
Data structure showing:
- Embryo DNA with arc structure and transformation rules
- Cell division output with parameter cascade
- Learning feedback loop structure
- Asset library references

## What To Build

### Phase 1: Core Application
1. **CLI Interface** - Commands to create embryos, generate stories, provide feedback
2. **Persistent Storage** - Save embryo lineage and learning history (SQLite or JSON)
3. **Asset Library Integration** - Load characters, locations, objects from folders or database

### Phase 2: Web Interface (Optional)
1. **Dashboard** - View current embryo generation and learned parameters
2. **Story Generator** - Input duration, select assets, generate cell structure
3. **Feedback UI** - Rate generated content to trigger evolution
4. **Lineage Viewer** - Visualize how parameters evolved over generations

### Phase 3: AI Integration (Future)
1. **Content Generation** - Connect cells to actual AI generation (images, video)
2. **Automatic Feedback** - Use AI to evaluate coherence, quality, engagement
3. **Asset Library Population** - Generate and store consistent characters/locations

## Key Architecture Principles

1. **Simplicity First** - The three-point arc is the foundation for everything
2. **Parametric Cascade** - Parameters flow down and specialize at each level
3. **Learning Over Time** - System improves through feedback, not manual tuning
4. **Universal Application** - Same structure works for any subject matter

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

## Example Commands (CLI)

```bash
# Initialize new embryo
embryo init --name "commercial_v1"

# Load asset libraries
embryo assets --characters ./assets/characters --locations ./assets/locations

# Generate 30-second story
embryo generate --duration 30 --subject "car commercial"

# Provide feedback
embryo feedback --engagement 0.85 --coherence 0.9 --quality 0.8 --timing 0.7

# View current learned parameters
embryo status

# Export story structure
embryo export --format yaml --output story.yaml
```

## Success Criteria

- Can generate story structures for any duration (30 seconds to 10+ minutes)
- Learning visibly improves parameter selections over multiple generations
- Clean, minimal codebase that can be extended
- Works standalone without complex dependencies

## Notes

This is a fresh architecture inspired by but separate from RXOS. Keep it clean and pure. The goal is something buildable in 1-2 days that can be used immediately and extended over time.
