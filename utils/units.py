"""
Unit Conversion Utilities

Provides conversion functions between different units used in the test bench.
"""


class UnitConverter:
    """Unit conversion utilities for test bench measurements."""

    # Force conversions
    @staticmethod
    def newtons_to_kg(force_n: float) -> float:
        """
        Convert force from Newtons to kilograms (mass equivalent).

        Args:
            force_n: Force in Newtons

        Returns:
            Equivalent mass in kilograms (assuming g = 9.81 m/s²)
        """
        return force_n / 9.81

    @staticmethod
    def kg_to_newtons(mass_kg: float) -> float:
        """
        Convert mass to force.

        Args:
            mass_kg: Mass in kilograms

        Returns:
            Force in Newtons (assuming g = 9.81 m/s²)
        """
        return mass_kg * 9.81

    @staticmethod
    def mn_to_newtons(force_mn: float) -> float:
        """Convert millinewtons to Newtons."""
        return force_mn / 1000.0

    @staticmethod
    def newtons_to_mn(force_n: float) -> float:
        """Convert Newtons to millinewtons."""
        return force_n * 1000.0

    @staticmethod
    def mn_to_kg(force_mn: float) -> float:
        """Convert millinewtons to kilograms (mass equivalent)."""
        return force_mn / 1000.0 / 9.81

    @staticmethod
    def kg_to_mn(mass_kg: float) -> float:
        """Convert kilograms to millinewtons."""
        return mass_kg * 9.81 * 1000.0

    # Current conversions
    @staticmethod
    def ma_to_amps(current_ma: float) -> float:
        """Convert milliamps to amps."""
        return current_ma / 1000.0

    @staticmethod
    def amps_to_ma(current_a: float) -> float:
        """Convert amps to milliamps."""
        return current_a * 1000.0

    # Torque conversions
    @staticmethod
    def mnm_to_nm(torque_mnm: float) -> float:
        """Convert millinewton-meters to newton-meters."""
        return torque_mnm / 1000.0

    @staticmethod
    def nm_to_mnm(torque_nm: float) -> float:
        """Convert newton-meters to millinewton-meters."""
        return torque_nm * 1000.0

    # Angle conversions
    @staticmethod
    def counts_to_degrees(counts: int, counts_per_rev: int = 1000) -> float:
        """
        Convert encoder counts to degrees.

        Args:
            counts: Encoder counts
            counts_per_rev: Counts per revolution (default 1000)

        Returns:
            Angle in degrees
        """
        return (counts / counts_per_rev) * 360.0

    @staticmethod
    def degrees_to_counts(degrees: float, counts_per_rev: int = 1000) -> int:
        """
        Convert degrees to encoder counts.

        Args:
            degrees: Angle in degrees
            counts_per_rev: Counts per revolution (default 1000)

        Returns:
            Encoder counts (rounded to nearest integer)
        """
        return int(round((degrees / 360.0) * counts_per_rev))

    @staticmethod
    def counts_to_radians(counts: int, counts_per_rev: int = 1000) -> float:
        """
        Convert encoder counts to radians.

        Args:
            counts: Encoder counts
            counts_per_rev: Counts per revolution (default 1000)

        Returns:
            Angle in radians
        """
        import math
        return (counts / counts_per_rev) * 2 * math.pi

    @staticmethod
    def radians_to_counts(radians: float, counts_per_rev: int = 1000) -> int:
        """
        Convert radians to encoder counts.

        Args:
            radians: Angle in radians
            counts_per_rev: Counts per revolution (default 1000)

        Returns:
            Encoder counts
        """
        import math
        return int(round((radians / (2 * math.pi)) * counts_per_rev))

    # Velocity conversions
    @staticmethod
    def rpm_to_rad_per_sec(rpm: float) -> float:
        """Convert RPM to radians per second."""
        import math
        return rpm * (2 * math.pi) / 60.0

    @staticmethod
    def rad_per_sec_to_rpm(rad_per_sec: float) -> float:
        """Convert radians per second to RPM."""
        import math
        return rad_per_sec * 60.0 / (2 * math.pi)

    @staticmethod
    def rpm_to_deg_per_sec(rpm: float) -> float:
        """Convert RPM to degrees per second."""
        return rpm * 360.0 / 60.0

    @staticmethod
    def deg_per_sec_to_rpm(deg_per_sec: float) -> float:
        """Convert degrees per second to RPM."""
        return deg_per_sec * 60.0 / 360.0

    # Distance conversions (for stiffness tests)
    @staticmethod
    def mm_to_meters(distance_mm: float) -> float:
        """Convert millimeters to meters."""
        return distance_mm / 1000.0

    @staticmethod
    def meters_to_mm(distance_m: float) -> float:
        """Convert meters to millimeters."""
        return distance_m * 1000.0

    # Power conversions
    @staticmethod
    def watts_to_milliwatts(power_w: float) -> float:
        """Convert watts to milliwatts."""
        return power_w * 1000.0

    @staticmethod
    def milliwatts_to_watts(power_mw: float) -> float:
        """Convert milliwatts to watts."""
        return power_mw / 1000.0

    # Efficiency (as percentage)
    @staticmethod
    def efficiency_to_percent(efficiency: float) -> float:
        """
        Convert efficiency ratio to percentage.

        Args:
            efficiency: Efficiency as decimal (e.g., 0.45)

        Returns:
            Efficiency as percentage (e.g., 45.0)
        """
        return efficiency * 100.0

    @staticmethod
    def percent_to_efficiency(percent: float) -> float:
        """
        Convert percentage to efficiency ratio.

        Args:
            percent: Efficiency as percentage (e.g., 45.0)

        Returns:
            Efficiency as decimal (e.g., 0.45)
        """
        return percent / 100.0


# Convenience functions for common conversions
def format_force(force_mn: float, unit: str = 'N') -> str:
    """
    Format force with appropriate unit.

    Args:
        force_mn: Force in millinewtons
        unit: Desired unit ('N', 'kg', 'mN')

    Returns:
        Formatted string (e.g., "1.23 N" or "0.125 kg")
    """
    if unit == 'N':
        return f"{UnitConverter.mn_to_newtons(force_mn):.2f} N"
    elif unit == 'kg':
        return f"{UnitConverter.mn_to_kg(force_mn):.3f} kg"
    elif unit == 'mN':
        return f"{force_mn:.1f} mN"
    else:
        raise ValueError(f"Unknown force unit: {unit}")


def format_current(current_ma: float, unit: str = 'mA') -> str:
    """
    Format current with appropriate unit.

    Args:
        current_ma: Current in milliamps
        unit: Desired unit ('mA', 'A')

    Returns:
        Formatted string (e.g., "500 mA" or "0.5 A")
    """
    if unit == 'mA':
        return f"{current_ma:.1f} mA"
    elif unit == 'A':
        return f"{UnitConverter.ma_to_amps(current_ma):.3f} A"
    else:
        raise ValueError(f"Unknown current unit: {unit}")


def format_angle(counts: int, unit: str = 'deg', counts_per_rev: int = 1000) -> str:
    """
    Format angle with appropriate unit.

    Args:
        counts: Encoder counts
        unit: Desired unit ('deg', 'rad', 'counts')
        counts_per_rev: Counts per revolution

    Returns:
        Formatted string (e.g., "45.0°" or "0.785 rad")
    """
    if unit == 'deg':
        degrees = UnitConverter.counts_to_degrees(counts, counts_per_rev)
        return f"{degrees:.1f}°"
    elif unit == 'rad':
        radians = UnitConverter.counts_to_radians(counts, counts_per_rev)
        return f"{radians:.3f} rad"
    elif unit == 'counts':
        return f"{counts} counts"
    else:
        raise ValueError(f"Unknown angle unit: {unit}")


def format_torque(torque_mnm: float, unit: str = 'mNm') -> str:
    """
    Format torque with appropriate unit.

    Args:
        torque_mnm: Torque in millinewton-meters
        unit: Desired unit ('mNm', 'Nm')

    Returns:
        Formatted string (e.g., "1500 mNm" or "1.5 Nm")
    """
    if unit == 'mNm':
        return f"{torque_mnm:.1f} mNm"
    elif unit == 'Nm':
        return f"{UnitConverter.mnm_to_nm(torque_mnm):.3f} Nm"
    else:
        raise ValueError(f"Unknown torque unit: {unit}")


def format_efficiency(efficiency: float) -> str:
    """
    Format efficiency as percentage.

    Args:
        efficiency: Efficiency as decimal (0.0 to 1.0)

    Returns:
        Formatted string (e.g., "45.2%")
    """
    return f"{UnitConverter.efficiency_to_percent(efficiency):.1f}%"
