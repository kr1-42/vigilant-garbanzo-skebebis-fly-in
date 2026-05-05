"""Asset loading utilities for GIFs and sprites."""

import pygame
from PIL import Image


def load_gif_frames(gif_path: str, max_width: int = 20, max_height: int = 20) -> tuple[list, int] | None:
    """Load all frames from a GIF file and calculate total duration.

    Args:
        gif_path: Path to the GIF file
        max_width: Maximum width for the frames
        max_height: Maximum height for the frames

    Returns:
        A tuple of (frames, total_duration_ms) or None if GIF can't be loaded
    """
    try:
        gif = Image.open(gif_path)
        frames = []
        total_duration = 0
        frame_index = 0

        # Extract all frames from the GIF
        while True:
            try:
                gif.seek(frame_index)
            except EOFError:
                break

            # Get frame duration in milliseconds
            duration = gif.info.get('duration', 100)
            total_duration += duration

            # Convert frame to RGBA and resize
            frame = gif.convert('RGBA')
            frame.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Convert PIL image to pygame surface
            pygame_surface = pygame.image.fromstring(
                frame.tobytes(),
                frame.size,
                'RGBA'
            )
            frames.append(pygame_surface)
            frame_index += 1

        return frames, total_duration
    except Exception as e:
        print(f"Warning: Could not load GIF '{gif_path}': {e}")
        return None
