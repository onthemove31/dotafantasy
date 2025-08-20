from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "players",
        sa.Column("account_id", sa.Integer(), primary_key=True),
        sa.Column("persona_name", sa.String(length=120)),
        sa.Column("team_name", sa.String(length=120)),
        sa.Column("last_seen", sa.DateTime()),
    )

    op.create_table(
        "matches",
        sa.Column("match_id", sa.Integer(), primary_key=True),
        sa.Column("start_time", sa.DateTime()),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("patch", sa.String(length=16), nullable=False, server_default=sa.text("'unknown'")),
        sa.Column("radiant_win", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "match_players",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.match_id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("players.account_id", ondelete="CASCADE"), nullable=False),
        sa.Column("hero_id", sa.Integer(), nullable=False),
        sa.Column("kills", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deaths", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assists", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gpm", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("xpm", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lh", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dn", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("damage", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stuns", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("wards_placed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wards_destroyed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("win", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("match_id", "account_id", name="uix_match_player"),
    )


def downgrade() -> None:
    op.drop_table("match_players")
    op.drop_table("matches")
    op.drop_table("players")
