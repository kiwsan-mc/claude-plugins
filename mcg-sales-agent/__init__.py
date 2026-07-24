#!/usr/bin/env python3
"""
MCG Sales Agent Plugin - Main Entry Point
Auto-initializes wrapper for auto-triggered skills on mcg-toolbox queries

Location: /var/folders/.../mcg-sales-agent/__init__.py
"""

import logging
import os
from typing import Optional, Callable, List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# IMPORT WRAPPER COMPONENTS
# ============================================================================

try:
    from mcg_sales_agent_wrapper_server import (
        MCGSalesAgentWrapper,
        initialize_wrapper,
        enable_wrapper,
        SkillTrigger
    )
    from plugin_integration_hook import (
        MCGToolboxIntegration,
        patch_mcg_toolbox,
        create_integration_patch
    )
    WRAPPER_AVAILABLE = True
    logger.info("✅ Wrapper components imported successfully")
except ImportError as e:
    WRAPPER_AVAILABLE = False
    logger.warning(f"⚠️ Wrapper components not available: {e}")
    logger.warning("   Plugin will run without auto-trigger feature")


# ============================================================================
# PLUGIN CONFIGURATION
# ============================================================================

class MCGSalesAgentConfig:
    """Plugin configuration"""

    # Auto-trigger settings
    ENABLE_AUTO_TRIGGER = True
    MIN_CONFIDENCE_THRESHOLD = 0.5
    PARALLEL_EXECUTION = True
    DEBUG_MODE = os.getenv("MCG_SALES_AGENT_DEBUG", "false").lower() == "true"

    # Timeout settings
    QUERY_TIMEOUT_SECONDS = 30
    SKILL_TIMEOUT_SECONDS = 5

    # Features
    ENRICH_RESULTS = True
    CACHE_RESULTS = False
    RETURN_CONFIDENCE_SCORES = True

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        cls.ENABLE_AUTO_TRIGGER = os.getenv(
            "MCG_AUTO_TRIGGER", "true"
        ).lower() == "true"
        cls.DEBUG_MODE = os.getenv(
            "MCG_DEBUG", "false"
        ).lower() == "true"
        cls.MIN_CONFIDENCE_THRESHOLD = float(
            os.getenv("MCG_MIN_CONFIDENCE", "0.5")
        )
        return cls


# ============================================================================
# PLUGIN STATE
# ============================================================================

class MCGSalesAgentPlugin:
    """Main plugin class - manages initialization and integration"""

    def __init__(self):
        """Initialize plugin"""
        self.config = MCGSalesAgentConfig.from_env()
        self.wrapper: Optional[MCGSalesAgentWrapper] = None
        self.integration: Optional[MCGToolboxIntegration] = None
        self.original_execute_sql: Optional[Callable] = None
        self.enabled = False
        self.initialized = False

    def initialize(self, mcg_toolbox_module: Optional[Any] = None) -> bool:
        """
        Initialize plugin and patch mcg-toolbox if available

        Args:
            mcg_toolbox_module: mcg-toolbox module to patch (optional)
                               If not provided, deferred until first use

        Returns:
            bool: True if initialization successful
        """
        if self.initialized:
            logger.info("⚠️ Plugin already initialized")
            return True

        if not WRAPPER_AVAILABLE:
            logger.warning("❌ Wrapper not available, skipping auto-trigger setup")
            self.initialized = True
            return False

        try:
            # Step 1: Create wrapper
            self.wrapper = MCGSalesAgentWrapper()
            self.wrapper.debug = self.config.DEBUG_MODE
            self.wrapper.min_confidence = self.config.MIN_CONFIDENCE_THRESHOLD

            logger.info(f"✅ Wrapper created (debug={self.config.DEBUG_MODE})")

            # Step 2: Patch mcg-toolbox if provided
            if mcg_toolbox_module:
                self._patch_mcg_toolbox(mcg_toolbox_module)

            # Step 3: Mark as initialized
            self.initialized = True
            self.enabled = self.config.ENABLE_AUTO_TRIGGER

            logger.info(
                f"✅ Plugin initialized "
                f"(auto_trigger={self.enabled}, min_confidence={self.config.MIN_CONFIDENCE_THRESHOLD})"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Plugin initialization failed: {e}")
            self.initialized = False
            self.enabled = False
            return False

    def _patch_mcg_toolbox(self, mcg_toolbox_module: Any) -> bool:
        """
        Patch mcg-toolbox.execute_sql with wrapper

        Args:
            mcg_toolbox_module: mcg-toolbox module

        Returns:
            bool: Success
        """
        try:
            # Save original
            self.original_execute_sql = mcg_toolbox_module.execute_sql

            # Create integration
            self.integration = MCGToolboxIntegration(self.original_execute_sql)
            self.integration.initialize(debug=self.config.DEBUG_MODE)

            # Patch execute_sql
            mcg_toolbox_module.execute_sql = self.integration.execute_sql_wrapper

            logger.info("✅ mcg-toolbox.execute_sql patched successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to patch mcg-toolbox: {e}")
            return False

    def set_skill_executor(self, executor: Callable) -> None:
        """
        Set skill executor function

        Args:
            executor: Function that executes detected skills
        """
        if self.integration:
            self.integration.set_skill_executor(executor)
            logger.info("✅ Skill executor registered")

    def enable(self, enable: bool = True) -> None:
        """Enable/disable auto-trigger"""
        if self.wrapper:
            self.wrapper.enabled = enable
            self.enabled = enable
            logger.info(f"Auto-trigger {'enabled' if enable else 'disabled'}")

    def set_debug(self, debug: bool = True) -> None:
        """Enable/disable debug mode"""
        if self.wrapper:
            self.wrapper.debug = debug
            logger.info(f"Debug mode {'enabled' if debug else 'disabled'}")

    def set_confidence_threshold(self, threshold: float) -> None:
        """Set minimum confidence threshold (0.0 - 1.0)"""
        if not 0.0 <= threshold <= 1.0:
            logger.error(f"Invalid threshold: {threshold} (must be 0.0-1.0)")
            return
        if self.wrapper:
            self.wrapper.min_confidence = threshold
            logger.info(f"Confidence threshold set to {threshold:.1%}")

    def detect_skills(self, query: str) -> List[str]:
        """Detect skills for a query (without executing)"""
        if not self.wrapper or not self.enabled:
            return []
        skills = self.wrapper.detect_skills(query)
        return [s.name for s in skills]

    def get_status(self) -> Dict[str, Any]:
        """Get plugin status"""
        return {
            "initialized": self.initialized,
            "enabled": self.enabled,
            "wrapper_available": WRAPPER_AVAILABLE,
            "debug_mode": self.config.DEBUG_MODE,
            "min_confidence": self.config.MIN_CONFIDENCE_THRESHOLD,
            "auto_trigger": self.config.ENABLE_AUTO_TRIGGER,
            "parallel_execution": self.config.PARALLEL_EXECUTION
        }


# ============================================================================
# GLOBAL PLUGIN INSTANCE
# ============================================================================

_plugin_instance: Optional[MCGSalesAgentPlugin] = None


def get_plugin() -> MCGSalesAgentPlugin:
    """Get or create global plugin instance"""
    global _plugin_instance
    if _plugin_instance is None:
        _plugin_instance = MCGSalesAgentPlugin()
    return _plugin_instance


# ============================================================================
# PUBLIC API
# ============================================================================

def initialize(mcg_toolbox_module: Optional[Any] = None) -> bool:
    """
    Initialize MCG Sales Agent plugin

    Usage:
        from mcg_sales_agent import initialize
        initialize(mcg_toolbox)

    Args:
        mcg_toolbox_module: mcg-toolbox module to patch

    Returns:
        bool: Success
    """
    plugin = get_plugin()
    return plugin.initialize(mcg_toolbox_module)


def set_skill_executor(executor: Callable) -> None:
    """
    Register skill executor function

    Usage:
        def run_skills(detected_skills):
            results = {}
            for skill in detected_skills:
                results[skill.name] = invoke_skill(skill.name)
            return results

        set_skill_executor(run_skills)
    """
    plugin = get_plugin()
    plugin.set_skill_executor(executor)


def enable_auto_trigger(enable: bool = True) -> None:
    """Enable/disable auto-trigger feature"""
    plugin = get_plugin()
    plugin.enable(enable)


def set_debug_mode(enable: bool = True) -> None:
    """Enable/disable debug logging"""
    plugin = get_plugin()
    plugin.set_debug(enable)


def detect_skills(query: str) -> List[str]:
    """Detect which skills would trigger for a query"""
    plugin = get_plugin()
    return plugin.detect_skills(query)


def get_status() -> Dict[str, Any]:
    """Get plugin status"""
    plugin = get_plugin()
    return plugin.get_status()


# ============================================================================
# FLASK/FASTAPI INTEGRATION EXAMPLES
# ============================================================================

def setup_flask_integration(app):
    """
    Setup plugin with Flask app

    Usage:
        from flask import Flask
        from mcg_sales_agent import setup_flask_integration
        import mcg_toolbox

        app = Flask(__name__)
        setup_flask_integration(app)
    """
    import mcg_toolbox

    # Initialize plugin
    initialize(mcg_toolbox)

    @app.route("/api/mcg/status", methods=["GET"])
    def get_plugin_status():
        """Get plugin status"""
        return get_status()

    @app.route("/api/mcg/query", methods=["POST"])
    def execute_query():
        """Execute query with auto-triggered skills"""
        from flask import request
        query = request.json.get("query")
        if not query:
            return {"error": "Query required"}, 400
        try:
            result = mcg_toolbox.execute_sql(query)
            return result
        except Exception as e:
            return {"error": str(e)}, 500

    logger.info("✅ Flask integration setup complete")


def setup_fastapi_integration(app):
    """
    Setup plugin with FastAPI app

    Usage:
        from fastapi import FastAPI
        from mcg_sales_agent import setup_fastapi_integration
        import mcg_toolbox

        app = FastAPI()
        setup_fastapi_integration(app)
    """
    import mcg_toolbox
    from pydantic import BaseModel

    # Initialize plugin
    initialize(mcg_toolbox)

    class QueryRequest(BaseModel):
        query: str

    @app.get("/api/mcg/status")
    async def get_plugin_status():
        """Get plugin status"""
        return get_status()

    @app.post("/api/mcg/query")
    async def execute_query(request: QueryRequest):
        """Execute query with auto-triggered skills"""
        try:
            result = mcg_toolbox.execute_sql(request.query)
            return result
        except Exception as e:
            return {"error": str(e)}

    logger.info("✅ FastAPI integration setup complete")


# ============================================================================
# PLUGIN INITIALIZATION (AUTO ON IMPORT)
# ============================================================================

def _auto_initialize():
    """
    Auto-initialize plugin on module import
    (if configuration allows)
    """
    try:
        # Check if auto-init enabled
        if not os.getenv("MCG_AUTO_INIT", "true").lower() == "true":
            logger.info("ℹ️ Auto-init disabled (set MCG_AUTO_INIT=true to enable)")
            return

        # Try to import mcg_toolbox
        try:
            import mcg_toolbox
            plugin = get_plugin()
            if plugin.initialize(mcg_toolbox):
                logger.info("✅ Plugin auto-initialized with mcg_toolbox")
        except ImportError:
            logger.info("ℹ️ mcg_toolbox not found, manual initialization required")

    except Exception as e:
        logger.warning(f"⚠️ Auto-init failed: {e}")


# Auto-initialize on import
_auto_initialize()


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__version__ = "1.0.0"
__all__ = [
    "initialize",
    "set_skill_executor",
    "enable_auto_trigger",
    "set_debug_mode",
    "detect_skills",
    "get_status",
    "get_plugin",
    "setup_flask_integration",
    "setup_fastapi_integration",
    "MCGSalesAgentConfig",
    "MCGSalesAgentPlugin",
]


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    import sys

    def show_status():
        """Show plugin status"""
        plugin = get_plugin()
        status = plugin.get_status()
        print("\n📊 MCG Sales Agent Plugin Status")
        print("=" * 50)
        for key, value in status.items():
            print(f"  {key}: {value}")
        print("=" * 50 + "\n")

    def test_detection():
        """Test pattern detection"""
        plugin = get_plugin()
        plugin.initialize()

        test_queries = [
            ("Dashboard", "SELECT SUM(sales), SUM(qty) FROM sales"),
            ("ABC", "SELECT category, product, SUM(sales) FROM sales GROUP BY category, product ORDER BY SUM(sales) DESC"),
            ("Member", "SELECT member_type, SUM(sales) FROM sales WHERE channel <> 'Marketplace' GROUP BY member_type"),
            ("Channel", "SELECT main_channel, SUM(sales) FROM sales GROUP BY main_channel"),
        ]

        print("\n🧪 Pattern Detection Test")
        print("=" * 50)
        for name, query in test_queries:
            skills = plugin.detect_skills(query)
            print(f"  {name}: {skills or 'No match'}")
        print("=" * 50 + "\n")

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "status":
            show_status()
        elif command == "test":
            test_detection()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python __init__.py [status|test]")
    else:
        show_status()