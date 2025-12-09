"""
AI Service for Cattle Classification
Generates trait scores based on uploaded images
"""
from app.models.trait_definitions import TRAIT_DEFINITIONS, get_all_traits_flat
from typing import List, Dict
import random
from datetime import datetime

class AIService:
    """
    AI Service for cattle trait evaluation
    """
    
    def __init__(self):
        """Initialize service"""
        self.traits = get_all_traits_flat()
        print("✓ AI Service initialized for trait evaluation")
    
    async def classify_animal(self, image_paths: List[str], animal_info: Dict) -> Dict:
        """
        Generate trait scores for cattle classification
        
        Args:
            image_paths: 5 image paths (rear, side, top, udder, side_udder)
            animal_info: Animal details dict
        
        Returns:
            Complete classification results with trait scores
        """
        print(f"✓ Processing classification for {len(image_paths)} images")
        return self._generate_mock_results(animal_info)

    def _calculate_milk_yield(self, traits: List[Dict], animal_info: Dict) -> Dict:
        """
        Calculate daily milk yield prediction from body measurements
        """
        measurements = {trait['trait']: trait.get('measurement', 0) for trait in traits}
        scores = {trait['trait']: trait['score'] for trait in traits}
        
        # Body measurements
        stature = measurements.get('Stature', 135)
        body_length = measurements.get('Body Length', 155)
        body_depth = measurements.get('Body Depth', 70)
        heart_girth = measurements.get('Heart Girth', 190)
        
        # Body capacity factor
        body_capacity = (stature * body_length * body_depth * heart_girth) / 1000000
        body_factor = 1 + (body_capacity - 140) / 100
        
        # Udder quality factor
        udder_traits = ['Fore Udder Attachment', 'Rear Udder Height', 'Central Ligament', 'Udder Depth']
        udder_scores = [scores.get(t, 5) for t in udder_traits]
        udder_factor = sum(udder_scores) / (len(udder_scores) * 9)
        
        # Udder measurements
        rear_udder_width = measurements.get('Rear udder width', 25)
        udder_width_factor = 1 + (rear_udder_width - 25) / 50
        
        # Body condition
        bcs = scores.get('Body condition score', 5)
        bcs_factor = 0.9 + (bcs - 5) * 0.02
        
        # Lactation factor
        lactation = animal_info.get('lactationNumber', 1)
        lactation_factor = {1: 0.85, 2: 0.95, 3: 1.0, 4: 1.0}.get(lactation, 0.90)
        
        # Breed base yield
        breed = animal_info.get('breed', '').lower()
        if any(b in breed for b in ['holstein', 'hf', 'friesian']):
            breed_base = 25
        elif 'jersey' in breed:
            breed_base = 20
        elif any(b in breed for b in ['gir', 'sahiwal', 'red sindhi']):
            breed_base = 12
        elif any(b in breed for b in ['murrah', 'mehsana', 'surti']):
            breed_base = 10
        else:
            breed_base = 15
        
        # Calculate yield
        daily_yield = breed_base * body_factor * udder_factor * udder_width_factor * bcs_factor * lactation_factor
        daily_yield = round(daily_yield, 1)
        
        return {
            "dailyYield": daily_yield,
            "minYield": round(daily_yield * 0.85, 1),
            "maxYield": round(daily_yield * 1.15, 1),
            "unit": "liters/day",
            "lactationYield": round(daily_yield * 305, 0),
            "lactationUnit": "liters/305 days",
            "confidence": 85
        }
    
    def _generate_mock_results(self, animal_info: Dict) -> Dict:
        """Generate realistic mock data following official format"""
        
        sections = {}
        
        for category, traits in TRAIT_DEFINITIONS.items():
            section_traits = []
            for trait in traits:
                score = random.randint(5, 8)
                measurement = None
                
                # Add realistic measurements
                if trait['measurement_unit'] == 'cm':
                    if 'Stature' in trait['name']:
                        measurement = random.randint(130, 145)
                    elif 'Girth' in trait['name']:
                        measurement = random.randint(180, 200)
                    elif 'Length' in trait['name']:
                        measurement = random.randint(145, 165)
                    elif 'Depth' in trait['name']:
                        measurement = random.randint(65, 80)
                    elif 'Width' in trait['name']:
                        measurement = random.randint(20, 50)
                    elif 'Height' in trait['name']:
                        measurement = random.randint(15, 25)
                    elif 'Teat' in trait['name']:
                        measurement = round(random.uniform(2, 8), 1)
                    else:
                        measurement = random.randint(10, 40)
                elif trait['measurement_unit'] == 'degrees':
                    measurement = random.randint(25, 50)
                
                section_traits.append({
                    "trait": trait['name'],
                    "score": score,
                    "measurement": measurement
                })
            
            sections[category] = section_traits
        
        # Calculate overall
        all_scores = []
        all_traits_list = []
        for traits in sections.values():
            all_scores.extend([t['score'] for t in traits])
            all_traits_list.extend(traits)
        
        overall = round(sum(all_scores) / len(all_scores), 1)
        
        # Calculate milk yield prediction
        milk_yield = self._calculate_milk_yield(all_traits_list, animal_info)
        
        return {
            "animalInfo": animal_info,
            "officialFormat": {
                "villageName": animal_info.get('village', ''),
                "farmerName": animal_info.get('farmerName', ''),
                "animalTagNo": animal_info['tagNumber'],
                "dateOfBirth": animal_info['dateOfBirth'],
                "lactationNo": animal_info['lactationNumber'],
                "dateOfCalving": animal_info['dateOfCalving'],
                "classificationDate": datetime.now().strftime("%Y-%m-%d"),
                "classifiedBy": "AI System (Mock Data)",
                "sections": sections
            },
            "categoryScores": {
                cat: round(sum(t['score'] for t in traits) / len(traits), 1)
                for cat, traits in sections.items()
            },
            "overallScore": overall,
            "grade": "Good" if overall >= 6 else "Fair",
            "totalTraits": 20,
            "confidenceLevel": 88,
            "milkYieldPrediction": milk_yield
        }

# Singleton
ai_service = AIService()
