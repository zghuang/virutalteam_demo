import httpx
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.financial_data import FinancialData

CIK_MAP = {
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "GOOGL": "0001652044",
    "GOOG": "0001652044",
    "AMZN": "0001018724",
    "TSLA": "0001318605",
    "META": "0001326801",
    "NVDA": "0001045810",
    "JPM": "0000019617",
    "V": "0001403161",
    "JNJ": "0000200406",
    "WMT": "0000104169",
    "PG": "0000080424",
    "MA": "0001141391",
    "UNH": "0000731766",
    "HD": "0000354950",
    "DIS": "0001744489",
    "BAC": "0000070858",
    "XOM": "0000034088",
    "INTC": "0000050863",
}

SEC_BASE_URL = "https://data.sec.gov/submissions"
USER_AGENT = "FinancialIngestionService/1.0 (huangyuxin2012@gmail.com)"


class FinancialIngestionError(Exception):
    pass


class FinancialIngestionService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    @staticmethod
    def ticker_to_cik(ticker: str) -> str:
        ticker_upper = ticker.upper().strip()
        if ticker_upper in CIK_MAP:
            return CIK_MAP[ticker_upper]
        raise FinancialIngestionError(f"Unknown ticker: {ticker}")

    async def fetch_company_filings(self, ticker: str) -> list[dict]:
        cik = self.ticker_to_cik(ticker)
        url = f"{SEC_BASE_URL}/CIK{cik}.json"

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                url,
                headers={"User-Agent": USER_AGENT},
            )
            if resp.status_code != 200:
                raise FinancialIngestionError(
                    f"SEC API returned {resp.status_code} for ticker {ticker}"
                )

            data = resp.json()

        filings = data.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        acc_nums = filings.get("accessionNumber", [])

        results = []
        for i, form_type in enumerate(forms):
            if form_type not in ("10-K", "10-Q"):
                continue
            results.append({
                "ticker": ticker.upper(),
                "form_type": form_type,
                "filing_date": dates[i] if i < len(dates) else None,
                "accession_number": acc_nums[i] if i < len(acc_nums) else None,
            })

        return results

    def store_financial_data(self, ticker: str, filings: list[dict]) -> list[FinancialData]:
        records = []
        for filing in filings:
            record = FinancialData(
                company_name=ticker.upper(),
                ticker=ticker.upper(),
                data_type=filing["form_type"],
                value=0.0,
                currency="USD",
                period=filing.get("filing_date"),
                source_url=self._build_filing_url(filing.get("accession_number")),
                published_at=self._parse_filing_date(filing.get("filing_date")),
            )
            records.append(record)
            self.db.add(record)

        self.db.commit()
        return records

    @staticmethod
    def _build_filing_url(accession_number: Optional[str]) -> Optional[str]:
        if not accession_number:
            return None
        return (
            f"https://www.sec.gov/Archives/edgar/data/"
            f"{accession_number.replace('-', '')}/index.json"
        )

    @staticmethod
    def _parse_filing_date(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    async def ingest(self, ticker: str) -> list[FinancialData]:
        filings = await self.fetch_company_filings(ticker)
        return self.store_financial_data(ticker, filings)
