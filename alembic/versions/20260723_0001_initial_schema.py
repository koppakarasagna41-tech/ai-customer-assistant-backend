"""Initial production schema

Revision ID: 20260723_0001
Revises:
Create Date: 2026-07-23 00:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260723_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=True),
        sa.Column("permissions", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_user_id"), "users", ["user_id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "agents",
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("department", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("agent_id"),
    )
    op.create_index(op.f("ix_agents_agent_id"), "agents", ["agent_id"], unique=False)
    op.create_index(op.f("ix_agents_email"), "agents", ["email"], unique=True)

    op.create_table(
        "tickets",
        sa.Column("ticket_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("priority", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("assigned_agent_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("ticket_id"),
    )
    op.create_index(op.f("ix_tickets_ticket_id"), "tickets", ["ticket_id"], unique=False)

    op.create_table(
        "ticket_comments",
        sa.Column("comment_id", sa.String(), nullable=False),
        sa.Column("ticket_id", sa.String(), nullable=False),
        sa.Column("author", sa.String(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.ticket_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("comment_id"),
    )
    op.create_index(
        op.f("ix_ticket_comments_comment_id"), "ticket_comments", ["comment_id"], unique=False
    )

    op.create_table(
        "ticket_timeline",
        sa.Column("event_id", sa.String(), nullable=False),
        sa.Column("ticket_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("actor", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.ticket_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index(
        op.f("ix_ticket_timeline_event_id"), "ticket_timeline", ["event_id"], unique=False
    )

    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("performed_by", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.ticket_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_activity_logs_id"), "activity_logs", ["id"], unique=False)

    op.create_table(
        "assignment_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.ticket_id"]),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.agent_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assignment_history_id"), "assignment_history", ["id"], unique=False)

    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.String(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("uploaded_by", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.ticket_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_attachments_id"), "attachments", ["id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_id"), "audit_logs", ["id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_refresh_tokens_id"), "refresh_tokens", ["id"], unique=False)

    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("theme", sa.String(length=20), nullable=False),
        sa.Column("language", sa.String(length=20), nullable=False),
        sa.Column("email_notifications", sa.Boolean(), nullable=True),
        sa.Column("push_notifications", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_preferences_id"), "user_preferences", ["id"], unique=False)

    op.create_table(
        "conversations",
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("messages", sa.JSON(), nullable=True),
        sa.Column("session_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.create_index(
        op.f("ix_conversations_session_id"), "conversations", ["session_id"], unique=False
    )

    op.create_table(
        "analytics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("total_tickets", sa.Integer(), nullable=True),
        sa.Column("resolved_tickets", sa.Integer(), nullable=True),
        sa.Column("pending_tickets", sa.Integer(), nullable=True),
        sa.Column("escalated_tickets", sa.Integer(), nullable=True),
        sa.Column("avg_resolution_time_hrs", sa.Float(), nullable=True),
        sa.Column("avg_response_time_min", sa.Float(), nullable=True),
        sa.Column("customer_satisfaction_score", sa.Float(), nullable=True),
        sa.Column("ai_confidence_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analytics_id"), "analytics", ["id"], unique=False)


def downgrade() -> None:
    op.drop_table("analytics")
    op.drop_table("conversations")
    op.drop_table("user_preferences")
    op.drop_table("refresh_tokens")
    op.drop_table("notifications")
    op.drop_table("audit_logs")
    op.drop_table("attachments")
    op.drop_table("assignment_history")
    op.drop_table("activity_logs")
    op.drop_table("ticket_timeline")
    op.drop_table("ticket_comments")
    op.drop_table("tickets")
    op.drop_table("agents")
    op.drop_table("users")
