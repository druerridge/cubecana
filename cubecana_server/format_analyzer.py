"""
Format Analyzer module for analyzing Lorcana draft formats from draftmancer files.
"""
import tempfile
import os
import json
import re
from typing import Dict, List, Any, Optional
from cubecana_server import draftmancer
from cubecana_server.lorcast_api import lorcast_api
from cubecana_server import id_helper


class FormatAnalyzer:
    """Analyzes Lorcana draft formats from draftmancer files to extract comprehensive format statistics."""
    
    def __init__(self):
        self.draftmancer_file = None
        self.settings = {}
        self.custom_cards = []
        self.card_slot_data = {}
        
    def analyze_format(self, draftmancer_file_contents: str) -> Dict[str, Any]:
        """
        Parse draftmancer file and generate comprehensive format analysis data.
        
        Args:
            draftmancer_file_contents: Raw text content of the draftmancer file
            
        Returns:
            Dictionary containing all format analysis data including cards, traits, distributions, and settings
        """
        try:
            # Parse the draftmancer file
            self._parse_draftmancer_file(draftmancer_file_contents)
            
            # Parse settings from the file content
            self._parse_settings(draftmancer_file_contents)
            
            # Calculate player limits based on settings
            max_players = self._calculate_max_players(draftmancer_file_contents)
            
            # Extract slot information and card frequencies
            self._extract_slot_data(draftmancer_file_contents)
            
            # Build comprehensive card analysis
            analysis_data = self._build_card_analysis(max_players)
            
            print(f"Successfully analyzed format with {len(self.custom_cards)} cards and {len(analysis_data['traits'])} traits")
            
            return analysis_data
            
        except Exception as e:
            print(f"Error analyzing format: {e}")
            import traceback
            traceback.print_exc()
            return self._get_empty_analysis()
    
    def _parse_draftmancer_file(self, file_contents: str) -> None:
        """Parse the draftmancer file using existing parsing logic."""
        # Create a temporary file to use existing parsing logic
        with tempfile.NamedTemporaryFile(mode='w', suffix='.draftmancer.txt', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(file_contents)
            temp_file_path = temp_file.name
        
        try:
            # Parse using existing logic
            self.draftmancer_file = draftmancer.read_draftmancer_file(temp_file_path)
            
            if not self.draftmancer_file:
                raise ValueError("Failed to parse draftmancer file")
            
            # Extract cards from the parsed data
            self.custom_cards = list(self.draftmancer_file.id_to_custom_card.values())
            
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
    
    def _parse_settings(self, file_contents: str) -> None:
        """Parse the settings section from the draftmancer file."""
        lines = file_contents.split('\n')
        in_settings = False
        settings_json = ""
        
        for line in lines:
            if line.strip() == '[Settings]':
                in_settings = True
                continue
            elif line.startswith('[') and in_settings:
                # End of settings section
                if settings_json.strip():
                    try:
                        self.settings = json.loads(settings_json)
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse settings JSON: {e}")
                        self.settings = {}
                in_settings = False
                break
            elif in_settings:
                settings_json += line + '\n'
        
        # Set defaults if not found
        if not self.settings:
            self.settings = {
                'boostersPerPlayer': 3,
                'withReplacement': True,
                'name': 'Unknown Set'
            }
    
    def _calculate_max_players(self, file_contents: str) -> int:
        """Calculate maximum pod size based on card availability and settings."""
        boosters_per_player = self.settings.get('boostersPerPlayer', 3)
        with_replacement = self.settings.get('withReplacement', True)
        
        if with_replacement:
            # For retail sets with replacement (weights), always 8 players max
            return 8
        else:
            # For cubes without replacement, calculate based on total cards available
            lines = file_contents.split('\n')
            total_cards_per_pack = 0
            
            for line in lines:
                if line.startswith('[') and ('Slot' in line or 'slot' in line.lower()):
                    # Extract slot count from parentheses like "[MainSlot(12)]"
                    match = re.search(r'\((\d+)\)', line)
                    if match:
                        total_cards_per_pack += int(match.group(1))
            
            # Calculate total unique cards available from all slots
            total_unique_cards = len(self.custom_cards)
            
            # Each player needs: boosters_per_player * total_cards_per_pack cards
            cards_needed_per_player = boosters_per_player * total_cards_per_pack
            
            # Maximum players is limited by available cards (min 2, max 8)
            if cards_needed_per_player > 0:
                return min(8, max(2, total_unique_cards // cards_needed_per_player))
            else:
                return 8  # Fallback if calculation fails
    
    def _extract_slot_data(self, file_contents: str) -> None:
        """Extract slot information and card frequencies from the draftmancer file."""
        lines = file_contents.split('\n')
        current_slot = None
        current_slot_count = 0
        
        for line in lines:
            if line.startswith('[') and ('Slot' in line or 'slot' in line.lower()):
                # Parse slot header like "[CommonSlotSteel(1)]"
                current_slot = line.strip()
                # Extract slot count from parentheses
                match = re.search(r'\((\d+)\)', line)
                current_slot_count = int(match.group(1)) if match else 1
                continue
            elif line.startswith('[') and current_slot:
                current_slot = None
                current_slot_count = 0
            elif current_slot and line.strip():
                # Parse slot line format: "60 Card Name - Version"
                parts = line.strip().split(' ', 1)
                if len(parts) >= 2 and parts[0].isdigit():
                    weight = int(parts[0])
                    card_name = parts[1]
                    card_id = id_helper.to_id(card_name)
                    self.card_slot_data[card_id] = {
                        'weight': weight,
                        'slot_name': current_slot,
                        'slot_count': current_slot_count
                    }
    
    def _build_card_analysis(self, max_players: int) -> Dict[str, Any]:
        """Build comprehensive card analysis data."""
        all_traits = set()
        card_type_counts = {}
        strength_distribution = {}
        willpower_distribution = {}
        trait_calculations = {}  # For trait analysis
        trait_ink_cost_distributions = {}  # For trait by ink cost charts
        
        # Initialize distributions for ink costs 0-8
        for cost in range(9):
            strength_distribution[str(cost)] = {}
            willpower_distribution[str(cost)] = {}
        
        boosters_per_player = self.settings.get('boostersPerPlayer', 4)
        
        for custom_card in self.custom_cards:
            card_name = custom_card.get('name', '')
            card_id = id_helper.to_id(card_name)
            
            # Get API card data - this is our primary source of truth for card properties
            api_card = lorcast_api.get_api_card(card_id)
            
            if not api_card:
                print(f"Warning: No API data found for card '{card_name}', skipping...")
                continue
                
            # Use API card data for all card properties
            ink_cost = min(api_card.cost, 8)  # Cap at 8 for 8+ category
            lorcana_type = self._get_primary_card_type(api_card.types)
            
            # Count card types
            card_type_counts[lorcana_type] = card_type_counts.get(lorcana_type, 0) + 1
            
            # Calculate probabilities and frequencies (only thing we get from draftmancer)
            slot_data = self.card_slot_data.get(card_id, {'weight': 1, 'slot_name': 'Unknown', 'slot_count': 1})
            copies_per_pack = self._calculate_copies_per_pack(card_id, slot_data)
            
            # Calculate expected copies at table
            total_packs = max_players * boosters_per_player
            expected_at_table = copies_per_pack * total_packs
            expected_in_seat = copies_per_pack * boosters_per_player
            
            # Update distributions and traits using API data
            traits = api_card.classifications or []
            all_traits.update(traits)
            self._update_distributions(api_card, ink_cost, strength_distribution, willpower_distribution)
            
            # Build trait calculations for each trait this card has
            for trait in traits:
                if trait not in trait_calculations:
                    trait_calculations[trait] = {
                        'expectedAtTable': 0,
                        'expectedInSeat': 0
                    }
                trait_calculations[trait]['expectedAtTable'] += expected_at_table
                trait_calculations[trait]['expectedInSeat'] += expected_in_seat
                
                # Track trait by ink cost distribution
                if trait not in trait_ink_cost_distributions:
                    trait_ink_cost_distributions[trait] = {}
                if str(ink_cost) not in trait_ink_cost_distributions[trait]:
                    trait_ink_cost_distributions[trait][str(ink_cost)] = 0
                trait_ink_cost_distributions[trait][str(ink_cost)] += 1
        
        # Generate chart data structures
        chart_data = self._generate_chart_data(
            card_type_counts, 
            strength_distribution, 
            willpower_distribution,
            trait_calculations,
            trait_ink_cost_distributions
        )
        
        return {
            'cardTypes': card_type_counts,
            'traits': sorted(list(all_traits)),
            'strengthDistribution': strength_distribution,
            'willpowerDistribution': willpower_distribution,
            'traitCalculations': trait_calculations,
            'traitInkCostDistributions': trait_ink_cost_distributions,
            'chartData': chart_data,
            'settings': {
                'boostersPerPlayer': boosters_per_player,
                'name': self.settings.get('name', 'Unknown Set'),
                'withReplacement': self.settings.get('withReplacement', True),
                'playersCount': max_players,
                'totalPacks': max_players * boosters_per_player
            }
        }
    
    def _get_primary_card_type(self, api_types: List[str]) -> str:
        """Get the primary Lorcana card type from API card types list."""
        if not api_types:
            return 'Unknown'
        
        # Priority order for determining primary type
        type_priorities = ['Character', 'Action', 'Song', 'Item', 'Location']
        
        # Find the first type in our priority list
        for priority_type in type_priorities:
            if priority_type in api_types:
                return priority_type
        
        # If none of the standard types found, return the first type
        return api_types[0]
    
    def _generate_chart_data(self, card_type_counts: Dict[str, int], 
                            strength_distribution: Dict[str, Dict[str, int]], 
                            willpower_distribution: Dict[str, Dict[str, int]],
                            trait_calculations: Dict[str, Dict[str, float]],
                            trait_ink_cost_distributions: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        """Generate ready-to-use chart data structures for frontend."""
        
        # Prepare card type chart data
        card_type_chart = {
            'labels': list(card_type_counts.keys()),
            'data': list(card_type_counts.values())
        }
        
        # Prepare strength chart data (organized by ink cost)
        ink_costs = ['0', '1', '2', '3', '4', '5', '6', '7', '8']
        
        # Filter to only include ink costs that have cards
        active_ink_costs = []
        for cost in ink_costs:
            has_cards = any(strength_distribution[cost].get(strength, 0) > 0 
                          for strength in strength_distribution[cost])
            if has_cards:
                active_ink_costs.append(cost)
        
        # If no active costs found, include all (fallback)
        if not active_ink_costs:
            active_ink_costs = ink_costs
            
        strength_chart = {
            'labels': [cost if cost != '8' else '8+' for cost in active_ink_costs],
            'datasets': [],
            'options': {
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'suggestedMax': None  # Will be calculated below
                    }
                }
            }
        }
        
        # Get all unique strength values
        all_strengths = set()
        for cost_dist in strength_distribution.values():
            all_strengths.update(cost_dist.keys())
        
        # Calculate max value for scaling
        max_strength_value = 0
        
        # Create datasets for each strength value
        for strength in sorted(all_strengths, key=lambda x: int(x) if x.isdigit() else 999):
            dataset = {
                'label': f'Strength {strength}',
                'data': [strength_distribution[cost].get(strength, 0) for cost in active_ink_costs],
                'backgroundColor': self._get_strength_color(strength)
            }
            strength_chart['datasets'].append(dataset)
            max_strength_value = max(max_strength_value, max(dataset['data']))
        
        # Add 10% margin to the max value for better visualization
        if max_strength_value > 0:
            strength_chart['options']['scales']['y']['suggestedMax'] = int(max_strength_value * 1.1) + 1
        
        # Prepare willpower chart data (organized by ink cost) 
        # Use the same active ink costs as strength chart for consistency
        willpower_chart = {
            'labels': [cost if cost != '8' else '8+' for cost in active_ink_costs],
            'datasets': [],
            'options': {
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'suggestedMax': None  # Will be calculated below
                    }
                }
            }
        }
        
        # Get all unique willpower values
        all_willpowers = set()
        for cost_dist in willpower_distribution.values():
            all_willpowers.update(cost_dist.keys())
        
        # Calculate max value for scaling
        max_willpower_value = 0
        
        # Create datasets for each willpower value
        for willpower in sorted(all_willpowers, key=lambda x: int(x) if x.isdigit() else 999):
            dataset = {
                'label': f'Willpower {willpower}',
                'data': [willpower_distribution[cost].get(willpower, 0) for cost in active_ink_costs],
                'backgroundColor': self._get_willpower_color(willpower)
            }
            willpower_chart['datasets'].append(dataset)
            max_willpower_value = max(max_willpower_value, max(dataset['data']))
        
        # Add 10% margin to the max value for better visualization
        if max_willpower_value > 0:
            willpower_chart['options']['scales']['y']['suggestedMax'] = int(max_willpower_value * 1.1) + 1
        
        return {
            'cardTypeChart': card_type_chart,
            'strengthChart': strength_chart,
            'willpowerChart': willpower_chart,
            'traitCalculations': trait_calculations,
            'traitInkCostDistributions': trait_ink_cost_distributions
        }
    
    def _build_card_data_from_api(self, card_name: str, api_card, ink_cost: int, 
                                  lorcana_type: str, copies_per_pack: float, 
                                  expected_at_table: float, slot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive card data dictionary using API card data as source of truth."""
        
        # Determine rarity from API card data if available, otherwise use default
        rarity = 'Common'  # Default
        if api_card.card_printings:
            # Use the rarity from the default printing
            rarity = api_card.default_printing.rarity if api_card.default_printing else api_card.card_printings[0].rarity
        
        card_data = {
            'name': card_name,
            'type': lorcana_type,
            'inkCost': ink_cost,
            'rarity': rarity.title(),
            'expectedAtTable': round(expected_at_table, 2),
            'copiesPerPack': round(copies_per_pack, 4),
            'slotInfo': {
                'name': slot_data['slot_name'],
                'weight': slot_data['weight'],
                'probability': round(slot_data['weight'] / self._get_slot_total_weight(slot_data['slot_name']), 4)
            },
            'traits': api_card.classifications or [],
            'strength': api_card.strength,
            'willpower': api_card.willpower
        }
        
        return card_data
    
    def _calculate_copies_per_pack(self, card_id: str, slot_data: Dict[str, Any]) -> float:
        """Calculate expected copies of this card per pack."""
        weight = slot_data['weight']
        slot_name = slot_data['slot_name']
        slot_count = slot_data['slot_count']
        
        # Calculate total weight for this slot to determine probability
        slot_total_weight = 0
        for other_card_id, other_slot_data in self.card_slot_data.items():
            if other_slot_data['slot_name'] == slot_name:
                slot_total_weight += other_slot_data['weight']
        
        # Calculate probability of this card appearing in one instance of this slot type
        card_probability = weight / slot_total_weight if slot_total_weight > 0 else 0
        
        # Calculate expected copies per pack (probability × slot count per pack)
        return card_probability * slot_count
    
    def _get_slot_total_weight(self, slot_name: str) -> int:
        """Get total weight for a specific slot."""
        return sum(
            slot_data['weight'] 
            for slot_data in self.card_slot_data.values() 
            if slot_data['slot_name'] == slot_name
        )
    
    def _update_distributions(self, api_card, ink_cost: int, 
                            strength_distribution: Dict, willpower_distribution: Dict) -> None:
        """Update strength and willpower distributions."""
        cost_key = str(ink_cost)
        
        # Build strength distribution (only for characters with strength)
        if api_card.strength is not None:
            strength_key = str(api_card.strength)
            if strength_key not in strength_distribution[cost_key]:
                strength_distribution[cost_key][strength_key] = 0
            strength_distribution[cost_key][strength_key] += 1
        
        # Build willpower distribution (for characters and locations with willpower)
        if api_card.willpower is not None:
            willpower_key = str(api_card.willpower)
            if willpower_key not in willpower_distribution[cost_key]:
                willpower_distribution[cost_key][willpower_key] = 0
            willpower_distribution[cost_key][willpower_key] += 1
    
    def _get_empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure for error cases."""
        return {
            'cards': [],
            'cardTypes': {},
            'traits': [],
            'strengthDistribution': {},
            'willpowerDistribution': {},
            'chartData': {
                'cardTypeChart': {'labels': [], 'data': []},
                'strengthChart': {'labels': [], 'datasets': []},
                'willpowerChart': {'labels': [], 'datasets': []},
                'traitCalculations': {},
                'traitInkCostDistributions': {}
            },
            'settings': {
                'boostersPerPlayer': 3,
                'name': 'Unknown Set',
                'withReplacement': True,
                'playersCount': 8,
                'totalPacks': 24
            }
        }
    
    def _get_strength_color(self, strength: str) -> str:
        """Generate color for strength values."""
        try:
            str_val = int(strength)
            # Use a red gradient for strength (low to high)
            if str_val <= 0:
                return 'rgb(100, 0, 0)'
            elif str_val <= 2:
                return f'rgb({100 + str_val * 30}, 0, 0)'
            elif str_val <= 4:
                return f'rgb({160 + (str_val - 2) * 30}, {(str_val - 2) * 20}, 0)'
            else:
                return f'rgb({220 + min(35, (str_val - 4) * 7)}, {40 + min(80, (str_val - 4) * 16)}, 0)'
        except ValueError:
            return 'rgb(128, 128, 128)'  # Gray for non-numeric values
    
    def _get_willpower_color(self, willpower: str) -> str:
        """Generate color for willpower values."""
        try:
            wp_val = int(willpower)
            # Use a blue-purple gradient for willpower (low to high)
            if wp_val <= 0:
                return 'rgb(0, 0, 100)'
            elif wp_val <= 2:
                return f'rgb(0, 0, {100 + wp_val * 30})'
            elif wp_val <= 4:
                return f'rgb({(wp_val - 2) * 20}, 0, {160 + (wp_val - 2) * 30})'
            else:
                return f'rgb({40 + min(80, (wp_val - 4) * 16)}, 0, {220 + min(35, (wp_val - 4) * 7)})'
        except ValueError:
            return 'rgb(128, 128, 128)'  # Gray for non-numeric values
