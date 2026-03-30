from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Dict, Any


class ServiceDegradationStatus(Enum):
    """ Service degradation Status """

    # Everything is working fine
    HEALTHY = "healthy"

    # Some components are slow or experiencing minor issues
    DEGRADED = "degraded"

    # A major component is down, affecting service functionality
    CRITICAL = "critical"


class ComponentDegradationLevel(Enum):
    """
    Represents the degradation state of a system component.

    This enumeration defines the possible levels of degradation that a component
    can experience during operation.

    Attributes:
        NONE (str): The component is in perfect condition, with no degradation.
        PART_DEGRADED (str): The component is partially degraded, causing minor
            performance loss or inefficiency.
        FULLY_DEGRADED (str): The component is fully degraded and no longer
            functioning as intended.
    """

    # The component is in perfect condition, with no degradation.
    NONE = "none"

    # The component is partially degraded, causing minor performance loss or
    # inefficiency.
    PART_DEGRADED = "partial"

    # The component is fully degraded and no longer functioning as intended.
    FULLY_DEGRADED = "fully_degraded"


@dataclass(slots=True)
class ServiceState:
    """
    Represents the operational state of a service, including health,
    optional database condition, version, and maintenance mode.
    """
    # pylint: disable=too-many-instance-attributes

    # Service health
    service_health: ComponentDegradationLevel = ComponentDegradationLevel.NONE
    service_health_state_str: str = ""

    # Database health (optional, ignored if service has no DB)
    database_enabled: bool = True  # Controls whether DB health is used
    database_health: ComponentDegradationLevel = ComponentDegradationLevel.NONE
    database_health_state_str: str = ""

    # Metadata
    version: str = ""
    startup_time: int = field(default_factory=lambda: int(time.time()))

    # Maintenance flag
    in_maintenance: bool = False

    # ---------------------------------------------------------------------
    # Lifecycle helpers
    # ---------------------------------------------------------------------

    def mark_database_failed(self, reason: str = "Fatal SQL failure") -> None:
        """
        Mark the database as failed and enter maintenance mode (if DB is
        enabled).
        """
        if not self.database_enabled:
            return
        self.database_health = ComponentDegradationLevel.FULLY_DEGRADED
        self.database_health_state_str = reason
        self.enter_maintenance(f"Database failure: {reason}")

    def mark_service_failed(self, reason: str) -> None:
        """Mark the service as failed and enter maintenance mode."""
        self.service_health = ComponentDegradationLevel.FULLY_DEGRADED
        self.service_health_state_str = reason
        self.enter_maintenance(reason)

    def enter_maintenance(self,
                          reason: str = "Entering maintenance mode") -> None:
        """Enable maintenance mode."""
        self.in_maintenance = True
        self.service_health = ComponentDegradationLevel.FULLY_DEGRADED
        self.service_health_state_str = reason

    def exit_maintenance(self) -> None:
        """Disable maintenance mode (return to normal operation)."""
        self.in_maintenance = False
        self.service_health = ComponentDegradationLevel.NONE
        self.service_health_state_str = "Normal operation"

    def is_operational(self) -> bool:
        """Return True if the service is fully operational."""
        return not self.in_maintenance

    # ---------------------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation of the state."""
        data = {
            "service_health": self.service_health.name,
            "service_health_state_str": self.service_health_state_str,
            "version": self.version,
            "startup_time": self.startup_time,
            "in_maintenance": self.in_maintenance
        }

        if self.database_enabled:
            data.update({
                "database_health": self.database_health.name,
                "database_health_state_str": self.database_health_state_str,
            })

        return data
