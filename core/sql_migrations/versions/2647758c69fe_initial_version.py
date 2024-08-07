"""initial version

Revision ID: 2647758c69fe
Revises: 
Create Date: 2024-07-21 17:37:53.374130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2647758c69fe'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('property',
    sa.Column('property_id', sa.Uuid(), nullable=False),
    sa.Column('data_source_type', sa.Enum('REAL_ESTATE', 'DOMAIN', name='datasourcetype'), nullable=False),
    sa.Column('listing_type', sa.Enum('BUY', 'RENT', name='listingtype'), nullable=False),
    sa.Column('query_city', sa.Unicode(length=20), nullable=False),
    sa.Column('query_state', sa.Unicode(length=10), nullable=False),
    sa.Column('query_region', sa.Unicode(length=200), nullable=False),
    sa.Column('search_page', sa.SmallInteger(), nullable=False),
    sa.Column('url', sa.Unicode(length=250), nullable=False),
    sa.Column('price_detail', sa.Unicode(length=100), nullable=False),
    sa.Column('address', sa.Unicode(length=200), nullable=False),
    sa.Column('num_bedrooms', sa.SmallInteger(), nullable=True),
    sa.Column('num_bathrooms', sa.SmallInteger(), nullable=True),
    sa.Column('num_carparks', sa.SmallInteger(), nullable=True),
    sa.Column('area_sqm', sa.Integer(), nullable=True),
    sa.Column('property_type', sa.Enum('HOUSE', 'TOWNHOUSE', 'APARTMENT', 'UNIT', 'RETIREMENT_LIVING', 'RESIDENTIAL_LAND', 'BLOCK_OF_UNITS', 'OTHER', name='propertytype'), nullable=False),
    sa.Column('remarks', sa.Unicode(length=200), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('total_duration_seconds', sa.Float(), nullable=True),
    sa.Column('first_created', sa.DateTime(), nullable=False),
    sa.Column('last_updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('property_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('property')
    # ### end Alembic commands ###
