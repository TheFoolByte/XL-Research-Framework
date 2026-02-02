"""
Advanced pattern analyzer for family codes

Migrated from xl-research/src/modules/analyzer.py
Adapted for integration with main framework.
"""
import re
import json
from collections import Counter
from typing import Dict, List, Optional, Tuple
import uuid as uuid_lib
from datetime import datetime
import random


class FamilyCodeAnalyzer:
    """Analyzes family codes for patterns and intelligence"""
    
    def __init__(self):
        # Patterns extracted from 300+ samples
        self.known_patterns = {
            # Prefix patterns
            "d0": {"category": "Biz/Bebas Puas", "confidence": 0.95, "count": 25},
            "5d": {"category": "Conference/Edukasi", "confidence": 0.90, "count": 8},
            "e3": {"category": "Event/Pilkada", "confidence": 0.85, "count": 3},
            "7f": {"category": "XL PASS", "confidence": 0.80, "count": 2},
            "6a": {"category": "Streaming/Vidio", "confidence": 0.75, "count": 4},
            "2f": {"category": "Social Media", "confidence": 0.70, "count": 5},
            "08": {"category": "Unlimited Turbo", "confidence": 0.85, "count": 3},
            "ad": {"category": "Xtra Combo Mini", "confidence": 0.90, "count": 10},
            "3c": {"category": "Xtra Combo Flex", "confidence": 0.80, "count": 6},
            "3a": {"category": "Xtra Combo Flex LENGKAP", "confidence": 0.75, "count": 3},
            "4a": {"category": "Xcs Flex Ori", "confidence": 0.70, "count": 2},
            "6e": {"category": "Akrab", "confidence": 0.95, "count": 15},
            "f4": {"category": "Akrab Full", "confidence": 0.80, "count": 5},
            "54": {"category": "Booster Akrab", "confidence": 0.75, "count": 3},
            "48": {"category": "Akrab 2KB", "confidence": 0.70, "count": 4},
            "80": {"category": "Bonus/Addon", "confidence": 0.65, "count": 8},
            "58": {"category": "Addon XCP 2GB", "confidence": 0.60, "count": 2},
            "45": {"category": "Addon XCP 15GB", "confidence": 0.60, "count": 2},
            "76": {"category": "Addon XCP 10GB", "confidence": 0.55, "count": 1},
            "31": {"category": "Family Hide/Unlimited", "confidence": 0.85, "count": 3},
            "20": {"category": "Biz Starter", "confidence": 0.75, "count": 4},
            "53": {"category": "Biz Data+", "confidence": 0.70, "count": 3},
            "fc": {"category": "EduCoference", "confidence": 0.65, "count": 2},
            "1f": {"category": "YouTube Bonus", "confidence": 0.60, "count": 3},
            "96": {"category": "Paket Harian", "confidence": 0.55, "count": 2},
            "8b": {"category": "Bonus Kuota", "confidence": 0.50, "count": 1},
            "fd": {"category": "Xtra Combo Lite", "confidence": 0.45, "count": 2},
            "00": {"category": "Bonus Aktivasi", "confidence": 0.40, "count": 2},
            "23": {"category": "XCP VIP/PRIO", "confidence": 0.85, "count": 10},
            "9f": {"category": "myPRIO DEAL", "confidence": 0.75, "count": 3},
            "25": {"category": "myPRIO DEAL Unlimited", "confidence": 0.70, "count": 1},
            "19": {"category": "myPRIO X Unlimited", "confidence": 0.65, "count": 2},
            "3f": {"category": "PRIO Ultima", "confidence": 0.60, "count": 1},
            "28": {"category": "PRIO Diamond", "confidence": 0.55, "count": 1},
            "1d": {"category": "PRIO Platinum", "confidence": 0.50, "count": 1},
            "ed": {"category": "PRIO Gold", "confidence": 0.45, "count": 1},
            "e5": {"category": "PRIO Silver", "confidence": 0.40, "count": 1},
            "70": {"category": "Platinum Mobile", "confidence": 0.35, "count": 1},
            "b7": {"category": "Vidio", "confidence": 0.30, "count": 1},
            "9e": {"category": "Call & SMS/Apps Quota", "confidence": 0.25, "count": 3},
            "8f": {"category": "PRIO Booster", "confidence": 0.20, "count": 3},
            "39": {"category": "VIU", "confidence": 0.15, "count": 1},
            "73": {"category": "Umrah & Hajj", "confidence": 0.05, "count": 2},
        }
        
        # Known family codes database (from your data)
        self.known_codes = {}
        self._load_known_codes()
    
    def _load_known_codes(self):
        """Load known family codes from internal database"""
        # This would be loaded from data/family_codes.json
        # For now, we'll create a sample
        self.known_codes = {
            "d004d498-e8a8-4e22-b8b1-b71b7652b409": {
                "name": "BIZ Prime - NEW",
                "price": 90000,
                "category": "BIZ",
                "type": "Postpaid"
            },
            "d0a349a7-0b3a-4552-bc1d-3fd9ac0a17ee": {
                "name": "Bebas Puas",
                "price": 50000,
                "category": "General",
                "type": "Prepaid"
            },
            # Add more from your 300+ list
        }
    
    def analyze_code(self, family_code: str) -> Dict:
        """
        Analyze a family code for patterns and intelligence
        """
        if not self._is_valid_uuid(family_code):
            return {"error": "Invalid UUID format"}
        
        result = {
            "family_code": family_code,
            "analysis": {},
            "patterns": [],
            "predictions": []
        }
        
        # Clean UUID for analysis
        clean_code = family_code.replace('-', '')
        
        # 1. Check if known code
        if family_code in self.known_codes:
            result["known"] = True
            result["info"] = self.known_codes[family_code]
        
        # 2. Analyze prefix (first 2 chars)
        prefix = clean_code[:2].lower()
        if prefix in self.known_patterns:
            pattern = self.known_patterns[prefix]
            result["patterns"].append({
                "type": "prefix",
                "value": prefix,
                "category": pattern["category"],
                "confidence": pattern["confidence"],
                "description": f"Matches {pattern['category']} pattern"
            })
        
        # 3. Analyze character distribution
        char_dist = Counter(clean_code)
        result["analysis"]["character_distribution"] = dict(char_dist)
        
        # 4. Check UUID version (position 13)
        uuid_version = clean_code[12]
        result["analysis"]["uuid_version"] = uuid_version
        if uuid_version == '4':
            result["patterns"].append({
                "type": "uuid_version",
                "value": "v4",
                "description": "Standard random UUID"
            })
        
        # 5. Check variant (position 17)
        uuid_variant = clean_code[16]
        valid_variants = ['8', '9', 'a', 'b']
        if uuid_variant in valid_variants:
            result["analysis"]["uuid_variant_valid"] = True
        else:
            result["analysis"]["uuid_variant_valid"] = False
            result["patterns"].append({
                "type": "warning",
                "value": f"Invalid variant: {uuid_variant}",
                "description": "UUID variant should be 8, 9, a, or b"
            })
        
        # 6. Generate predictions based on patterns
        predictions = self._generate_predictions(family_code, prefix)
        result["predictions"] = predictions
        
        # 7. Calculate overall confidence
        if result["patterns"]:
            confidences = [p.get("confidence", 0) for p in result["patterns"] if "confidence" in p]
            if confidences:
                result["analysis"]["overall_confidence"] = sum(confidences) / len(confidences)
        
        return result
    
    def _is_valid_uuid(self, uuid_str: str) -> bool:
        """Check if string is valid UUID"""
        try:
            uuid_obj = uuid_lib.UUID(uuid_str)
            return str(uuid_obj) == uuid_str
        except ValueError:
            return False
    
    def _generate_predictions(self, family_code: str, prefix: str) -> List[Dict]:
        """Generate predictions based on patterns"""
        predictions = []
        
        # Prediction based on prefix
        if prefix in self.known_patterns:
            pattern = self.known_patterns[prefix]
            predictions.append({
                "type": "category",
                "prediction": pattern["category"],
                "confidence": pattern["confidence"],
                "basis": f"Prefix pattern '{prefix}'"
            })
        
        # Prediction based on UUID structure
        clean_code = family_code.replace('-', '')
        
        # Check if looks sequential (low randomness)
        sequential_score = self._calculate_sequential_score(clean_code)
        if sequential_score > 0.7:
            predictions.append({
                "type": "generation_method",
                "prediction": "Sequential/Pattern-based generation",
                "confidence": 0.8,
                "basis": f"High sequential score: {sequential_score:.2f}"
            })
        
        # Check for common patterns in your data
        if prefix in ['d0', 'ad', '3c', '6e']:
            predictions.append({
                "type": "availability",
                "prediction": "Likely active/available",
                "confidence": 0.75,
                "basis": "Common active prefix in database"
            })
        
        return predictions
    
    def _calculate_sequential_score(self, code: str) -> float:
        """Calculate how sequential/non-random a code looks"""
        if len(code) < 4:
            return 0.0
        
        # Check for repeating characters
        repeats = sum(1 for i in range(len(code)-1) if code[i] == code[i+1])
        repeat_score = repeats / len(code)
        
        # Check for sequential numbers/letters
        sequential = 0
        for i in range(len(code)-2):
            if code[i:i+3].isdigit():
                nums = [int(c) for c in code[i:i+3]]
                if nums == list(range(nums[0], nums[0]+3)):
                    sequential += 1
        
        seq_score = sequential / (len(code) - 2) if len(code) > 2 else 0
        
        return max(repeat_score, seq_score)
    
    def analyze_batch(self, family_codes: List[str]) -> Dict:
        """Analyze multiple family codes"""
        results = {
            "total": len(family_codes),
            "valid": 0,
            "invalid": 0,
            "analyses": [],
            "statistics": {}
        }
        
        prefix_counter = Counter()
        category_counter = Counter()
        
        for code in family_codes:
            analysis = self.analyze_code(code)
            results["analyses"].append(analysis)
            
            if "error" not in analysis:
                results["valid"] += 1
                
                # Collect statistics
                clean_code = code.replace('-', '')
                prefix = clean_code[:2].lower()
                prefix_counter[prefix] += 1
                
                # Get predicted category
                if analysis.get("patterns"):
                    for pattern in analysis["patterns"]:
                        if pattern.get("type") == "prefix":
                            category = pattern.get("category", "Unknown")
                            category_counter[category] += 1
            else:
                results["invalid"] += 1
        
        # Add statistics
        results["statistics"]["prefix_distribution"] = dict(prefix_counter)
        results["statistics"]["category_distribution"] = dict(category_counter)
        
        # Most common prefixes
        if prefix_counter:
            results["statistics"]["top_prefixes"] = prefix_counter.most_common(10)
        
        return results
    
    def generate_smart_uuid(self, category: str = None) -> str:
        """
        Generate UUID with smart patterns based on category
        """
        if category:
            # Find prefix for category
            matching_prefixes = [
                prefix for prefix, info in self.known_patterns.items()
                if info["category"].lower() == category.lower()
            ]
            
            if matching_prefixes:
                # Use most common prefix for category
                prefix = matching_prefixes[0]
                # Generate rest of UUID
                rest = ''.join(random.choices('0123456789abcdef', k=30))
                uuid_str = f"{prefix}{rest}"
                
                # Format as UUID v4
                uuid_str = f"{uuid_str[:8]}-{uuid_str[8:12]}-4{uuid_str[13:16]}-{random.choice(['8','9','a','b'])}{uuid_str[17:20]}-{uuid_str[20:32]}"
                
                # Validate
                try:
                    uuid_obj = uuid_lib.UUID(uuid_str)
                    return str(uuid_obj)
                except ValueError:
                    pass
        
        # Fallback to random UUID
        return str(uuid_lib.uuid4())
