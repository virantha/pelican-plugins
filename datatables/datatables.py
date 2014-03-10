from pelican import signals
import re
import html5lib
from html5lib import sanitizer
from bs4 import BeautifulSoup


def getText(node, recursive = False):
    """Get all the text associated with this node.
       With recursive == True, all text from child nodes is retrieved."""
    L = ['']
    for n in node.childNodes:
        if n.nodeType in (node.TEXT_NODE, node.CDATA_SECTION_NODE):
            L.append(n.data)
        else:
            if not recursive:
                return None
        L.append(getText(n) )
    return ''.join(L)

def parse_for_tables(article_generator):
    #parser = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("dom"))
    parser = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("dom"),tokenizer=sanitizer.HTMLSanitizer)
    for article in article_generator.articles:
        if "<table" in article._content:
            soup = BeautifulSoup(article._content, 'html.parser')

            body = soup.find('body')
            assert body
            #css_head = soup.new_tag('link', rel="stylesheet")
            #<script type="text/javascript" charset="utf8" src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.2.min.js"></script>
            scr = soup.new_tag('script', type="text/javascript", charset="utf8", src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.2.min.js")
            body.append(scr)
            scr = soup.new_tag('script', type="text/javascript", charset="utf8", src="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js")
            body.append(scr)
            #css_head.setAttribute("type", "text/css")
            #css_head.setAttribute("href", "http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/css/jquery.dataTables.css")
            #head.appendChild(css_head)
            for table in soup.find_all('table'):
                print table.attrs
                if 'id' in table.attrs:
                    table_id = table.attrs['id']
                    scr = soup.new_tag('script')
                    scr.string = """
                           $(document).ready(function() {
                             $('#%s').dataTable();
                           } );""" % table_id
                    body.append(scr)
                    print ("TABLE FOUND!!!! %s" % (table_id))

            article._content = soup.decode()
    return

    if "[ref]" in article._content and "[/ref]" in article._content:
        content = article._content.replace("[ref]", "<x-simple-footnote>").replace("[/ref]", "</x-simple-footnote>")
        parser = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("dom"))
        dom = parser.parse(content)
        endnotes = []
        count = 0
        for footnote in dom.getElementsByTagName("x-simple-footnote"):
            pn = footnote
            leavealone = False
            while pn:
                if pn.nodeName in RAW_FOOTNOTE_CONTAINERS:
                    leavealone = True
                    break
                pn = pn.parentNode
            if leavealone:
                continue
            count += 1
            fnid = "sf-%s-%s" % (article.slug, count)
            fnbackid = "%s-back" % (fnid,)
            endnotes.append((footnote, fnid, fnbackid))
            number = dom.createElement("sup")
            number.setAttribute("id", fnbackid)
            numbera = dom.createElement("a")
            numbera.setAttribute("href", "#%s" % fnid)
            numbera.setAttribute("class", "simple-footnote")
            numbera.appendChild(dom.createTextNode(str(count)))
            txt = getText(footnote, recursive=True).replace("\n", " ")
            numbera.setAttribute("title", txt)
            number.appendChild(numbera)
            footnote.parentNode.insertBefore(number, footnote)
        if endnotes:
            ol = dom.createElement("ol")
            ol.setAttribute("class", "simple-footnotes")
            ol.appendChild(dom.createTextNode('Notes:'))
            for e, fnid, fnbackid in endnotes:
                li = dom.createElement("li")
                li.setAttribute("id", fnid)
                while e.firstChild:
                    li.appendChild(e.firstChild)
                backlink = dom.createElement("a")
                backlink.setAttribute("href", "#%s" % fnbackid)
                backlink.setAttribute("class", "simple-footnote-back")
                backlink.appendChild(dom.createTextNode(u'\u21a9'))
                li.appendChild(dom.createTextNode(" "))
                li.appendChild(backlink)
                ol.appendChild(li)
                e.parentNode.removeChild(e)
            dom.getElementsByTagName("body")[0].appendChild(ol)
            s = html5lib.serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False, quote_attr_values=True)
            output_generator = s.serialize(html5lib.treewalkers.getTreeWalker("dom")(dom.getElementsByTagName("body")[0]))
            article._content =  "".join(list(output_generator)).replace(
                "<x-simple-footnote>", "[ref]").replace("</x-simple-footnote>", "[/ref]").replace(
                "<body>", "").replace("</body>", "")
    if False:
        count = 0
        endnotes = []
        for f in footnotes:
            count += 1
            fnstr = '<a class="simple-footnote" name="%s-%s-back" href="#%s-%s"><sup>%s</a>' % (
                article.slug, count, article.slug, count, count)
            endstr = '<li id="%s-%s">%s <a href="#%s-%s-back">&uarr;</a></li>' % (
                article.slug, count, f[len("[ref]"):-len("[/ref]")], article.slug, count)
            content = content.replace(f, fnstr)
            endnotes.append(endstr)
        content += '<h4>Footnotes</h4><ol class="simple-footnotes">%s</ul>' % ("\n".join(endnotes),)
        article._content = content


def register():
    signals.article_generator_finalized.connect(parse_for_tables)

