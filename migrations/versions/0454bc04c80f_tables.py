"""tables

Revision ID: 0454bc04c80f
Revises: 
Create Date: 2024-12-31 23:53:41.341801

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0454bc04c80f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('media',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('type', sa.Enum('tv', 'film', name='mediatype', create_constraint=True), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title', 'type', name='_media_title_type_uc')
    )
    with op.batch_alter_table('media', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_media_title'), ['title'], unique=False)

    op.create_table('subscription',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('cost', sa.String(), nullable=False),
    sa.Column('payment_frequency', sa.Enum('monthly', 'yearly', name='paymentfrequency', create_constraint=True), nullable=False),
    sa.Column('active_date', sa.Date(), nullable=False),
    sa.Column('inactive_date', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('subscription', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_subscription_active_date'), ['active_date'], unique=False)
        batch_op.create_index(batch_op.f('ix_subscription_name'), ['name'], unique=True)

    op.create_table('log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('subscription_id', sa.Integer(), nullable=False),
    sa.Column('media_id', sa.Integer(), nullable=False),
    sa.Column('season', sa.Integer(), nullable=True),
    sa.Column('episode', sa.Integer(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['media_id'], ['media.id'], ),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscription.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_log_date'), ['date'], unique=False)
        batch_op.create_index(batch_op.f('ix_log_media_id'), ['media_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_log_subscription_id'), ['subscription_id'], unique=False)

    op.drop_table('_alembic_tmp_media')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('_alembic_tmp_media',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=256), nullable=False),
    sa.Column('type', sa.VARCHAR(length=4), nullable=False),
    sa.Column('description', sa.VARCHAR(length=256), nullable=True),
    sa.CheckConstraint("type IN ('tv', 'film')", name='mediatype'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title', 'type', name='_media_title_type_uc')
    )
    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_log_subscription_id'))
        batch_op.drop_index(batch_op.f('ix_log_media_id'))
        batch_op.drop_index(batch_op.f('ix_log_date'))

    op.drop_table('log')
    with op.batch_alter_table('subscription', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_subscription_name'))
        batch_op.drop_index(batch_op.f('ix_subscription_active_date'))

    op.drop_table('subscription')
    with op.batch_alter_table('media', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_media_title'))

    op.drop_table('media')
    # ### end Alembic commands ###