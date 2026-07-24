#!/usr/bin/env python3
"""
MCG Toolbox Plugin Integration Hook
Hook this into your plugin's __init__.py or main entry point

Location: /var/folders/.../mcg-sales-agent/plugin_integration_hook.py
"""

import logging
from typing import Any, Callable, List, Dict, Optional
from mcg_sales_agent_wrapper_server import (
    MCGSalesAgentWrapper,
    initialize_wrapper,
    enable_wrapper,
    process_execute_sql_result
)

logger = logging.getLogger(__name__)


class MCGToolboxIntegration:
    """
    Integration wrapper for mcg-toolbox plugin
    Patches execute_sql to auto-trigger skills
    """

    def __init__(self, original_execute_sql: Callable):
        """
        Initialize integration

        Args:
            original_execute_sql: Original execute_sql function from mcg-toolbox
        """
        self.original_execute_sql = original_execute_sql
        self.wrapper = None
        self.skill_executor = None

    def set_skill_executor(self, executor: Callable):
        """Set the skill executor function"""
        self.skill_executor = executor
        if self.wrapper:
            self.wrapper.skill_executor = executor

    def initialize(self, debug: bool = False):
        """Initialize wrapper and integration"""
        initialize_wrapper(skill_executor=self.skill_executor, debug=debug)
        self.wrapper = MCGSalesAgentWrapper(skill_executor=self.skill_executor)
        self.wrapper.debug = debug
        logger.info("MCG Toolbox Integration initialized")

    def execute_sql_wrapper(self, query: str, **kwargs) -> Any:
        """
        Wrapped execute_sql that auto-triggers skills

        Usage:
            mcg_toolbox.execute_sql = integration.execute_sql_wrapper
        """
        try:
            # Execute original query
            result = self.original_execute_sql(query, **kwargs)

            # Process through wrapper
            if self.wrapper:
                enriched = self.wrapper.process_query(query, result)
                return enriched
            else:
                return result

        except Exception as e:
            logger.error(f"Error in execute_sql_wrapper: {e}")
            # Fallback to original on error
            return self.original_execute_sql(query, **kwargs)


# ============================================================================
# INSTALLATION INSTRUCTIONS
# ============================================================================

"""
HOW TO INTEGRATE WITH MCG-TOOLBOX PLUGIN
==========================================

1. Copy these files to your plugin directory:
   - mcg_sales_agent_wrapper_server.py
   - plugin_integration_hook.py

2. In your plugin's __init__.py or main entry point:

   from plugin_integration_hook import MCGToolboxIntegration

   # Get the original execute_sql function
   original_execute_sql = mcg_toolbox.execute_sql

   # Create integration wrapper
   integration = MCGToolboxIntegration(original_execute_sql)

   # Initialize
   integration.initialize(debug=True)

   # Set skill executor (optional, if you have one)
   def run_skills(detected_skills):
       # Your skill execution logic here
       results = {}
       for skill in detected_skills:
           results[skill.name] = invoke_skill(skill.name)
       return results

   integration.set_skill_executor(run_skills)

   # Patch execute_sql
   mcg_toolbox.execute_sql = integration.execute_sql_wrapper

3. That's it! Now all execute_sql calls will auto-trigger skills.

CONFIGURATION
=============

Enable/disable wrapper at runtime:
   enable_wrapper(True)   # Enable
   enable_wrapper(False)  # Disable

Set debug mode:
   wrapper.debug = True

Set confidence threshold:
   wrapper.min_confidence = 0.6  # Default 0.5

EXAMPLE USAGE
=============

# In your application code (unchanged):
result = mcg_toolbox.execute_sql("SELECT category, SUM(sales) FROM sales GROUP BY category")

# The wrapper now:
# 1. Detects "abc-analysis" pattern
# 2. Auto-triggers abc-analysis skill
# 3. Returns: {
#    "results": [...],
#    "auto_triggered_skills": ["abc-analysis"],
#    "skill_results": {...}
# }
"""


def create_integration_patch(
    original_execute_sql: Callable,
    skill_executor: Optional[Callable] = None,
    debug: bool = False
) -> Callable:
    """
    Create a patched execute_sql function

    Usage:
        patched_execute_sql = create_integration_patch(
            original_execute_sql,
            skill_executor=run_skills,
            debug=True
        )
        mcg_toolbox.execute_sql = patched_execute_sql
    """
    integration = MCGToolboxIntegration(original_execute_sql)
    integration.initialize(debug=debug)

    if skill_executor:
        integration.set_skill_executor(skill_executor)

    return integration.execute_sql_wrapper


# ============================================================================
# MINIMAL INTEGRATION (1 function)
# ============================================================================

def patch_mcg_toolbox(mcg_module, debug: bool = False):
    """
    Minimal one-liner integration

    Usage:
        from plugin_integration_hook import patch_mcg_toolbox
        patch_mcg_toolbox(mcg_toolbox, debug=True)
    """
    original_execute_sql = mcg_module.execute_sql
    integration = MCGToolboxIntegration(original_execute_sql)
    integration.initialize(debug=debug)
    mcg_module.execute_sql = integration.execute_sql_wrapper
    logger.info("MCG Toolbox patched with skill integration")


if __name__ == "__main__":
    print(__doc__)