# pyicer

Simple decompress ICER-image using libicer

### build
Please note that submodule code is used
```commandline
git clone --recurse-submodules https://github.com/baskiton/pyicer.git
```

## Example
```python
from PIL import Image
import pyicer

fn = 'image.icer'
data = open(fn, 'rb').read()
rgb = pyicer.decompress(data, stages=4, segments=1, filter='A', color=1)
img = Image.fromarray(rgb)
img.save('image.png')
```
