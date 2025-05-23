"""Add image column to kindle_reading table

Revision ID: e2e68fe3f052
Revises: 4eb5ab509a18
Create Date: 2025-04-13 16:21:58.352132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = 'e2e68fe3f052'
down_revision: Union[str, None] = '4eb5ab509a18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('kindle_reading', sa.Column('image', sa.String(), nullable=True, comment='image_column'))


    # Fetch all rows from the kindle_reading table
    connection = op.get_bind()
    result = connection.execute(text("SELECT id, asin FROM kindle_reading")).fetchall()

    # Update each row with the transformed ASIN
    for row in result:
        image = get_asin_image(row[1])  # Access 'asin' using the second element of the tuple
        if not image:
            image = ""
        connection.execute(
            text("UPDATE kindle_reading SET image = :image WHERE id = :id"),
            {"image": image, "id": row[0]}
        )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('kindle_reading', 'image')
    # ### end Alembic commands ###


def get_asin_image(asin: str) -> Union[str, None]:
    """Returns the image url associated with a given asin code. Returns None if not valid
    asin.

    Parameters
    ----------
    asin : str
        asin code.

    Returns
    -------
    str | None
        Returns asin image url if input is valid asin code. Otherwise returns None.
    """
    if not is_valid_asin(asin):
        return None
    return f"https://images.amazon.com/images/P/{asin}.jpg"

def is_valid_asin(asin: str) -> bool:
    """Checks if a given string is an ASIN code. Asin codes are made of 10 alphanumeric
    characters. They begin with "B0"

    Parameters
    ----------
    asin : str
        String to check

    Returns
    -------
    bool
        True if input is an asin code.
    """
    return (
        len(asin) == 10 and asin.isalnum() and asin.isupper() and asin.startswith("B0")
    )
