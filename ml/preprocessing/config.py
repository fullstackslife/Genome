"""Configuration for normalization pipeline."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class NormalizationConfig:
    """Configuration for normalization pipeline."""

    # Log normalization
    log_base: float = 2.0
    use_log1p: bool = True  # Use log1p instead of log to handle zeros

    # Batch correction (placeholder for future)
    apply_batch_correction: bool = False
    batch_correction_method: Optional[str] = None

    # Reproducibility
    random_seed: int = 42

    # Scaling
    scale_to_unit_variance: bool = False
    center_mean: bool = False

    def to_dict(self) -> dict:
        """Convert config to dictionary for logging."""
        return {
            "log_base": self.log_base,
            "use_log1p": self.use_log1p,
            "apply_batch_correction": self.apply_batch_correction,
            "batch_correction_method": self.batch_correction_method,
            "random_seed": self.random_seed,
            "scale_to_unit_variance": self.scale_to_unit_variance,
            "center_mean": self.center_mean,
        }
