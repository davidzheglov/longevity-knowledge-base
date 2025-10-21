from pydantic import BaseModel
from typing import Dict

class RunContext(BaseModel):
    gene_alias_map: Dict