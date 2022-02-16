import re
from typing import Dict

from .colors import RgbColor, HlsColor

FUND_GROUP_BASE_COLORS: Dict[str, RgbColor] = {
    "PASSIVE": RgbColor(red=200, green=40, blue=40),
    'ACTIVE': RgbColor(red=200, green=40, blue=40),
    'BALANCED': RgbColor(red=230, green=130, blue=0),
    'FIXED_INCOME': RgbColor(red=80, green=140, blue=80),
    'OTHER': RgbColor(red=100, green=100, blue=100)}


class FundUtils:

    @staticmethod
    def get_fund_color(fund_group: str, risk_level: int) -> RgbColor:
        """
        Creates fund based on fund group and risk level
        Args:
            fund_group: fund group
            risk_level: risk level

        Returns:
            Fund color
        """
        base_color = FundUtils.get_fund_group_base_color(fund_group=fund_group)
        color = base_color.to_hls()
        lightness_add = ((7 - min(max(1, risk_level), 7)) * 0.07)
        return HlsColor(hue=color.hue, lightness=color.lightness + lightness_add, saturation=color.saturation).to_rgb()

    @staticmethod
    def get_fund_group_base_color(fund_group: str) -> RgbColor:
        """
        Returns base color for given fund group
        Args:
            fund_group: fund group

        Returns:
            base color for given fund group
        """
        return FUND_GROUP_BASE_COLORS.get(fund_group, FUND_GROUP_BASE_COLORS["OTHER"])

    @staticmethod
    def get_fund_long_name_from_security_name(security_name: str) -> str:
        """
        Translates security name into long fund name. Fund name is almost identical to security name
        with exception that fund name does not contain postfix for series (A, B, VA, etc).

        Args:
            security_name: security name

        Returns:
            long fund name
        """
        regex = r" [B]{0,1}\([A-Z]{1,}\).*"
        return re.sub(regex, "", security_name, 0, re.MULTILINE).strip()

    @staticmethod
    def get_fund_short_name_from_security_name(security_name: str) -> str:
        """
        Translates security name into short fund name. Short find name is the security name
        without company name prefix and series postfix

        Args:
            security_name: security name

        Returns:
            short fund name
        """
        prefixes = ["Seligson & Co", "LähiTapiola", "LocalTapiola", "LokalTapiola"]
        result = FundUtils.get_fund_long_name_from_security_name(security_name=security_name)

        for prefix in prefixes:
            result = result.removeprefix(prefix)

        return result.strip()
