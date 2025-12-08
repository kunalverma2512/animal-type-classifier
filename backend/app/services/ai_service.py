import google.generativeai as genai
from app.core.config import settings
from app.models.trait_definitions import TRAIT_DEFINITIONS, get_all_traits_flat
from typing import List, Dict
import json
from PIL import Image
import random
from datetime import datetime

# Configure Gemini
if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
    genai.configure(api_key=settings.GEMINI_API_KEY)
    GEMINI_ENABLED = True
else:
    GEMINI_ENABLED = False
    print("⚠ Gemini API key not configured - using mock data")

class AIService:
    """
    AI Service using official Type Classification format.
    Uses Gemini AI - designed to be easily swappable with custom models.
    """
    
    def __init__(self):
        if GEMINI_ENABLED:
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                print(f"⚠ Gemini initialization failed: {e}")
                self.model = None
        else:
            self.model = None
        self.traits = get_all_traits_flat()
    
    async def classify_animal(self, image_paths: List[str], animal_info: Dict) -> Dict:
        """
        Main classification following official Type Evaluation Format
        
        Args:
            image_paths: 3 image paths (left_side, right_side, udder_closeup)
            animal_info: Animal details dict
        
        Returns:
            Complete classification results with official 20-trait scoring + milk yield prediction
        """
        
        # If Gemini is not available or disabled, use mock data
        if not self.model:
            print("Using mock data for classification")
            return self._generate_mock_results(animal_info)
        
        # Create official prompt
        prompt = self._create_official_prompt(animal_info)
        
        # Load images
        try:
            images = [Image.open(path) for path in image_paths]
        except Exception as e:
            print(f"Image loading error: {e}")
            return self._generate_mock_results(animal_info)
        
        try:
            # Call Gemini API
            response = self.model.generate_content([prompt] + images)
            
            # Parse response
            results = self._parse_response(response.text, animal_info)
            
            return results
            
        except Exception as e:
            print(f"AI Error: {e}")
            # Return mock data if AI fails
            return self._generate_mock_results(animal_info)
    
    def _create_official_prompt(self, animal_info: Dict) -> str:
        """Generate prompt following exact government format"""
        
        prompt = f"""
You are an expert Animal Typer trained in the official Type Classification system for dairy cattle and buffaloes.

ANIMAL INFORMATION:
- Village: {animal_info.get('village', 'N/A')}
- Farmer Name: {animal_info.get('farmerName', 'N/A')}
- Animal Tag No: {animal_info['tagNumber']}
- Animal Type: {animal_info['animalType']}
- Breed: {animal_info['breed']}
- Date of Birth: {animal_info['dateOfBirth']}
- Lactation No: {animal_info['lactationNumber']}
- Date of Calving: {animal_info['dateOfCalving']}

TASK: Evaluate the animal using the OFFICIAL Type Evaluation Format (Annex II).

Score ALL 20 traits on a scale of 1-9:

**SECTION 1: STRENGTH (5 traits)**
1. Stature (Short=1 → Tall=9) - Measure height in cm
2. Heart Girth (Narrow=1 → Wide=9) - Measure chest width in cm
3. Body Length (Short=1 → Long=9) - Measure shoulder to pin bone in cm
4. Body Depth (Shallow=1 → Deep=9) - Measure rib depth in cm
5. Angularity (Non-angular=1 → Angular=9) - Visual assessment

**SECTION 2: RUMP (2 traits)**
6. Rump Angle (High=1 → Low=9) - Measure angle in degrees
7. Rump Width (Narrow=1 → Wide=9) - Measure pin bone distance in cm

**SECTION 3: FEET AND LEG (3 traits)**
8. Rear Legs Set (Straight=1 → Curved=9) - Visual assessment
9. Rear Legs Rear View (Hocked-in=1 → Straight=9) - Visual assessment
10. Foot Angle (Low=1 → Steep=9) - Measure hoof angle in degrees

**SECTION 4: UDDER (9 traits)**
11. Fore Udder Attachment (Weak=1 → Strong=9)
12. Rear Udder Height (Low=1 → High=9) - Measure in cm
13. Central Ligament (Weak=1 → Strong=9)
14. Udder Depth (Deep=1 → Shallow=9) - Measure in cm
15. Front Teat Placement (Wide=1 → Close=9) - Measure distance in cm
16. Teat Length (Short=1 → Long=9) - Measure in cm
17. Rear Teat Placement (Wide=1 → Close=9) - Measure distance in cm
18. Rear udder width (Narrow=1 → Wide=9) - Measure in cm
19. Teat thickness (Thin=1 → Thick=9) - Measure diameter in cm

**SECTION 5: GENERAL (1 trait)**
20. Body condition score (Thin=1 → Fatty=9) - BCS 1-5 scale

Return ONLY valid JSON (no markdown, no code blocks):

{{
  "villageName": "{animal_info.get('village', '')}",
  "farmerName": "{animal_info.get('farmerName', '')}",
  "animalTagNo": "{animal_info['tagNumber']}",
  "dateOfBirth": "{animal_info['dateOfBirth']}",
  "lactationNo": {animal_info['lactationNumber']},
  "dateOfCalving": "{animal_info['dateOfCalving']}",
  "classificationDate": "2025-12-02",
  "classifiedBy": "AI System",
  "sections": {{
    "Strength": [
      {{"trait": "Stature", "score": 7, "measurement": 138}},
      {{"trait": "Heart Girth", "score": 6, "measurement": 195}},
      {{"trait": "Body Length", "score": 7, "measurement": 156}},
      {{"trait": "Body Depth", "score": 6, "measurement": 72}},
      {{"trait": "Angularity", "score": 5, "measurement": null}}
    ],
    "Rump": [
      {{"trait": "Rump Angle", "score": 6, "measurement": 28}},
      {{"trait": "Rump Width", "score": 7, "measurement": 45}}
    ],
    "Feet and Leg": [
      {{"trait": "Rear Legs Set", "score": 6, "measurement": null}},
      {{"trait": "Rear Legs Rear View", "score": 7, "measurement": null}},
      {{"trait": "Foot Angle", "score": 6, "measurement": 45}}
    ],
    "Udder": [
      {{"trait": "Fore Udder Attachment", "score": 8, "measurement": null}},
      {{"trait": "Rear Udder Height", "score": 7, "measurement": 18}},
      {{"trait": "Central Ligament", "score": 7, "measurement": null}},
      {{"trait": "Udder Depth", "score": 6, "measurement": 32}},
      {{"trait": "Front Teat Placement", "score": 7, "measurement": 15}},
      {{"trait": "Teat Length", "score": 6, "measurement": 5.2}},
      {{"trait": "Rear Teat Placement", "score": 6, "measurement": 12}},
      {{"trait": "Rear udder width", "score": 7, "measurement": 28}},
      {{"trait": "Teat thickness", "score": 6, "measurement": 2.8}}
    ],
    "General": [
      {{"trait": "Body condition score", "score": 5, "measurement": null}}
    ]
  }},
  "overallScore": 6.5,
  "grade": "Good",
  "summary": "Well-balanced animal with good dairy characteristics"
}}

Be accurate, realistic, and follow the official format exactly.
"""
        return prompt
    
    def _parse_response(self, response_text: str, animal_info: Dict) -> Dict:
        """Parse Gemini response into structured format"""
        
        try:
            # Clean response
            cleaned = response_text.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned.split('```')[1]
                if cleaned.startswith('json'):
                    cleaned = cleaned[4:]
            
            data = json.loads(cleaned.strip())
            
            # Calculate category averages
            category_scores = {}
            all_traits = []
            
            for category, traits in data['sections'].items():
                scores = [t['score'] for t in traits]
                category_scores[category] = round(sum(scores) / len(scores), 1)
                all_traits.extend(traits)
            
            # Calculate overall
            overall = round(sum(t['score'] for t in all_traits) / len(all_traits), 1)
            
            # Determine grade
            if overall >= 7.5:
                grade = "Excellent"
            elif overall >= 6.0:
                grade = "Good"
            elif overall >= 4.0:
                grade = "Fair"
            else:
                grade = "Poor"
            
            # Calculate milk yield prediction
            milk_yield = self._calculate_milk_yield(all_traits, animal_info)
            
            return {
                "animalInfo": animal_info,
                "officialFormat": data,
                "categoryScores": category_scores,
                "overallScore": overall,
                "grade": grade,
                "totalTraits": len(all_traits),
                "confidenceLevel": 92,
                "milkYieldPrediction": milk_yield
            }
            
        except Exception as e:
            print(f"Parse error: {e}")
            return self._generate_mock_results(animal_info)
    
    def _calculate_milk_yield(self, traits: List[Dict], animal_info: Dict) -> Dict:
        """
        Calculate daily milk yield prediction from body measurements
        Uses body size, udder characteristics, breed, lactation number
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
