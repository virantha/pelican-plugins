"""
Better Figures & Images
------------------------

This plugin:

- Adds a style="width: ???px; height: auto;" to each image in the content
- Also adds the width of the contained image to any parent div.figures.
    - If RESPONSIVE_IMAGES == True, also adds style="max-width: 100%;"
- Corrects alt text: if alt == image filename, set alt = ''

TODO: Need to add a test.py for this plugin.

"""

from os import path, access, R_OK

from pelican import signals

from bs4 import BeautifulSoup
from PIL import Image

import logging
logger = logging.getLogger(__name__)

def content_object_init(instance):

    if instance._content is not None:
        content = instance._content
        soup = BeautifulSoup(content)

        if 'img' in content:
            for img in soup('img'):
                logger.debug('Better Fig. PATH: %s', instance.settings['PATH'])
                logger.debug('Better Fig. img.src: %s', img['src'])

                # Some exclusions
                if 'amazon' in img['src']:
                    continue
                if 'http' in img['src']:
                    continue

                if 'skip_better' in img['alt']:
                    img['alt'] = img['alt'].replace('skip_better', '')
                    continue

                img_path, img_filename = path.split(img['src'])

                logger.debug('Better Fig. img_path: %s', img_path)
                logger.debug('Better Fig. img_fname: %s', img_filename)

                # Strip off {filename}, |filename| or /static
                if img_path.startswith(('{filename}', '|filename|')):
                    img_path = img_path[10:]
                elif img_path.startswith('/images'):
                    #img_path = img_path[7:]
                    pass
                else:
                    logger.warning('Better Fig. Error: img_path should start with either {filename}, |filename| or /images')

                # Build the source image filename
                src = instance.settings['PATH'] + img_path + '/' + img_filename

                logger.debug('Better Fig. src: %s', src)
                if not (path.isfile(src) and access(src, R_OK)):
                    logger.error('Better Fig. Error: image not found: {}'.format(src))

                # Open the source image and query dimensions; build style string
                im = Image.open(src)
                width = im.size[0]
                height = im.size[1]
                extra_style = 'width: {}px; height: auto;'.format(im.size[0])

                img['width'] = width
                img['height'] = height

                if instance.settings['RESPONSIVE_IMAGES']:
                    extra_style += ' max-width: 100%;'

                if img.get('style'):
                    img['style'] += extra_style
                else:
                    img['style'] = extra_style

                if img['alt'] == img['src']:
                    img['alt'] = ''

                fig = img.find_parent('div', 'figure')
                if fig:
                    if fig.get('style'):
                        fig['style'] += extra_style
                    else:
                        fig['style'] = extra_style

        instance._content = soup.decode()


def register():
    signals.content_object_init.connect(content_object_init)
