from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String
from db import Base


# Create a table Model which inherit from Base
class AnkiNoteModel(Base):
    """Create a table based on the specified model as follows:"""

    __tablename__ = "vector_table_1"

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    vector = Column(Vector(dim=1536))
