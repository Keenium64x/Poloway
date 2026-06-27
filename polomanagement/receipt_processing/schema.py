from typing import Literal

from pydantic import BaseModel, Field


ReceiptLineType = Literal["Item", "Horse", "Groom", "Tournament", "Service", "Other"]
TransactionType = Literal["Purchase", "Sale", "Expense", "Income"]
CostCategory = Literal[
	"Feed",
	"Equipment",
	"Supplies",
	"Supplements",
	"Groom Salary",
	"Overtime Pay",
	"Benefits",
	"Horse Purchase",
	"Horse Sale",
	"Medical",
	"Farrier",
	"Training",
	"Tournament",
	"Transport",
	"Service",
	"Other",
]


class ReceiptLineExtraction(BaseModel):
	line_type: ReceiptLineType = "Other"
	description: str = ""
	item_name: str | None = None
	horse_name: str | None = None
	groom_name: str | None = None
	tournament: str | None = None
	quantity: float = 1
	unit: str | None = None
	rate: float = 0
	tax_amount: float = 0
	total: float = 0
	cost_category: CostCategory = "Other"
	affects_inventory: bool = False
	confidence: float | None = Field(default=None, ge=0, le=1)


class ReceiptExtraction(BaseModel):
	vendor_name: str | None = None
	transaction_date: str | None = Field(default=None, description="ISO date, yyyy-mm-dd if visible")
	transaction_type: TransactionType = "Purchase"
	transaction_category: CostCategory = "Other"
	currency: str | None = None
	payment_method: str | None = None
	total_amount: float = 0
	lines: list[ReceiptLineExtraction] = Field(default_factory=list)
	notes: str | None = None
	confidence: float | None = Field(default=None, ge=0, le=1)
