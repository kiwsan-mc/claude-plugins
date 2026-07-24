#!/usr/bin/env python3
"""
MCG Sales Agent - Server-Side Wrapper
Integrates with mcg-toolbox plugin to auto-trigger skills
Place in: /var/folders/.../mcg-sales-agent/mcg_sales_agent_wrapper_server.py
"""

import re
import logging
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SkillTrigger:
    """Represents a skill to trigger"""
    name: str
    pattern_name: str
    confidence: float


class MCGSalesAgentWrapper:
    """
    Server-side wrapper for MCG Sales Agent
    Auto-detects query patterns and triggers skills
    """

    def __init__(self, skill_executor: Optional[Callable] = None):
        """
        Initialize wrapper

        Args:
            skill_executor: Function to execute skills (optional)
                          Should accept list of SkillTrigger objects
                          Returns dict of skill results
        """
        self.skill_executor = skill_executor
        self.debug = False
        self.enabled = True
        self.min_confidence = 0.5

        # Pattern functions
        self.patterns = {
            "sales-dashboard": self._pattern_dashboard,
            "abc-analysis": self._pattern_abc,
            "channel-regional": self._pattern_channel,
            "discount-margin": self._pattern_discount,
            "member-analysis": self._pattern_member,
            "sales-sqm": self._pattern_sqm,
        }

    def detect_skills(self, query: str) -> List[SkillTrigger]:
        """Detect which skills to trigger based on query"""
        if not self.enabled or not query:
            return []

        query_normalized = self._normalize_query(query)
        detected = []

        for skill_name, pattern_func in self.patterns.items():
            try:
                confidence = pattern_func(query_normalized)
                if confidence > self.min_confidence:
                    detected.append(SkillTrigger(
                        name=skill_name,
                        pattern_name=skill_name.replace("-", "_"),
                        confidence=confidence
                    ))
            except Exception as e:
                if self.debug:
                    logger.error(f"Error in pattern {skill_name}: {e}")

        # Sort by confidence
        detected.sort(key=lambda x: x.confidence, reverse=True)

        if self.debug and detected:
            logger.info(f"Detected skills: {[s.name for s in detected]}")

        return detected

    def enrich_results(
        self,
        query: str,
        query_results: Any,
        skills: List[SkillTrigger]
    ) -> Dict[str, Any]:
        """
        Enrich query results with skill insights

        Args:
            query: Original SQL query
            query_results: Results from execute_sql()
            skills: List of detected skills

        Returns:
            Enriched result dict
        """
        enriched = {
            "query": query,
            "results": query_results,
            "auto_triggered_skills": [s.name for s in skills],
            "skill_confidence": [
                {"skill": s.name, "confidence": f"{s.confidence:.1%}"}
                for s in skills
            ],
            "timestamp": datetime.now().isoformat()
        }

        # Execute skills if executor provided
        if self.skill_executor and skills:
            try:
                if self.debug:
                    logger.info(f"Executing {len(skills)} skill(s)")

                skill_results = self.skill_executor(skills)
                enriched["skill_results"] = skill_results
                enriched["enriched"] = True

            except Exception as e:
                logger.error(f"Skill execution error: {e}")
                enriched["skill_error"] = str(e)
                enriched["enriched"] = False

        return enriched

    # ========================================================================
    # PATTERN DETECTION FUNCTIONS
    # ========================================================================

    def _pattern_dashboard(self, query: str) -> float:
        """Sales Dashboard pattern: broad KPI aggregations"""
        score = 0.0

        agg_funcs = ["SUM(", "COUNT(", "AVG(", "MAX(", "MIN("]
        if any(func in query for func in agg_funcs):
            score += 0.3

        simple_groups = [
            "GROUP BY MAIN_CHANNEL",
            "GROUP BY FY_MONTH",
            "GROUP BY FY_QUARTER",
            "GROUP BY SOLD_DATE"
        ]
        if any(group in query for group in simple_groups):
            score += 0.3

        if "SOLD_DATE" in query and ">=" in query:
            score += 0.2

        if "TOTAL_EXC_VAT_PRICE" in query and "SUM(" in query:
            score += 0.1

        return min(score, 1.0)

    def _pattern_abc(self, query: str) -> float:
        """ABC Analysis pattern: product classification"""
        score = 0.0

        if "GROUP BY" in query and "CATEGORY" in query and "PRODUCT" in query:
            score += 0.4

        if "ORDER BY" in query and ("DESC" in query or "ASC" in query):
            score += 0.2

        if "SUM(" in query and "TOTAL_EXC_VAT_PRICE" in query:
            score += 0.2

        if "TOTAL_QUANTITY" in query:
            score += 0.1

        return min(score, 1.0)

    def _pattern_channel(self, query: str) -> float:
        """Channel & Regional pattern"""
        score = 0.0

        if "GROUP BY MAIN_CHANNEL" in query:
            score += 0.5

        regional_cols = ["REGIONAL", "PROVINCE", "REGIONAL_TEXT"]
        if "GROUP BY" in query and any(col in query for col in regional_cols):
            score += 0.5

        if "SUM(" in query and "TOTAL_EXC_VAT_PRICE" in query:
            score += 0.2

        return min(score, 1.0)

    def _pattern_discount(self, query: str) -> float:
        """Discount & Margin pattern"""
        score = 0.0

        discount_cols = ["TOTAL_DISCOUNT_AMOUNT", "PRICE_SIGN", "DISCOUNT"]
        if any(col in query for col in discount_cols):
            score += 0.3

        if "COGS" in query or "MARGIN" in query:
            score += 0.3

        if "GROUP BY" in query and "CATEGORY" in query:
            score += 0.2

        if "/" in query or "NULLIF" in query:
            score += 0.1

        return min(score, 1.0)

    def _pattern_member(self, query: str) -> float:
        """Member Analysis pattern"""
        score = 0.0

        if "GROUP BY" in query and "MEMBER_TYPE" in query:
            score += 0.5

        if "MEMBER_TYPE =" in query or "CHANNEL_STORE <> 'MARKETPLACE'" in query:
            score += 0.3

        if "MEMBER" in query:
            score += 0.2

        return min(score, 1.0)

    def _pattern_sqm(self, query: str) -> float:
        """Sales per Sqm pattern"""
        score = 0.0

        if "SQM" in query:
            score += 0.4

        store_cols = ["BRANCH_CODE", "NAME_3", "BRANCH"]
        if "GROUP BY" in query and any(col in query for col in store_cols):
            score += 0.3

        if "MAIN_CHANNEL = 'OFFLINE'" in query:
            score += 0.2

        if "PROVINCE_NAME" in query or "BRANCH_CODE" in query:
            score += 0.1

        return min(score, 1.0)

    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================

    def _normalize_query(self, query: str) -> str:
        """Normalize SQL for pattern matching"""
        query = " ".join(query.split())
        query = query.upper()
        return query

    def process_query(
        self,
        query: str,
        query_results: Any,
        enable_skills: bool = True
    ) -> Dict[str, Any]:
        """
        Process query results with skill enrichment

        Args:
            query: Original SQL query
            query_results: Results from execute_sql
            enable_skills: Whether to trigger skills (default True)

        Returns:
            Enriched results dict
        """
        if not enable_skills or not self.enabled:
            return {
                "query": query,
                "results": query_results,
                "enriched": False
            }

        try:
            # Detect skills
            skills = self.detect_skills(query)

            # Enrich results
            enriched = self.enrich_results(query, query_results, skills)

            return enriched

        except Exception as e:
            logger.error(f"Error in process_query: {e}")
            return {
                "query": query,
                "results": query_results,
                "error": str(e),
                "enriched": False
            }


# ============================================================================
# PLUGIN INTEGRATION FUNCTIONS
# ============================================================================

# Global wrapper instance
_wrapper_instance: Optional[MCGSalesAgentWrapper] = None


def initialize_wrapper(skill_executor: Optional[Callable] = None, debug: bool = False):
    """Initialize the wrapper for plugin use"""
    global _wrapper_instance
    _wrapper_instance = MCGSalesAgentWrapper(skill_executor=skill_executor)
    _wrapper_instance.debug = debug
    logger.info("MCG Sales Agent Wrapper initialized")


def enable_wrapper(enable: bool = True):
    """Enable/disable wrapper"""
    if _wrapper_instance:
        _wrapper_instance.enabled = enable
        logger.info(f"Wrapper {'enabled' if enable else 'disabled'}")


def process_execute_sql_result(
    query: str,
    result: Any,
    enable_skills: bool = True
) -> Any:
    """
    Wrapper function to enrich execute_sql results
    Call this after execute_sql to add skill insights

    Usage:
        result = execute_sql(query)
        enriched = process_execute_sql_result(query, result)
    """
    if not _wrapper_instance:
        return result

    return _wrapper_instance.process_query(query, result, enable_skills)


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example 1: Create wrapper
    wrapper = MCGSalesAgentWrapper()
    wrapper.debug = True

    # Example 2: Detect skills
    query1 = """
    SELECT TOP 10 category, product, SUM(total_exc_vat_price) as sales
    FROM [dbo].[mcg_aiplatform_sales]
    GROUP BY category, product
    ORDER BY SUM(total_exc_vat_price) DESC
    """

    skills = wrapper.detect_skills(query1)
    print(f"Detected skills: {[s.name for s in skills]}")
    # Output: ['abc-analysis']

    # Example 3: Process results
    mock_results = [
        {"category": "JEANS", "product": "JEANS", "sales": 57514916.99},
        {"category": "TOP", "product": "T SHIRT", "sales": 45724341.08}
    ]

    enriched = wrapper.process_query(query1, mock_results, enable_skills=False)
    print(f"\nEnriched result keys: {list(enriched.keys())}")
    # Output: ['query', 'results', 'auto_triggered_skills', ...]