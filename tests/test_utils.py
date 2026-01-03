"""Unit tests for utility modules."""
import pytest
from utils.units import UnitConverter


class TestUnitConversions:
    """Test unit conversion functions."""

    def test_milli_to_base(self):
        """Test millinewton to newton conversion."""
        assert UnitConverter.mn_to_newtons(1000) == pytest.approx(1.0)
        assert UnitConverter.mn_to_newtons(500) == pytest.approx(0.5)
        assert UnitConverter.mn_to_newtons(0) == pytest.approx(0.0)

    def test_base_to_milli(self):
        """Test newton to millinewton conversion."""
        assert UnitConverter.newtons_to_mn(1.0) == pytest.approx(1000)
        assert UnitConverter.newtons_to_mn(0.5) == pytest.approx(500)
        assert UnitConverter.newtons_to_mn(0.0) == pytest.approx(0.0)

    def test_force_conversions(self):
        """Test force unit conversions."""
        # Newtons to kg
        kg = UnitConverter.newtons_to_kg(9.81)
        assert kg == pytest.approx(1.0, abs=0.01)

        # kg to Newtons
        newtons = UnitConverter.kg_to_newtons(1.0)
        assert newtons == pytest.approx(9.81, abs=0.01)

        # mN to kg
        kg_from_mn = UnitConverter.mn_to_kg(9810)
        assert kg_from_mn == pytest.approx(1.0, abs=0.01)

    def test_torque_conversions(self):
        """Test torque unit conversions."""
        # Nm to mNm
        mNm = UnitConverter.nm_to_mnm(1.0)
        assert mNm == pytest.approx(1000)

        # mNm to Nm
        Nm = UnitConverter.mnm_to_nm(1000)
        assert Nm == pytest.approx(1.0)

    def test_current_conversions(self):
        """Test current unit conversions."""
        # mA to A
        amps = UnitConverter.ma_to_amps(1000)
        assert amps == pytest.approx(1.0)

        # A to mA
        ma = UnitConverter.amps_to_ma(1.0)
        assert ma == pytest.approx(1000)
