"""Configuration loading and management."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class AnthropicConfig:
    """Anthropic API configuration."""

    api_key: str
    model: str = "claude-sonnet-4-5"


@dataclass
class ElevenlabsConfig:
    """ElevenLabs API configuration."""

    api_key: str
    voice_id: str = "Antoni"
    model: str = "eleven_turbo_v2_5"
    stability: float = 0.5
    similarity_boost: float = 0.75
    volume_boost: float = 0.0  # Volume boost in dB (0.0 = normal, 10.0 = louder, 20.0 = loudest)


@dataclass
class HotkeyConfig:
    """Hotkey configuration."""

    toggle_voice: Optional[str] = None
    force_analyze: Optional[str] = None
    correction_mode: Optional[str] = None
    # Aliases for backward compatibility
    toggle: str = None
    correct: str = None

    def __post_init__(self):
        """Set up aliases."""
        if self.toggle is None:
            self.toggle = self.toggle_voice or "f10"
        if self.correct is None:
            self.correct = self.correction_mode or "ctrl+c"


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""

    fps: int = 2
    motion_threshold: float = 0.02
    ball_stop_duration: float = 1.0
    monitor_index: int = 0  # Which monitor to capture (0 = primary)


@dataclass
class AIConfig:
    """AI model configuration."""

    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 150
    temperature: float = 0.7
    target_image_size: List[int] = None

    def __post_init__(self):
        """Initialize default image size if not provided."""
        if self.target_image_size is None:
            self.target_image_size = [1280, 720]


@dataclass
class CacheConfig:
    """Cache configuration."""

    pattern_cache_file: str = "data/cache/pattern_cache.json"
    hamming_threshold: int = 10
    min_confidence_to_cache: float = 0.7
    # Aliases for backward compatibility
    confidence_threshold: float = None
    hamming_distance_max: int = None
    persist_interval: int = 10

    def __post_init__(self):
        """Set up aliases."""
        if self.confidence_threshold is None:
            self.confidence_threshold = self.min_confidence_to_cache
        if self.hamming_distance_max is None:
            self.hamming_distance_max = self.hamming_threshold


@dataclass
class CostConfig:
    """Cost management configuration."""

    max_cost_per_round: float = 5.0
    warn_at_cost: float = 3.0
    # Aliases for backward compatibility
    budget_per_round: float = None
    warn_at_percentage: float = None

    def __post_init__(self):
        """Set up aliases."""
        if self.budget_per_round is None:
            self.budget_per_round = self.max_cost_per_round
        if self.warn_at_percentage is None:
            # Calculate percentage from absolute values
            if self.max_cost_per_round > 0:
                self.warn_at_percentage = self.warn_at_cost / self.max_cost_per_round
            else:
                self.warn_at_percentage = 0.80


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    file: str = "logs/mully-mouth.log"


@dataclass
class Config:
    """Main application configuration."""

    anthropic: AnthropicConfig
    elevenlabs: ElevenlabsConfig
    personality: str = "neutral"
    commentary_frequency: float = 0.7
    name_frequency: float = 0.3
    volume_boost: float = 0.0  # Volume boost in dB
    hotkeys: HotkeyConfig = None
    monitoring: MonitoringConfig = None
    ai: AIConfig = None
    cache: CacheConfig = None
    cost: CostConfig = None
    logging: LoggingConfig = None

    def __post_init__(self):
        """Initialize default configs if not provided."""
        if self.hotkeys is None:
            self.hotkeys = HotkeyConfig()
        if self.monitoring is None:
            self.monitoring = MonitoringConfig()
        if self.ai is None:
            self.ai = AIConfig()
        if self.cache is None:
            self.cache = CacheConfig()
        if self.cost is None:
            self.cost = CostConfig()
        if self.logging is None:
            self.logging = LoggingConfig()


def _expand_env_vars(value: Any) -> Any:
    """
    Recursively expand environment variables in config values.

    Args:
        value: Config value (str, dict, list, or other)

    Returns:
        Value with environment variables expanded
    """
    if isinstance(value, str):
        # Handle ${VAR} syntax
        if value.startswith("${") and value.endswith("}"):
            var_name = value[2:-1]
            return os.environ.get(var_name, "")
        return value
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_expand_env_vars(item) for item in value]
    return value


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file.

    API keys are loaded in this priority order:
    1. Securely stored credentials (Windows Credential Manager)
    2. Environment variables (ANTHROPIC_API_KEY, ELEVENLABS_API_KEY)
    3. Config file values

    Args:
        config_path: Path to config file (default: config/config.yaml)

    Returns:
        Config object

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    if config_path is None:
        config_path = "config/config.yaml"

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Run setup wizard: python setup_wizard.py\n"
            f"Or copy template: cp config/config.yaml.template config/config.yaml"
        )

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    # Expand environment variables
    data = _expand_env_vars(data)

    # Try to load from secure credential store first
    try:
        from src.lib.credentials import CredentialsManager
        creds = CredentialsManager()

        # Priority 1: Stored credentials
        stored_anthropic = creds.get_anthropic_key()
        stored_elevenlabs = creds.get_elevenlabs_key()
    except Exception:
        stored_anthropic = None
        stored_elevenlabs = None

    # Priority 2: Environment variables
    env_anthropic = os.environ.get("ANTHROPIC_API_KEY")
    env_elevenlabs = os.environ.get("ELEVENLABS_API_KEY")

    # Apply in priority order: stored > env > config file
    anthropic_key = stored_anthropic or env_anthropic
    if anthropic_key:
        if "anthropic" not in data:
            data["anthropic"] = {}
        data["anthropic"]["api_key"] = anthropic_key

    elevenlabs_key = stored_elevenlabs or env_elevenlabs
    if elevenlabs_key:
        if "elevenlabs" not in data:
            data["elevenlabs"] = {}
        data["elevenlabs"]["api_key"] = elevenlabs_key

    # Parse AI config first to potentially use its model
    ai_config = None
    if "ai" in data:
        ai_config = AIConfig(**data["ai"])

    # Parse nested configs
    anthropic_data = data.get("anthropic", {})
    # If model is in AI config but not in anthropic, use AI model
    if ai_config and "model" not in anthropic_data:
        anthropic_data["model"] = ai_config.model
    anthropic_config = AnthropicConfig(**anthropic_data)

    elevenlabs_config = ElevenlabsConfig(**data.get("elevenlabs", {}))

    hotkeys_config = None
    if "hotkeys" in data:
        hotkeys_config = HotkeyConfig(**data["hotkeys"])

    monitoring_config = None
    if "monitoring" in data:
        monitoring_config = MonitoringConfig(**data["monitoring"])

    cache_config = None
    if "cache" in data:
        cache_config = CacheConfig(**data["cache"])

    cost_config = None
    if "cost" in data:
        cost_config = CostConfig(**data["cost"])

    logging_config = None
    if "logging" in data:
        logging_config = LoggingConfig(**data["logging"])

    return Config(
        anthropic=anthropic_config,
        elevenlabs=elevenlabs_config,
        personality=data.get("personality", "neutral"),
        commentary_frequency=data.get("commentary_frequency", 0.7),
        name_frequency=data.get("name_frequency", 0.3),
        volume_boost=data.get("volume_boost", 0.0),
        hotkeys=hotkeys_config,
        monitoring=monitoring_config,
        ai=ai_config,
        cache=cache_config,
        cost=cost_config,
        logging=logging_config,
    )
