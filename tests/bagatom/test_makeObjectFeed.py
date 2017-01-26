from lxml import etree
from codalib.bagatom import makeObjectFeed, ATOM_NAMESPACE as atom_ns
from mock import Mock


def test_simpleFeed():
    """
    Verify the return type of makeObjectFeed is an instance of etree._Element
    and check for link with rel=alternative
    """
    obj = Mock()
    obj.id = "0xDEADBEEF"
    obj.name = "0xDEADBEEF"
    obj.to = "Tove"
    obj.sender = "Jani"
    obj.heading = "Reminder"
    obj.title = "Reminder"
    obj.body = "Don't forget me this weekend!"
    objs = [obj, ]
    oxml = etree.XML("""<note>
        <to>Tove</to>
        <sender>Jani</sender>
        <heading>Reminder</heading>
        <title>Reminder</title>
        <body>Don't forget me this weekend!</body>
    </note>""")
    paginator = Mock()
    paginator.num_pages = 1
    paginator.page = 1
    paginator.page_range = (1,)
    paginator.count = 20
    page_return = Mock()
    page_return.object_list = objs
    page_return.next_page_number = Mock(return_value=1)
    page_return.has_next = Mock(return_value=False)
    page_return.previous_page_number = Mock(return_value=1)
    page_return.has_previous = Mock(return_value=False)
    paginator.page = Mock(return_value=page_return)
    dummy_obj2xml_func = Mock(return_value=oxml)
    feed_id = 'APP/bag/'
    title = 'Bag Feed'
    web_root = 'http://localhost:8787'

    feed = makeObjectFeed(paginator, dummy_obj2xml_func, feed_id, title, web_root)

    assert isinstance(feed, etree._Element)
    elements = feed.getroottree().xpath(
        '/a:feed//a:entry/a:link[@rel="alternate"]',
        namespaces={'a': atom_ns}
    )
    assert len(elements) == 1
    assert elements[0].attrib["type"] == "text/html"
