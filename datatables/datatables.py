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
from pelican import signals
import re
from bs4 import BeautifulSoup



def parse_for_tables(article_generator):
    for article in article_generator.articles:
        if "<table" in article._content:
            soup = BeautifulSoup(article._content, 'html.parser')

            body = soup.find('body')
            assert body
            scr = soup.new_tag('script', type="text/javascript", charset="utf8", src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.2.min.js")
            body.append(scr)
            scr = soup.new_tag('script', type="text/javascript", charset="utf8", src="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js")
            body.append(scr)
            for table in soup.find_all('table'):
                #print table.attrs
                if 'id' in table.attrs:
                    table.attrs['class'] = table.attrs.get('class') + ['pretty']
                    table_id = table.attrs['id']
                    scr = soup.new_tag('script')
                    scr.string = """
                           $(document).ready(function() {
                             $('#%s').dataTable( {
                                "sPaginationType": "full_numbers" ,
                                "sDom": "rtipf",
                                "iDisplayLength": 25,
                                "oLanguage": {
                                    "oPaginate": {
                                        "sNext": ">",
                                        "sPrevious": "<",
                                        "sFirst": "<<",
                                        "sLast": ">>"
                                    }
                                }
                             });
                           } );""" % table_id
                    body.append(scr)

            article._content = soup.decode()
    return


def register():
    signals.article_generator_finalized.connect(parse_for_tables)

