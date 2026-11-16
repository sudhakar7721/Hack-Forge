display_name: Mapped[str] = mapped_column(
    "full_name",
    String(160),
    default="",
    nullable=False
)

active: Mapped[bool] = mapped_column(
    "is_active",
    Boolean,
    default=True,
    nullable=False
)