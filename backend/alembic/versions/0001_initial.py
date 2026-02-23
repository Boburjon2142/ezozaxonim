"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-22
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("preferred_work_hours", sa.String(length=64), nullable=False),
        sa.Column("goals", sa.String(length=500), nullable=False),
        sa.Column("push_enabled", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_premium", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "organizations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "organization_members",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("organization_id", sa.String(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
    )
    op.create_index("ix_org_members_org", "organization_members", ["organization_id"], unique=False)
    op.create_index("ix_org_members_user", "organization_members", ["user_id"], unique=False)

    op.create_table(
        "plans",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("reflection", sa.String(length=1000), nullable=False),
    )
    op.create_index("ix_plans_user", "plans", ["user_id"], unique=False)
    op.create_index("ix_plans_date", "plans", ["date"], unique=False)

    op.create_table(
        "plan_items",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("plan_id", sa.String(), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("estimate_minutes", sa.Integer(), nullable=False),
        sa.Column("tags", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_plan_items_plan", "plan_items", ["plan_id"], unique=False)

    op.create_table(
        "time_sessions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("plan_item_id", sa.String(), sa.ForeignKey("plan_items.id"), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("tags", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_time_sessions_user", "time_sessions", ["user_id"], unique=False)
    op.create_index("ix_time_sessions_started", "time_sessions", ["started_at"], unique=False)

    op.create_table(
        "checkins",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("energy", sa.Integer(), nullable=False),
        sa.Column("stress", sa.Integer(), nullable=False),
        sa.Column("mood", sa.Integer(), nullable=False),
        sa.Column("sleep", sa.Integer(), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=False),
    )
    op.create_index("ix_checkins_user", "checkins", ["user_id"], unique=False)
    op.create_index("ix_checkins_date", "checkins", ["date"], unique=False)

    op.create_table(
        "break_rules",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("focus_min", sa.Integer(), nullable=False),
        sa.Column("break_min", sa.Integer(), nullable=False),
        sa.Column("long_break_min", sa.Integer(), nullable=False),
        sa.Column("long_break_every", sa.Integer(), nullable=False),
        sa.Column("adaptive_enabled", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "notification_logs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
        sa.Column("snoozed_count", sa.Integer(), nullable=False),
    )
    op.create_index("ix_notification_user", "notification_logs", ["user_id"], unique=False)

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tier", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_subscriptions_user", "subscriptions", ["user_id"], unique=False)

    op.create_table(
        "feature_flags",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("key", sa.String(length=80), nullable=False),
        sa.Column("enabled", sa.String(length=10), nullable=False),
    )
    op.create_index("ix_feature_flags_user", "feature_flags", ["user_id"], unique=False)
    op.create_index("ix_feature_flags_key", "feature_flags", ["key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_feature_flags_key", table_name="feature_flags")
    op.drop_index("ix_feature_flags_user", table_name="feature_flags")
    op.drop_table("feature_flags")

    op.drop_index("ix_subscriptions_user", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index("ix_notification_user", table_name="notification_logs")
    op.drop_table("notification_logs")

    op.drop_table("break_rules")

    op.drop_index("ix_checkins_date", table_name="checkins")
    op.drop_index("ix_checkins_user", table_name="checkins")
    op.drop_table("checkins")

    op.drop_index("ix_time_sessions_started", table_name="time_sessions")
    op.drop_index("ix_time_sessions_user", table_name="time_sessions")
    op.drop_table("time_sessions")

    op.drop_index("ix_plan_items_plan", table_name="plan_items")
    op.drop_table("plan_items")

    op.drop_index("ix_plans_date", table_name="plans")
    op.drop_index("ix_plans_user", table_name="plans")
    op.drop_table("plans")

    op.drop_index("ix_org_members_user", table_name="organization_members")
    op.drop_index("ix_org_members_org", table_name="organization_members")
    op.drop_table("organization_members")

    op.drop_table("organizations")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
