from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    for name, cols in TABLE_DEFS:
        op.create_table(name, *cols)
    op.create_index('ix_analytics_type_user','analytics_events',['event_type','user_id'])

def downgrade():
    for name, _ in reversed(TABLE_DEFS):
        op.drop_table(name)

pk = lambda: sa.Column('id',postgresql.UUID(),primary_key=True)
uuid_col = lambda n,**kw: sa.Column(n,postgresql.UUID(),**kw)
str_col = lambda n,**kw: sa.Column(n,sa.String(255),**kw)
jsonb = lambda n,**kw: sa.Column(n,postgresql.JSONB(),**kw)
ts = lambda n: sa.Column(n,sa.DateTime(timezone=True),server_default=sa.func.now())

TABLE_DEFS = [
    ('companies',[pk(),str_col('name'),sa.Column('description',sa.Text()),str_col('website'),str_col('company_size'),uuid_col('industry_id'),str_col('contact_email'),sa.Column('subscription_tier',sa.String(32)),str_col('entity_type'),str_col('geo_id',unique=True),sa.Column('is_verified',sa.Boolean()),uuid_col('tenant_id'),str_col('region'),str_col('lang_tag'),jsonb('ext_metadata'),ts('created_at'),ts('updated_at')]),
    ('industries',[pk(),str_col('code'),str_col('name'),sa.Column('description',sa.Text()),uuid_col('parent_id'),sa.Column('level',sa.Integer()),sa.Column('sort_order',sa.Integer()),uuid_col('tenant_id'),ts('created_at'),ts('updated_at')]),
    ('capabilities',[pk(),uuid_col('company_id'),str_col('name'),sa.Column('description',sa.Text()),str_col('category'),sa.Column('level',sa.Integer()),jsonb('evidence_ids'),uuid_col('tenant_id'),ts('created_at'),ts('updated_at')]),
    ('relationships',[pk(),str_col('source_type'),uuid_col('source_id'),str_col('target_type'),uuid_col('target_id'),str_col('relation_type'),sa.Column('strength',sa.Float()),jsonb('evidence_ids'),jsonb('metadata'),uuid_col('tenant_id'),ts('created_at')]),
    ('events',[pk(),str_col('entity_type'),uuid_col('entity_id'),str_col('event_type'),str_col('title'),sa.Column('description',sa.Text()),sa.Column('event_date',sa.Date()),str_col('impact'),str_col('source'),jsonb('metadata'),uuid_col('tenant_id'),ts('created_at')]),
    ('evidence',[pk(),str_col('entity_type'),uuid_col('entity_id'),sa.Column('claim',sa.Text()),str_col('source_url'),str_col('source_type'),sa.Column('confidence_level',sa.Float()),sa.Column('verified',sa.Boolean()),uuid_col('verified_by'),sa.Column('verified_at',sa.DateTime(timezone=True)),uuid_col('tenant_id'),ts('created_at')]),
    ('analytics_events',[pk(),str_col('event_type',index=True),uuid_col('user_id'),str_col('session_id'),str_col('entity_type'),uuid_col('entity_id'),jsonb('properties'),str_col('source'),sa.Column('client_ts',sa.DateTime(timezone=True)),sa.Column('server_ts',sa.DateTime(timezone=True)),uuid_col('tenant_id'),ts('created_at')]),
    ('certifications',[pk(),uuid_col('entity_id'),str_col('entity_type'),str_col('level'),str_col('cert_type'),str_col('status'),jsonb('ai_review_result'),uuid_col('reviewer_id'),sa.Column('review_comment',sa.Text()),jsonb('evidence_ids'),ts('applied_at'),sa.Column('reviewed_at',sa.DateTime(timezone=True)),sa.Column('issued_at',sa.DateTime(timezone=True)),sa.Column('expires_at',sa.DateTime(timezone=True)),sa.Column('revoked_at',sa.DateTime(timezone=True)),jsonb('metadata'),uuid_col('tenant_id'),ts('created_at'),ts('updated_at')]),
    ('subscriptions',[pk(),uuid_col('user_id'),str_col('plan_tier'),str_col('status'),sa.Column('current_period_start',sa.DateTime(timezone=True),nullable=False),sa.Column('current_period_end',sa.DateTime(timezone=True),nullable=False),sa.Column('cancel_at_period_end',sa.Boolean()),sa.Column('auto_renew',sa.Boolean()),sa.Column('trial_ends_at',sa.DateTime(timezone=True)),str_col('provider'),str_col('provider_subscription_id'),jsonb('quota_usage'),jsonb('metadata'),uuid_col('tenant_id'),ts('created_at'),ts('updated_at')]),
    ('orders',[pk(),uuid_col('user_id'),str_col('order_type'),sa.Column('amount',sa.Numeric(10,2),nullable=False),str_col('currency'),sa.Column('tax_amount',sa.Numeric(10,2)),str_col('status'),jsonb('items'),str_col('provider'),str_col('provider_order_id'),sa.Column('paid_at',sa.DateTime(timezone=True)),jsonb('metadata'),uuid_col('tenant_id'),ts('created_at'),ts('updated_at')]),
    ('payment_transactions',[pk(),uuid_col('order_id'),uuid_col('user_id'),sa.Column('amount',sa.Numeric(10,2)),str_col('currency'),sa.Column('fee_amount',sa.Numeric(10,2)),str_col('method'),str_col('provider'),str_col('provider_tx_id'),str_col('status'),str_col('error_message'),jsonb('metadata'),ts('created_at')]),
    ('market_demands',[pk(),uuid_col('publisher_id'),str_col('demand_type'),str_col('title'),sa.Column('description',sa.String(5000)),str_col('category'),sa.Column('budget_min',sa.Numeric(12,2)),sa.Column('budget_max',sa.Numeric(12,2)),sa.Column('timeline_days',sa.Integer()),jsonb('requirements'),str_col('status'),jsonb('matched_providers'),sa.Column('view_count',sa.Integer()),sa.Column('inquiry_count',sa.Integer()),uuid_col('tenant_id'),ts('created_at'),ts('updated_at'),sa.Column('expires_at',sa.DateTime(timezone=True))]),
    ('transaction_reviews',[pk(),uuid_col('transaction_id'),uuid_col('reviewer_id'),uuid_col('reviewee_id'),sa.Column('rating_quality',sa.Integer()),sa.Column('rating_communication',sa.Integer()),sa.Column('rating_timeliness',sa.Integer()),sa.Column('rating_value',sa.Integer()),str_col('review_text'),jsonb('evidence'),str_col('status'),sa.Column('verified_at',sa.DateTime(timezone=True)),ts('created_at')]),
    ('competitors',[pk(),str_col('name'),str_col('tier'),str_col('website'),sa.Column('description',sa.String(2000)),jsonb('scores'),jsonb('strengths'),jsonb('weaknesses'),sa.Column('geo_ie_advantage',sa.String(2000)),sa.Column('last_updated',sa.DateTime(timezone=True)),ts('created_at')]),
]