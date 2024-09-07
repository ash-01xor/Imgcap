# imgcap


[![PyPI](https://img.shields.io/pypi/v/imgcap.svg)](https://pypi.org/project/imgcap/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ash-01xor/imgcap/blob/main/LICENSE)

A CLI to generate captions for images using the [GiT](https://huggingface.co/docs/transformers/en/model_doc/git) model from MSFT


### Install

Install ```imgcap``` in your system using:

 ```pip install imgcap```

The model size is of 707MB and once initially downloaded, it will be stored in the ```~/.cache/huggingface/hub/```.

### Usage

Run the CLI tool as follows

```
imgcap [OPTIONS] PATHS.. 
```

#### Options

-   ```--output [pretty|json]```: Specify the output format (default: pretty).
-    ```--max-tokens INTEGER```: Maximum number of tokens in the generated caption (default: 50).
-    ```--recursive```: Recursively process directories to find images.
-    ```--threads INTEGER```: Number of threads to use for processing (default: 1)


### Example commands

- Generate captions for a single image:
```
imgcap ./path/to/image.jpg --output pretty
```

- Generate captions for all images in a directory:
```
imgcap ./path/to/directory --recursive --output json
```

- Use multiple threads for faster processing:
```
imgcap ./images --threads 4
```