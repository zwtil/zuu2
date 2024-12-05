import os
import yaml

__all__ = ["extract_md_meta", "get_md_meta", "update_meta", "dump_meta"]


def extract_md_meta(md_content: str):
    """
    Extracts the metadata from the content of a Markdown file.

    Args:
        md_content (str): The content of the Markdown file.

    Returns:
        dict: The metadata dictionary extracted from the Markdown file.
    """

    if "---" not in md_content:
        return {}

    meta_start = md_content.index("---") + 3
    meta_end = md_content.index("---", meta_start)
    meta_str = md_content[meta_start:meta_end]


    meta_dict: dict = yaml.safe_load(meta_str)

    return meta_dict


def get_md_meta(md_file: str):
    """
    Retrieves the metadata from a Markdown file.

    Args:
        md_file (str): The path to the Markdown file.

    Returns:
        dict: The metadata dictionary extracted from the Markdown file.
    """

    with open(md_file, "r") as f:
        md_content = f.read()
        return extract_md_meta(md_content)


def append_meta(md_content: str, meta_dict: dict):
    """
    Appends the provided metadata dictionary to the Markdown content, either by adding a new metadata block or updating the existing one.

    Args:
        md_content (str): The Markdown content to append the metadata to.
        meta_dict (dict): The metadata dictionary to be appended.

    Returns:
        str: The updated Markdown content with the appended metadata.
    """
    

    if "---\n" not in md_content:
        return "---\n" + yaml.safe_dump(meta_dict) + "---\n" + md_content

    meta_start = md_content.index("---\n") + 4
    meta_end = md_content.index("---\n", meta_start)
    existing_meta_str = md_content[meta_start:meta_end]
    existing_meta_dict = yaml.safe_load(existing_meta_str)

    existing_meta_dict.update(meta_dict)
    updated_meta_str = yaml.safe_dump(existing_meta_dict, sort_keys=False)

    return md_content[:meta_start] + updated_meta_str + md_content[meta_end:]


def update_meta(md_file: str, meta_dict: dict):
    """
    Updates the metadata in a Markdown file by merging the existing metadata with the provided metadata dictionary.

    Args:
        md_file (str): The path to the Markdown file.
        meta_dict (dict): The metadata dictionary to be merged with the existing metadata.

    Returns:
        str: The updated Markdown content with the merged metadata.
    """

    if not os.path.exists(md_file):
        existingMeta = {}
    else:
        existingMeta = get_md_meta(md_file)
    existingMeta.update(meta_dict)

    with open(md_file, "r") as f:
        md_content = f.read()

    return append_meta(md_content, existingMeta)


def dump_meta(md_file: str, meta_dict: dict):
    """
    Dumps the provided metadata dictionary to a Markdown file.

    Args:
        md_file (str): The path to the Markdown file.
        meta_dict (dict): The metadata dictionary to be dumped.

    Returns:
        None
    """
    with open(md_file, "w") as f:
        f.write(update_meta(md_file, meta_dict))
