import click
import json
from pathlib import Path
from PIL import UnidentifiedImageError, Image

from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

import torch
from transformers import pipeline

import concurrent.futures

console = Console()

def generate_caption(caption_model, path: str, max_tokens: int = 50):
    try:
        image = Image.open(path)
        caption = caption_model(image, max_new_tokens=max_tokens)
        return path, caption[0]["generated_text"]
    except UnidentifiedImageError as e:
        return path, f"Error: {str(e)}"
    except Exception as e:
        return path, f"Unexpected error: {str(e)}"

def output_caption(path: str, caption: str, output_format: str, is_first: bool, is_last: bool):
    if output_format == 'json':
        prefix = "[" if is_first else " "
        suffix = "," if not is_last else "]"
        console.print(prefix + json.dumps({"path": path, "caption": caption}) + suffix)
    else:
        panel = Panel(f"[bold]{Path(path).name}[/bold]\n\n{caption}", expand=False, border_style="cyan")
        console.print(panel)

@click.command()
@click.argument(
    "paths",
    type=click.Path(exists=True, dir_okay=True, allow_dash=True),
    nargs=-1,
    required=True,
)
@click.option("--output", type=click.Choice(['pretty', 'json']), default='pretty', help="Output format")
@click.option("--model", default="microsoft/git-base", help="Uses MSFT GIT-Base model for captioning of images")
@click.option("--max-tokens", default=50, help="Maximum number of tokens for the caption")
@click.option("--recursive", is_flag=True, help="Recursively process directories")
@click.option("--threads", default=1, help="Number of threads to use for processing")
def cli(paths: List[str], output: str, model: str, max_tokens: int, recursive: bool, threads: int):
    device = 0 if torch.cuda.is_available() else -1
    caption_model = pipeline("image-to-text", model=model, device=device)
    
    all_image_paths = []
    for path in paths:
        p = Path(path)
        if p.is_dir():
            if recursive:
                all_image_paths.extend([str(f) for f in p.rglob("*") if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.bmp')])
            else:
                all_image_paths.extend([str(f) for f in p.glob("*") if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.bmp')])
        else:
            all_image_paths.append(str(p))
    
    total_images = len(all_image_paths)
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Processing images...", total=total_images)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_path = {executor.submit(generate_caption, caption_model, path, max_tokens): path for path in all_image_paths}
            
            for i, future in enumerate(concurrent.futures.as_completed(future_to_path)):
                path, caption = future.result()
                output_caption(path, caption, output, i == 0, i == total_images - 1)
                progress.update(task, advance=1)

    console.print(f"\n[bold green]Processed {total_images} images successfully![/bold green]")

if __name__ == "__main__":
    cli()