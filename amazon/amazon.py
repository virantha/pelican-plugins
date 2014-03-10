# Copyright 2014 Virantha Ekanayake All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Amazon Affiliate Link Inserter
==============================

This Pelican plugin lets you insert amazon affiliate links using the following two syntaxes:

    .. amazon:: ASIN image A really cool item

    .. amazon:: ASIN text A really cool item

    [amazon ASIN A really cool item]
"""
from __future__ import unicode_literals

from docutils import nodes
from docutils.parsers.rst import directives, Directive
from logging import error

from pelican import signals
import re

class Amazon(Directive):
    required_arguments = 3
    has_content= False
    final_argument_whitespace= True

    def run(self):
        error_text = "Amazon directive: "
        params = {}
        params['asin'] = self.arguments[0].strip()
        params['link_type'] = self.arguments[1].strip()
        if params['link_type'] not in ['image', 'text']: 
            error(error_text + '2nd argument must be image or text')

        params['text'] = self.arguments[2].strip()

        link_type = params['link_type']
        if link_type == 'text':
            myhtml = '<a href="http://www.amazon.com/gp/product/%(asin)s?ie=UTF8&linkCode=as2&camp=1634&tag=virantha-20">%(text)s</a>' % (params)
        elif link_type == 'image':
            myhtml = '<div><a href="http://www.amazon.com/gp/product/%(asin)s/ref=as_li_tf_il?ie=UTF8&camp=1789&creative=9325&creativeASIN=%(asin)s&linkCode=am2&tag=virantha-20&"><img border="0" width="110" src="http://ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN=%(asin)s&Format=_SL110_&ID=AsinImage&MarketPlace=US&ServiceVersion=20070822&WS=1&tag=virantha-20" style="vertical-align: middle;"/>%(text)s</a></div>' % params

        return [nodes.raw('', myhtml, format='html')]

def parse_for_amazon(article_generator):
    for article in article_generator.articles:
        mAmzn = re.compile(r"""\[amazon (?P<asin>[\w\d]+) (?P<text>[\w\d\s\-\,\.\(\)\!\'\_\/]+)\]""")
        myhtml = '<a href="http://www.amazon.com/gp/product/\g<asin>?ie=UTF8&linkCode=as2&camp=1634&tag=virantha-20">\g<text></a>'
        article._content = mAmzn.sub(myhtml, article._content)


def register():
    directives.register_directive('amazon', Amazon)
    signals.article_generator_finalized.connect(parse_for_amazon)
