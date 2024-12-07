import os
from PIL import Image
import numpy as np
import random
from moviepy.editor import VideoFileClip
from zuu.pkg.pillow import count_unique_colors

def make_thumbnail(
    video_path: str, sample_size: int = 5, avoid_single_color: bool = True
) -> Image:
    """
    Generate a thumbnail image from a video file.

    Args:
        video_path (str): The path to the video file.
        sample_size (int, optional): The number of random samples to choose. Defaults to 5.
        avoid_single_color (bool, optional): Whether to avoid generating thumbnails with a single color. Defaults to True.

    Returns:
        Image: The generated thumbnail image.

    Raises:
        None

    Notes:
        - This function uses the `moviepy` library to generate the thumbnail image.
        - The `sample_size` argument determines how many frames are randomly sampled to find the best one.
        - The `avoid_single_color` argument determines whether to avoid generating thumbnails with a single color.
        - The function returns an `Image` object representing the generated thumbnail.
    """
    with VideoFileClip(video_path) as clip:
        duration = clip.duration
        # Generate random sample timestamps
        random_timestamps = [random.uniform(0, duration) for _ in range(sample_size)]
        frames = []

        # Get frames at the sampled timestamps
        for timestamp in random_timestamps:
            frame = clip.get_frame(timestamp)
            image = Image.fromarray(frame)
            frames.append(image)

        if avoid_single_color:
            # Calculate color diversity for each frame
            color_diversities = [count_unique_colors(frame) for frame in frames]
            # Find the frame with the maximum number of colors
            best_frame_index = np.argmax(color_diversities)
            best_frame = frames[best_frame_index]
        else:
            best_frame = frames[0]

    return best_frame


def make_thumbnail_folder(
    path: str,
    supported_formats=[".mp4", ".mkv", ".mov", ".avi", ".webm"],
):
    """
    Generate thumbnails for all video files in a given folder.

    Args:
        path (str): The path to the folder containing video files.
        supported_formats (list of str, optional): A list of supported video file formats. Defaults to common video formats.

    Returns:
        None

    Notes:
        - Thumbnails are saved in the same directory as the videos, with the same filename and a '.jpg' extension.
    """
    if not os.path.isdir(path):
        raise ValueError("The provided path is not a directory.")

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        _, ext = os.path.splitext(filename)

        if ext.lower() in supported_formats:
            try:
                thumbnail = make_thumbnail(file_path)
                thumbnail_path = os.path.splitext(file_path)[0] + ".jpg"
                thumbnail.save(thumbnail_path, "JPEG")
                print(f"Thumbnail created for {filename} at {thumbnail_path}")
            except Exception as e:
                print(f"Failed to create thumbnail for {filename}: {e}")