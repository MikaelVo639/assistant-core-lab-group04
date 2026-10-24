"""Render assigned study blocks as a readable numbered plan."""

from shared.contract import Block


def render(blocks: list[Block]) -> str:
    """Show allocated total hours and each task's assigned hours to one decimal."""
    lines = [f"Tonight ({sum(block.hours for block in blocks):.1f} h):"]
    lines.extend(f"  {index}. {block.task.title} ...... {block.hours:.1f} h" for index, block in enumerate(blocks, 1))
    return "\n".join(lines)
