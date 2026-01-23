from pydantic import BaseModel

class SeatingConfigRequest(BaseModel):
    tech_stack: str
    rows: int
    columns: int
