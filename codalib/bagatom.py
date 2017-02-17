import os
import urllib
from datetime import datetime

from lxml import etree

from . import anvl, APP_AUTHOR
from codalib.xsdatetime import xsDateTime_format, localize_datetime

TIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"
DATE_FORMAT_STRING = "%Y-%m-%d"
BAG_NAMESPACE = "http://digital2.library.unt.edu/coda/bagxml/"
BAG = "{%s}" % BAG_NAMESPACE
BAG_NSMAP = {"bag": BAG_NAMESPACE}
ATOM_NAMESPACE = "http://www.w3.org/2005/Atom"
ATOM = "{%s}" % ATOM_NAMESPACE
ATOM_NSMAP = {None: ATOM_NAMESPACE}
QXML_NAMESPACE = "http://digital2.library.unt.edu/coda/queuexml/"
QXML = "{%s}" % QXML_NAMESPACE
QXML_NSMAP = {None: QXML_NAMESPACE}
NODE_NAMESPACE = "http://digital2.library.unt.edu/coda/nodexml/"
NODE = "{%s}" % NODE_NAMESPACE
NODE_NSMAP = {"node": NODE_NAMESPACE}

DEFAULT_ARK_NAAN = 67531


def wrapAtom(xml, id, title, author=None, updated=None, author_uri=None,
             alt=None, alt_type="text/html"):
    """
    Create an Atom entry tag and embed the passed XML within it
    """

    entryTag = etree.Element(ATOM + "entry", nsmap=ATOM_NSMAP)
    titleTag = etree.SubElement(entryTag, ATOM + "title")
    titleTag.text = title
    idTag = etree.SubElement(entryTag, ATOM + "id")
    idTag.text = id
    updatedTag = etree.SubElement(entryTag, ATOM + "updated")

    if alt:
        etree.SubElement(
            entryTag,
            ATOM + "link",
            rel='alternate',
            href=alt,
            type=alt_type)

    if updated is not None:
        # If updated is a naive datetime, set its timezone to the local one
        # So the xs:datetime value will include an explicit offset
        if updated.tzinfo is None:
            updated = localize_datetime(updated)
        updatedTag.text = xsDateTime_format(updated)
    else:
        updatedTag.text = xsDateTime_format(localize_datetime(datetime.now()))
    if author or author_uri:
        authorTag = etree.SubElement(entryTag, ATOM + "author")
        if author:
            nameTag = etree.SubElement(authorTag, ATOM + "name")
            nameTag.text = author
        if author_uri:
            nameUriTag = etree.SubElement(authorTag, ATOM + "uri")
            nameUriTag.text = author_uri
    contentTag = etree.SubElement(entryTag, ATOM + "content")
    contentTag.set("type", "application/xml")
    contentTag.append(xml)
    return entryTag


def getOxum(dataPath):
    """
    Calculate the oxum for a given path
    """

    fileCount = 0L
    fileSizeTotal = 0L
    for root, dirs, files in os.walk(dataPath):
        for fileName in files:
            fullName = os.path.join(root, fileName)
            stats = os.stat(fullName)
            fileSizeTotal += stats.st_size
            fileCount += 1
    return "%s.%s" % (fileSizeTotal, fileCount)


def getBagTags(bagInfoPath):
    """
    get bag tags
    """

    try:
        bagInfoString = open(bagInfoPath, "r").read().decode('utf-8')
    except UnicodeDecodeError:
        bagInfoString = open(bagInfoPath, "r").read().decode('iso-8859-1')
    bagTags = anvl.readANVLString(bagInfoString)
    return bagTags


def bagToXML(bagPath, ark_naan=None):
    """
    Given a path to a bag, read stuff about it and make an XML file
    """
    # This is so .DEFAULT_ARK_NAAN can be modified
    # at runtime.
    if ark_naan is None:
        ark_naan = DEFAULT_ARK_NAAN
    bagInfoPath = os.path.join(bagPath, "bag-info.txt")
    bagTags = getBagTags(bagInfoPath)
    if 'Payload-Oxum' not in bagTags:
        bagTags['Payload-Oxum'] = getOxum(os.path.join(bagPath, "data"))
    oxumParts = bagTags['Payload-Oxum'].split(".", 1)
    bagName = "ark:/%d/%s" % (ark_naan, os.path.split(bagPath)[1])
    bagSize = oxumParts[0]
    bagFileCount = oxumParts[1]
    bagitString = open(os.path.join(bagPath, "bagit.txt"), "r").read()
    bagitLines = bagitString.split("\n")
    versionLine = bagitLines[0].strip()
    bagVersion = versionLine.split(None, 1)[1]
    bagXML = etree.Element(BAG + "codaXML", nsmap=BAG_NSMAP)
    name = etree.SubElement(bagXML, BAG + "name")
    name.text = bagName
    fileCount = etree.SubElement(bagXML, BAG + "fileCount")
    fileCount.text = bagFileCount
    payLoadSize = etree.SubElement(bagXML, BAG + "payloadSize")
    payLoadSize.text = bagSize
    bagitVersion = etree.SubElement(bagXML, BAG + "bagitVersion")
    bagitVersion.text = bagVersion
    etree.SubElement(bagXML, BAG + "lastStatus")
    etree.SubElement(bagXML, BAG + "lastVerified")
    if 'Bagging-Date' in bagTags:
        baggingDate = etree.SubElement(bagXML, BAG + "baggingDate")
        baggingDate.text = bagTags['Bagging-Date']
    bagInfo = etree.SubElement(bagXML, BAG + "bagInfo")
    for tag, content in bagTags.items():
        item = etree.SubElement(bagInfo, BAG + "item")
        itemName = etree.SubElement(item, BAG + "name")
        itemName.text = tag
        itemBody = etree.SubElement(item, BAG + "body")
        itemBody.text = content
    return bagXML, bagName


def getValueByName(node, name):
    """
    A helper function to pull the values out of those annoying namespace
    prefixed tags
    """

    try:
        value = node.xpath("*[local-name() = '%s']" % name)[0].text.strip()
    except:
        return None
    return value


def getNodeByName(node, name):
    """
    Get the first child node matching a given local name
    """

    if node is None:
        raise Exception(
            "Cannot search for a child '%s' in a None object" % (name,)
        )
    if not name:
        raise Exception("Unspecified name to find node for.")
    try:
        childNode = node.xpath("*[local-name() = '%s']" % name)[0]
    except:
        return None
    return childNode


def getNodesByName(parent, name):
    """
    Return a list of all of the child nodes matching a given local name
    """

    try:
        childNodes = parent.xpath("*[local-name() = '%s']" % name)
    except:
        return []
    return childNodes


def getNodeByNameChain(node, chain_list):
    """
    Walk down a chain of node names and get the nodes they represent
    e.g. [ "entry", "content", "bag", "fileCount" ]
    """

    working_list = chain_list[:]
    working_list.reverse()
    current_node = node
    while len(working_list):
        current_name = working_list.pop()
        child_node = getNodeByName(current_node, current_name)
        if child_node is None:
            raise Exception("Unable to find child node %s" % current_name)
        current_node = child_node
    return current_node


def nodeToXML(nodeObject):
    """
    Take a Django node object from our CODA store and make an XML
    representation
    """

    xmlRoot = etree.Element(NODE + "node", nsmap=NODE_NSMAP)
    nameNode = etree.SubElement(xmlRoot, NODE + "name")
    nameNode.text = nodeObject.node_name
    urlNode = etree.SubElement(xmlRoot, NODE + "url")
    urlNode.text = nodeObject.node_url
    pathNode = etree.SubElement(xmlRoot, NODE + "path")
    pathNode.text = nodeObject.node_path
    capNode = etree.SubElement(xmlRoot, NODE + "capacity")
    capNode.text = str(nodeObject.node_capacity)
    sizeNode = etree.SubElement(xmlRoot, NODE + "size")
    sizeNode.text = str(nodeObject.node_size)
    if nodeObject.last_checked:
        checkedNode = etree.SubElement(xmlRoot, NODE + "lastChecked")
        checkedNode.text = nodeObject.last_checked.strftime(TIME_FORMAT_STRING)
    return xmlRoot


def queueEntryToXML(queueEntry):
    """
    Turn an instance of a QueueEntry model into an xml data format
    """

    xmlRoot = etree.Element(QXML + "queueEntry", nsmap=QXML_NSMAP)
    arkTag = etree.SubElement(xmlRoot, QXML + "ark")
    arkTag.text = queueEntry.ark
    oxumTag = etree.SubElement(xmlRoot, QXML + "oxum")
    oxumTag.text = queueEntry.oxum
    urlListLinkTag = etree.SubElement(xmlRoot, QXML + "urlListLink")
    urlListLinkTag.text = queueEntry.url_list
    statusTag = etree.SubElement(xmlRoot, QXML + "status")
    statusTag.text = queueEntry.status
    if hasattr(queueEntry, "harvest_start") and queueEntry.harvest_start:
        startTag = etree.SubElement(xmlRoot, QXML + "start")
        if isinstance(queueEntry.harvest_start, basestring):
            startTag.text = queueEntry.harvest_start
        else:
            startTag.text = queueEntry.harvest_start.strftime(
                TIME_FORMAT_STRING
            )
    if hasattr(queueEntry, "harvest_end") and queueEntry.harvest_end:
        endTag = etree.SubElement(xmlRoot, QXML + "end")
        if isinstance(queueEntry.harvest_end, basestring):
            endTag.text = queueEntry.harvest_end
        else:
            endTag.text = queueEntry.harvest_end.strftime(TIME_FORMAT_STRING)
    positionTag = etree.SubElement(xmlRoot, QXML + "position")
    positionTag.text = str(queueEntry.queue_position)
    return xmlRoot


class AttrDict(dict):
    """
    A class to give us fielded access from a dictionary...how hacky, but lets
    us reuse some code
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self


def makeObjectFeed(
        paginator, objectToXMLFunction, feedId, title, webRoot,
        idAttr="id", nameAttr="name", dateAttr=None, request=None, page=1,
        count=20, author=APP_AUTHOR):
    """
    Take a list of some kind of object, a conversion function, an id and a
    title Return XML representing an ATOM feed
    """

    listSize = paginator.count
    if listSize:
        object_list = paginator.page(page).object_list
    else:
        object_list = []
    count = int(count)
    originalId = feedId
    idParts = feedId.split("?", 1)
    if len(idParts) == 2:
        feedId = idParts[0]
    if request:
        GETStruct = request.GET
    else:
        GETStruct = False
    feedTag = etree.Element(ATOM + "feed", nsmap=ATOM_NSMAP)
    # The id tag is very similar to the 'self' link
    idTag = etree.SubElement(feedTag, ATOM + "id")
    idTag.text = "%s/%s" % (webRoot, feedId)
    # The title is passed in from the calling function
    titleTag = etree.SubElement(feedTag, ATOM + "title")
    titleTag.text = title
    # The author is passed in from the calling function and required to be valid ATOM
    if author:
        authorTag = etree.SubElement(feedTag, ATOM + "author")
        nameTag = etree.SubElement(authorTag, ATOM + "name")
        urlTag = etree.SubElement(authorTag, ATOM + "uri")
        nameTag.text = author.get('name', 'UNT')
        urlTag.text = author.get('uri', 'http://library.unt.edu/')
    # The updated tag is a
    updatedTag = etree.SubElement(feedTag, ATOM + "updated")
    updatedTag.text = xsDateTime_format(localize_datetime(datetime.now()))
    # We will always show the link to the current 'self' page
    linkTag = etree.SubElement(feedTag, ATOM + "link")
    linkTag.set("rel", "self")
    if not request or not request.META['QUERY_STRING']:
        linkTag.set("href", "%s/%s" % (webRoot, feedId))
    else:
        linkTag.set(
            "href", "%s/%s?%s" % (
                webRoot, feedId, urllib.urlencode(request.GET, doseq=True)
            )
        )
    # We always have a last page
    endLink = etree.SubElement(feedTag, ATOM + "link")
    endLink.set("rel", "last")
    if GETStruct:
        endLinkGS = GETStruct.copy()
    else:
        endLinkGS = {}
    endLinkGS.update({"page": paginator.num_pages})
    endLink.set(
        "href", "%s/%s?%s" % (
            webRoot, feedId, urllib.urlencode(endLinkGS, doseq=True)
        )
    )
    # We always have a first page
    startLink = etree.SubElement(feedTag, ATOM + "link")
    startLink.set("rel", "first")
    if GETStruct:
        startLinkGS = GETStruct.copy()
    else:
        startLinkGS = {}
    startLinkGS.update({"page": paginator.page_range[0]})
    startLink.set(
        "href", "%s/%s?%s" % (
            webRoot, feedId, urllib.urlencode(startLinkGS, doseq=True)
        )
    )
    # Potentially there is a previous page, list it's details
    if paginator.page(page).has_previous():
        prevLink = etree.SubElement(feedTag, ATOM + "link")
        prevLink.set("rel", "previous")
        if GETStruct:
            prevLinkGS = GETStruct.copy()
        else:
            prevLinkGS = {}
        prevLinkGS.update(
            {"page": paginator.page(page).previous_page_number()}
        )
        prevLinkText = "%s/%s?%s" % (
            webRoot, feedId, urllib.urlencode(prevLinkGS, doseq=True)
        )
        prevLink.set("href", prevLinkText)
    # Potentially there is a next page, fill in it's details
    if paginator.page(page).has_next():
        nextLink = etree.SubElement(feedTag, ATOM + "link")
        nextLink.set("rel", "next")
        if GETStruct:
            nextLinkGS = GETStruct.copy()
        else:
            nextLinkGS = {}
        nextLinkGS.update({"page": paginator.page(page).next_page_number()})
        nextLinkText = "%s/%s?%s" % (
            webRoot, feedId, urllib.urlencode(nextLinkGS, doseq=True)
        )
        nextLink.set("href", nextLinkText)
    for o in object_list:
        objectXML = objectToXMLFunction(o)
        if dateAttr:
            dateStamp = getattr(o, dateAttr)
        else:
            dateStamp = None
        althref = feedId.strip('/').split('/')[-1]
        althref = '%s/%s/%s/' % (
            webRoot, althref, getattr(o, idAttr)
        )
        objectEntry = wrapAtom(
            xml=objectXML,
            id='%s/%s%s/' % (webRoot, originalId, getattr(o, idAttr)),
            title=getattr(o, nameAttr),
            updated=dateStamp,
            alt=althref
        )
        feedTag.append(objectEntry)
    return feedTag


def makeServiceDocXML(title, collections):
    """
    Make an ATOM service doc here. The 'collections' parameter is a list of
    dictionaries, with the keys of 'title', 'accept' and 'categories'
    being valid
    """

    serviceTag = etree.Element("service")
    workspaceTag = etree.SubElement(serviceTag, "workspace")
    titleTag = etree.SubElement(workspaceTag, ATOM + "title", nsmap=ATOM_NSMAP)
    titleTag.text = title
    for collection in collections:
        collectionTag = etree.SubElement(workspaceTag, "collection")
        if 'href' in collection:
            collectionTag.set("href", collection['href'])
        if 'title' in collection:
            colTitleTag = etree.SubElement(
                collectionTag, ATOM + "title", nsmap=ATOM_NSMAP
            )
            colTitleTag.text = collection['title']
        if 'accept' in collection:
            acceptTag = etree.SubElement(collectionTag, "accept")
            acceptTag.text = collection['accept']
    return serviceTag


def addObjectFromXML(xmlObject, XMLToObjectFunc,
                     topLevelName, idKey, updateList):
    """
    Handle adding or updating the Queue.  Based on XML input.
    """

    # Get the current object to update
    contentElement = getNodeByName(xmlObject, "content")
    objectNode = getNodeByName(contentElement, topLevelName)
    dupObjects = None
    newObject = XMLToObjectFunc(objectNode)
    try:
        kwargs = {idKey: getattr(newObject, idKey)}
        dupObjects = type(newObject).objects.filter(**kwargs)
    except type(newObject).DoesNotExist:
        pass
    if dupObjects and dupObjects.count() > 1:
        raise Exception(
            "Duplicate object with identifier %s" % getattr(newObject, idKey)
        )
    newObject.save()
    return newObject


def updateObjectFromXML(xml_doc, obj, mapping):
    """
    Handle updating an object.  Based on XML input.
    """
    nsmap = None
    if isinstance(mapping, dict):
        # The special key @namespaces is used to pass
        # namespaces and prefix mappings for xpath selectors.
        # e.g. {'x': 'http://example.com/namespace'}
        if '@namespaces' in mapping:
            nsmap = mapping['@namespaces']
    else:
        raise TypeError('Tag-to-property map must be a dict.')
    # Iterate over the keys of the translation dictionary from event objects
    # to xml objects, so we can update the fields with the new information
    for k, v in mapping.items():
        if k.startswith('@'):
            continue
        selected_text = None
        if isinstance(v, basestring):
            selector = v
        elif isinstance(v, list):
            selector = '/'.join(v)
        else:
            raise TypeError(
                'Invalid tag-to-property mapping dict: '
                'values must be strings or lists, not %s.' % (type(v),)
            )
        try:
            selected_text = xml_doc.xpath(selector, namespaces=nsmap)
            if isinstance(selected_text, list):
                selected_text = selected_text[0]
            selected_text = selected_text.text
            setattr(obj, k, selected_text)
        except IndexError:
            # Assume the value is missing. It's also possible that the
            # given selector is valid but wrong, but the more common
            # case is that the element is missing. To be consistent with
            # the prior implementation, empty resultsets just mean empty
            # attributes.
            continue
    return obj
