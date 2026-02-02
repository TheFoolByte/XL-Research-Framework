"""
Smart family code enumerator with ML patterns

Migrated from xl-research/src/modules/enumerator.py
Adapted for integration with main framework.
"""
import uuid
import random
import time
from typing import List, Dict, Optional, Generator, Tuple
from datetime import datetime
import statistics

from ..client import XLResearchClient
from .analyzer import FamilyCodeAnalyzer

# Use framework logger if available, fallback to basic
try:
    from core.logger import log as logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SmartFamilyCodeEnumerator:
    """Smart enumeration with adaptive learning for family code discovery"""
    
    def __init__(self, client: XLResearchClient):
        self.client = client
        self.analyzer = FamilyCodeAnalyzer()
        self.found_codes = []
        self.attempts = 0
        self.success_rate = 0.0
        
        # Smart patterns from 300+ samples (weighted by frequency)
        self.smart_patterns = [
            ('d0', 0.25),      # Biz/Bebas Puas - Very common
            ('ad', 0.15),      # Xtra Combo Mini
            ('6e', 0.12),      # Akrab
            ('3c', 0.10),      # Xtra Combo Flex
            ('23', 0.08),      # XCP VIP/PRIO
            ('5d', 0.07),      # Conference/Edukasi
            ('08', 0.05),      # Unlimited Turbo
            ('2f', 0.04),      # Social Media
            ('80', 0.03),      # Bonus/Addon
            ('20', 0.03),      # Biz Starter
            ('53', 0.02),      # Biz Data+
            ('fc', 0.02),      # EduCoference
            ('1f', 0.01),      # YouTube Bonus
            ('96', 0.01),      # Paket Harian
            ('8b', 0.01),      # Bonus Kuota
        ]
        
        # Response time analysis
        self.response_times = []
        self.avg_response_time = 1.0
        
        # Adaptive learning
        self.successful_prefixes = {}
        self.failed_prefixes = {}
        
    def generate_smart_uuid(self, use_smart: bool = True, 
                           preferred_category: str = None) -> str:
        """
        Generate UUID with intelligence
        """
        if preferred_category:
            # Try to generate based on category
            smart_uuid = self.analyzer.generate_smart_uuid(preferred_category)
            if smart_uuid:
                return smart_uuid
        
        if use_smart and random.random() < 0.8:  # 80% use smart patterns
            # Weighted random choice
            patterns, weights = zip(*self.smart_patterns)
            prefix = random.choices(patterns, weights=weights)[0]
            
            # Generate with pattern
            hex_chars = '0123456789abcdef'
            random_part = ''.join(random.choices(hex_chars, k=30))
            
            # UUID v4 format with pattern
            uuid_str = f"{prefix}{random_part}"
            
            # Ensure valid UUID v4 format
            # Positions: 13 = '4', 17 ∈ ['8','9','a','b']
            uuid_str = (
                f"{uuid_str[:8]}-"
                f"{uuid_str[8:12]}-"
                f"4{uuid_str[13:16]}-"
                f"{random.choice(['8','9','a','b'])}{uuid_str[17:20]}-"
                f"{uuid_str[20:32]}"
            )
            
            try:
                uuid_obj = uuid.UUID(uuid_str)
                return str(uuid_obj)
            except ValueError:
                # Fallback to random
                pass
        
        # Random UUID v4
        return str(uuid.uuid4())
    
    def test_uuid(self, family_code: str) -> Tuple[bool, Optional[Dict]]:
        """
        Test if a UUID is valid and returns package details
        """
        start_time = time.time()
        
        try:
            result = self.client.get_package_detail(family_code)
            response_time = time.time() - start_time
            
            # Record response time
            self.response_times.append(response_time)
            if len(self.response_times) > 100:
                self.response_times.pop(0)
            self.avg_response_time = statistics.mean(self.response_times) if self.response_times else 1.0
            
            if result and 'error' not in result:
                # Record successful prefix
                prefix = family_code.replace('-', '')[:2].lower()
                self.successful_prefixes[prefix] = self.successful_prefixes.get(prefix, 0) + 1
                
                # Analyze the code
                analysis = self.analyzer.analyze_code(family_code)
                
                return True, {
                    'family_code': family_code,
                    'data': result,
                    'response_time': response_time,
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Record failed prefix
                prefix = family_code.replace('-', '')[:2].lower()
                self.failed_prefixes[prefix] = self.failed_prefixes.get(prefix, 0) + 1
                
                return False, None
                
        except Exception as e:
            if hasattr(logger, 'error'):
                logger.error(f"Error testing UUID {family_code}: {str(e)}")
            return False, None
    
    def enumerate(self, max_attempts: int = 100,
                 use_adaptive: bool = True,
                 target_categories: List[str] = None) -> Generator[Dict, None, None]:
        """
        Smart enumeration with adaptive learning
        """
        self.attempts = 0
        found_count = 0
        
        while self.attempts < max_attempts:
            self.attempts += 1
            
            # Adaptive pattern adjustment
            if use_adaptive and self.attempts % 10 == 0:
                self._adjust_patterns()
            
            # Choose category if specified
            category = None
            if target_categories:
                category = random.choice(target_categories)
            
            # Generate UUID
            test_uuid = self.generate_smart_uuid(
                use_smart=True,
                preferred_category=category
            )
            
            # Test the UUID
            success, result = self.test_uuid(test_uuid)
            
            if success and result:
                found_count += 1
                self.found_codes.append(result)
                
                # Update success rate
                self.success_rate = found_count / self.attempts
                
                yield result
            
            # Adaptive delay
            delay = self._calculate_adaptive_delay()
            if delay > 0:
                time.sleep(delay)
    
    def _adjust_patterns(self):
        """Adjust pattern weights based on success/failure"""
        if not self.successful_prefixes:
            return
        
        total_success = sum(self.successful_prefixes.values())
        total_failure = sum(self.failed_prefixes.values()) if self.failed_prefixes else 1
        
        # Calculate success ratios
        success_ratios = {}
        for prefix in set(list(self.successful_prefixes.keys()) + list(self.failed_prefixes.keys())):
            success = self.successful_prefixes.get(prefix, 0)
            failure = self.failed_prefixes.get(prefix, 0)
            total = success + failure
            if total > 0:
                success_ratios[prefix] = success / total
        
        # Update pattern weights
        new_patterns = []
        for prefix, weight in self.smart_patterns:
            if prefix in success_ratios:
                # Increase weight for successful prefixes
                new_weight = weight * (1 + success_ratios[prefix])
                new_patterns.append((prefix, new_weight))
            else:
                # Keep original weight
                new_patterns.append((prefix, weight))
        
        # Normalize weights
        total_weight = sum(w for _, w in new_patterns)
        self.smart_patterns = [(p, w/total_weight) for p, w in new_patterns]
    
    def _calculate_adaptive_delay(self) -> float:
        """Calculate delay based on response time and success rate"""
        base_delay = self.avg_response_time * 1.5
        
        # Adjust based on success rate
        if self.success_rate > 0.1:  # High success rate
            delay_factor = 0.5
        elif self.success_rate > 0.01:  # Moderate success rate
            delay_factor = 1.0
        else:  # Low success rate
            delay_factor = 2.0
        
        # Add randomness
        random_factor = random.uniform(0.8, 1.2)
        
        delay = base_delay * delay_factor * random_factor
        
        # Clamp between 0.5 and 5 seconds
        return max(0.5, min(delay, 5.0))
    
    def bulk_enumerate(self, max_attempts: int = 100,
                      concurrency: int = 1) -> List[Dict]:
        """
        Bulk enumeration (single-threaded for now)
        """
        found = []
        for result in self.enumerate(max_attempts):
            found.append(result)
        return found
    
    def targeted_enumeration(self, prefixes: List[str],
                           max_per_prefix: int = 20) -> List[Dict]:
        """
        Enumerate specific prefixes
        """
        found = []
        
        for prefix in prefixes:
            for _ in range(max_per_prefix):
                # Generate UUID with specific prefix
                hex_chars = '0123456789abcdef'
                random_part = ''.join(random.choices(hex_chars, k=30))
                uuid_str = f"{prefix}{random_part}"
                uuid_str = f"{uuid_str[:8]}-{uuid_str[8:12]}-4{uuid_str[13:16]}-{random.choice(['8','9','a','b'])}{uuid_str[17:20]}-{uuid_str[20:32]}"
                
                try:
                    uuid_obj = uuid.UUID(uuid_str)
                    test_uuid = str(uuid_obj)
                    
                    success, result = self.test_uuid(test_uuid)
                    if success:
                        found.append(result)
                
                except ValueError:
                    continue
                
                time.sleep(random.uniform(1.0, 2.0))
        
        return found
    
    def get_statistics(self) -> Dict:
        """Get enumeration statistics"""
        return {
            "total_attempts": self.attempts,
            "found_count": len(self.found_codes),
            "success_rate": self.success_rate,
            "avg_response_time": self.avg_response_time,
            "successful_prefixes": dict(self.successful_prefixes),
            "failed_prefixes": dict(self.failed_prefixes),
            "current_patterns": self.smart_patterns
        }
