import os
from ..common.markdownProp import dump_meta

def resolve_template_type(string: str):
    if os.sep in string:
        extension = string.split(os.sep)[-1].split(".")[-1]
    else:
        extension = string.split(".")[-1]

    match extension:
        case "html":
            return "html"
        case "md":
            return "markdown"
        case "tex":
            return "latex"
        case "pdf":
            return "latex"
        case "docx":
            return "docx"
        case "odt":
            return "odt"
        case "rtf":
            return "rtf"
        case "txt":
            return "plain"
        case "html":
            return "html"
        case "epub":
            return "epub"
        case "epub3":
            return "epub3"
        case "odt":
            return "odt"
        case "docx":
            return "docx"
        case "pptx":
            return "pptx"
        case "ppt":
            return "ppt"
        case "odp":
            return "odp"
        case "ods":
            return "ods"

PANDOC_DICT_TEMPLATE = 'pandoc "{input_md}" -o "{output_path}" -f {input_type} -t {output_type} --template="{template}" {args}'

def pandoc_run(
    data : dict,
    template_path : str,
    output_path : str = "output",
    delete_temporary : bool = True,
    meta_path : str = "input.md"
):
    """
    Runs the Pandoc command to convert a Markdown file to a specified output format.
    """
    if os.sep in output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    dump_meta(meta_path, data)
    out_type = resolve_template_type(template_path)

    cmd = PANDOC_DICT_TEMPLATE.format(
        input_md=meta_path,
        output_path=output_path,
        input_type=resolve_template_type("input.md"),
        output_type=out_type,
        template=template_path,
        args=" ".join(data.get("args", []))
    )

    os.system(cmd)

    if delete_temporary:
        os.remove("input.md")

    