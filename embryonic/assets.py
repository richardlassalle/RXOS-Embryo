"""
Asset Library System for Embryonic Story System
Load and manage characters, locations, and objects
"""

import json
import yaml
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Asset:
    """Base asset class"""
    id: str
    name: str
    asset_type: str  # character, location, object
    tags: List[str]
    metadata: Dict[str, Any]
    file_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Asset':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            asset_type=data.get('asset_type', 'unknown'),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
            file_path=data.get('file_path')
        )


class AssetLibrary:
    """Manages asset collections for story generation"""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else None
        self.characters: Dict[str, Asset] = {}
        self.locations: Dict[str, Asset] = {}
        self.objects: Dict[str, Asset] = {}
        self._selection_history = []

    def load_from_directories(self, characters_dir: str = None,
                             locations_dir: str = None,
                             objects_dir: str = None):
        """Load assets from directory structure"""
        if characters_dir:
            self._load_directory(characters_dir, 'character')
        if locations_dir:
            self._load_directory(locations_dir, 'location')
        if objects_dir:
            self._load_directory(objects_dir, 'object')

    def _load_directory(self, dir_path: str, asset_type: str):
        """Load assets from a directory"""
        path = Path(dir_path)
        if not path.exists():
            return

        storage = self._get_storage(asset_type)

        # Load JSON/YAML files
        for file_path in path.glob('*.json'):
            self._load_asset_file(file_path, asset_type, storage)

        for file_path in path.glob('*.yaml'):
            self._load_asset_file(file_path, asset_type, storage)

        for file_path in path.glob('*.yml'):
            self._load_asset_file(file_path, asset_type, storage)

        # Also scan for image files as simple assets
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.webp']
        for ext in image_extensions:
            for file_path in path.glob(ext):
                asset_id = f"{asset_type[:3]}_{file_path.stem}"
                if asset_id not in storage:
                    storage[asset_id] = Asset(
                        id=asset_id,
                        name=file_path.stem.replace('_', ' ').title(),
                        asset_type=asset_type,
                        tags=[],
                        metadata={'source': 'image'},
                        file_path=str(file_path)
                    )

    def _load_asset_file(self, file_path: Path, asset_type: str,
                        storage: Dict[str, Asset]):
        """Load asset from JSON/YAML file"""
        try:
            with open(file_path, 'r') as f:
                if file_path.suffix == '.json':
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            if isinstance(data, list):
                for item in data:
                    asset = self._create_asset(item, asset_type, str(file_path))
                    storage[asset.id] = asset
            elif isinstance(data, dict):
                if 'assets' in data:
                    for item in data['assets']:
                        asset = self._create_asset(item, asset_type, str(file_path))
                        storage[asset.id] = asset
                else:
                    asset = self._create_asset(data, asset_type, str(file_path))
                    storage[asset.id] = asset
        except Exception as e:
            print(f"Warning: Failed to load {file_path}: {e}")

    def _create_asset(self, data: Dict[str, Any], asset_type: str,
                     file_path: str) -> Asset:
        """Create asset from data dict"""
        asset_id = data.get('id', f"{asset_type[:3]}_{data.get('name', 'unknown').lower().replace(' ', '_')}")
        return Asset(
            id=asset_id,
            name=data.get('name', asset_id),
            asset_type=asset_type,
            tags=data.get('tags', []),
            metadata=data.get('metadata', data),
            file_path=file_path
        )

    def _get_storage(self, asset_type: str) -> Dict[str, Asset]:
        """Get storage dict for asset type"""
        if asset_type == 'character':
            return self.characters
        elif asset_type == 'location':
            return self.locations
        elif asset_type == 'object':
            return self.objects
        return {}

    def add_asset(self, asset: Asset):
        """Add a single asset"""
        storage = self._get_storage(asset.asset_type)
        storage[asset.id] = asset

    def add_character(self, id: str, name: str, tags: List[str] = None,
                     metadata: Dict = None):
        """Add a character asset"""
        self.characters[id] = Asset(
            id=id,
            name=name,
            asset_type='character',
            tags=tags or [],
            metadata=metadata or {}
        )

    def add_location(self, id: str, name: str, tags: List[str] = None,
                    metadata: Dict = None):
        """Add a location asset"""
        self.locations[id] = Asset(
            id=id,
            name=name,
            asset_type='location',
            tags=tags or [],
            metadata=metadata or {}
        )

    def add_object(self, id: str, name: str, tags: List[str] = None,
                  metadata: Dict = None):
        """Add an object asset"""
        self.objects[id] = Asset(
            id=id,
            name=name,
            asset_type='object',
            tags=tags or [],
            metadata=metadata or {}
        )

    def select_for_cell(self, arc_position: str,
                       params: Dict[str, float]) -> Dict[str, List[str]]:
        """Select assets for a cell based on arc and parameters"""
        intensity = params.get('intensity', 0.5)

        # Determine counts based on arc position
        if arc_position == 'setup':
            char_count = 1
            loc_count = 1
            obj_count = 1
        elif arc_position == 'conflict':
            char_count = 2
            loc_count = 1
            obj_count = 2
        else:  # resolution
            char_count = 1
            loc_count = 1
            obj_count = 1

        # Select assets
        selected_chars = self._select_random(self.characters, char_count)
        selected_locs = self._select_random(self.locations, loc_count)
        selected_objs = self._select_random(self.objects, obj_count)

        selection = {
            'characters': selected_chars,
            'locations': selected_locs,
            'objects': selected_objs
        }

        self._selection_history.append({
            'arc': arc_position,
            'params': params,
            'selection': selection,
            'timestamp': datetime.now().isoformat()
        })

        return selection

    def _select_random(self, storage: Dict[str, Asset], count: int) -> List[str]:
        """Select random assets from storage"""
        if not storage:
            return []
        ids = list(storage.keys())
        return random.sample(ids, min(count, len(ids)))

    def select_by_tags(self, asset_type: str, tags: List[str],
                      count: int = 1) -> List[str]:
        """Select assets that match any of the given tags"""
        storage = self._get_storage(asset_type)
        matching = [
            asset_id for asset_id, asset in storage.items()
            if any(tag in asset.tags for tag in tags)
        ]
        if not matching:
            return self._select_random(storage, count)
        return random.sample(matching, min(count, len(matching)))

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """Get asset by ID"""
        for storage in [self.characters, self.locations, self.objects]:
            if asset_id in storage:
                return storage[asset_id]
        return None

    def list_assets(self, asset_type: str = None) -> List[Dict[str, Any]]:
        """List all assets or assets of a specific type"""
        result = []
        if asset_type is None or asset_type == 'character':
            result.extend([a.to_dict() for a in self.characters.values()])
        if asset_type is None or asset_type == 'location':
            result.extend([a.to_dict() for a in self.locations.values()])
        if asset_type is None or asset_type == 'object':
            result.extend([a.to_dict() for a in self.objects.values()])
        return result

    def get_stats(self) -> Dict[str, int]:
        """Get asset library statistics"""
        return {
            'characters': len(self.characters),
            'locations': len(self.locations),
            'objects': len(self.objects),
            'total': len(self.characters) + len(self.locations) + len(self.objects)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Export library to dictionary"""
        return {
            'characters': [a.to_dict() for a in self.characters.values()],
            'locations': [a.to_dict() for a in self.locations.values()],
            'objects': [a.to_dict() for a in self.objects.values()]
        }

    def save(self, filepath: str):
        """Save library to file"""
        with open(filepath, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

    def load(self, filepath: str):
        """Load library from file"""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)

        for char_data in data.get('characters', []):
            self.characters[char_data['id']] = Asset.from_dict(char_data)
        for loc_data in data.get('locations', []):
            self.locations[loc_data['id']] = Asset.from_dict(loc_data)
        for obj_data in data.get('objects', []):
            self.objects[obj_data['id']] = Asset.from_dict(obj_data)


def create_sample_library() -> AssetLibrary:
    """Create a sample asset library for testing"""
    library = AssetLibrary()

    # Add sample characters
    library.add_character('chr_detective', 'Detective Noir',
                         tags=['protagonist', 'mysterious', 'serious'],
                         metadata={'description': 'A world-weary detective'})
    library.add_character('chr_femme_fatale', 'Mysterious Woman',
                         tags=['supporting', 'mysterious', 'dangerous'],
                         metadata={'description': 'A woman with secrets'})
    library.add_character('chr_villain', 'The Mastermind',
                         tags=['antagonist', 'intelligent', 'threatening'],
                         metadata={'description': 'The one behind it all'})

    # Add sample locations
    library.add_location('loc_alley', 'Dark Alley',
                        tags=['urban', 'night', 'dangerous'],
                        metadata={'mood': 'tense'})
    library.add_location('loc_cafe', 'Neon Cafe',
                        tags=['urban', 'night', 'social'],
                        metadata={'mood': 'mysterious'})
    library.add_location('loc_office', 'Private Office',
                        tags=['indoor', 'professional', 'private'],
                        metadata={'mood': 'contemplative'})

    # Add sample objects
    library.add_object('obj_cigarette', 'Lit Cigarette',
                      tags=['prop', 'atmospheric'],
                      metadata={'symbolism': 'time, mortality'})
    library.add_object('obj_briefcase', 'Leather Briefcase',
                      tags=['prop', 'macguffin'],
                      metadata={'symbolism': 'secrets, value'})
    library.add_object('obj_gun', 'Revolver',
                      tags=['prop', 'weapon', 'danger'],
                      metadata={'symbolism': 'power, violence'})
    library.add_object('obj_photo', 'Faded Photograph',
                      tags=['prop', 'clue'],
                      metadata={'symbolism': 'memory, loss'})

    return library
