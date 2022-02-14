import re


class FundUtils:

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
