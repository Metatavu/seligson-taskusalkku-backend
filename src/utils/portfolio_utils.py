class PortfolioUtils:
    @staticmethod
    def get_portfolio_key(original_portfolio_id: str) -> str:
        """

        Args:
            original_portfolio_id: string representing portfolio original id

        Returns:
            either 0001 if the portfolio is the main portfolio or in case of
            sub portfolio dd00 where dd represents a number between 01-99.
        """
        portfolio_id_parts = original_portfolio_id.split("_")
        if len(portfolio_id_parts) == 2:
            portfolio_key = portfolio_id_parts[1].zfill(2)
        else:
            portfolio_key = "00"

        return portfolio_key + "01"

    @staticmethod
    def make_reference(share: str, company_code: str, portfolio_key: str) -> str:
        """

        Args:
            share(str): string representing profit("10") or growth("20")
            company_code(str): original company code associated with the portfolio
            portfolio_key(str): string value generated from portfolio id

        Returns(str):
            value including the concatenation of input with an extra digit, which is
            formulated from input parameters.

        """
        multiplier = [7, 3, 1]
        sum_of_digits = 0
        stem = share + company_code + portfolio_key
        i = len(stem) - 1
        j = 0
        while i >= 0:
            sum_of_digits += int(stem[i]) * multiplier[j % 3]
            i -= 1
            j += 1
        final_number = (10 - (sum_of_digits % 10)) % 10
        return stem + str(final_number)
