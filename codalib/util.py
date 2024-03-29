from datetime import datetime
import http.client
import json
import os
import tempfile
import time
import urllib.request
import urllib.error
import urllib.parse
import uuid

from lxml import etree

from . import bagatom
from .xsdatetime import xsDateTime_format

# Not really thrilled about duplicating these globals here -- maybe define them in coda.bagatom?
PREMIS_NAMESPACE = "info:lc/xmlns/premis-v2"
PREMIS = "{%s}" % PREMIS_NAMESPACE
PREMIS_NSMAP = {"premis": PREMIS_NAMESPACE}


def parseVocabularySources(jsonFilePath):
    choiceList = []
    jsonString = open(jsonFilePath, "r").read()
    jsonDict = json.loads(jsonString)
    terms = jsonDict["terms"]
    for term in terms:
        choiceList.append((term['name'], term['label']))
    return choiceList


class HEADREQUEST(urllib.request.Request):
    def get_method(self):
        return "HEAD"


class PUTREQUEST(urllib.request.Request):
    def get_method(self):
        return "PUT"


class DELETEREQUEST(urllib.request.Request):
    def get_method(self):
        return "DELETE"


def waitForURL(url, max_seconds=None):
    """
    Give it a URL.  Keep trying to get a HEAD request from it until it works.
    If it doesn't work, wait a while and try again
    """

    startTime = datetime.now()
    while True:
        response = None
        try:
            response = urllib.request.urlopen(HEADREQUEST(url))
        except urllib.error.URLError:
            pass
        if response is not None and isinstance(response, http.client.HTTPResponse):
            if response.getcode() == 200:
                # We're done, yay!
                return
        timeNow = datetime.now()
        timePassed = timeNow - startTime
        if max_seconds and max_seconds < timePassed.seconds:
            return
        print("%s: Waiting on URL %s for %s so far" % (str(timeNow), url, timePassed))
        time.sleep(30)


def doWaitWebRequest(url, method="GET", data=None, headers={}):
    """
    Same as doWebRequest, but with built in wait-looping
    """

    completed = False
    while not completed:
        completed = True
        try:
            response, content = doWebRequest(url, method, data, headers)
        except urllib.error.URLError:
            completed = False
            waitForURL(url)
    return response, content


def doWebRequest(url, method="GET", data=None, headers={}):
    """
    A urllib wrapper to mimic the functionality of http2lib, but with timeout support
    """

    # Initialize variables
    response = None
    content = None
    # Find condition that matches request
    if method == "HEAD":
        request = HEADREQUEST(url, data=data, headers=headers)
    elif method == "PUT":
        request = PUTREQUEST(url, data=data, headers=headers)
    elif method == "DELETE":
        request = DELETEREQUEST(url, headers=headers)
    elif method == "GET":
        request = urllib.request.Request(url, headers=headers)
    # POST?
    else:
        request = urllib.request.Request(url, data=data, headers=headers)
    response = urllib.request.urlopen(request)
    if response:
        content = response.read()
    return response, content


def sendPREMISEvent(webRoot, eventType, agentIdentifier, eventDetail,
                    eventOutcome, eventOutcomeDetail=None, linkObjectList=[],
                    eventDate=None, debug=False, eventIdentifier=None):
    """
    A function to format an event to be uploaded and send it to a particular CODA server
    in order to register it
    """

    atomID = uuid.uuid1().hex
    eventXML = createPREMISEventXML(
        eventType=eventType,
        agentIdentifier=agentIdentifier,
        eventDetail=eventDetail,
        eventOutcome=eventOutcome,
        outcomeDetail=eventOutcomeDetail,
        eventIdentifier=eventIdentifier,
        eventDate=eventDate,
        linkObjectList=linkObjectList
    )
    atomXML = bagatom.wrapAtom(eventXML, id=atomID, title=atomID)
    atomXMLText = b'<?xml version="1.0"?>\n%s' % etree.tostring(
        atomXML, pretty_print=True
    )
    if debug:
        print("Uploading XML to %s\n---\n%s\n---\n" % (webRoot, atomXMLText))
    response = None
    try:
        response, content = doWebRequest(webRoot, "POST", data=atomXMLText)
    except urllib.error.URLError:
        pass
    if not response:
        waitForURL(webRoot, 60)
        response, content = doWebRequest(webRoot, "POST", data=atomXMLText)
    if response.code != 201:
        if debug:
            tempdir = tempfile.gettempdir()
            tfPath = os.path.join(
                tempdir, "premis_upload_%s.html" % uuid.uuid1().hex
            )
            tf = open(tfPath, "wb")
            tf.write(content)
            tf.close()
            print(
                "Output from webserver available at %s. Response code %s" % (
                    tf.name, response.code
                )
            )
        raise Exception(
            "Error uploading PREMIS Event to %s. Response code is %s" % (
                webRoot, response.code
            )
        )
    return response, content


def createPREMISEventXML(eventType, agentIdentifier, eventDetail, eventOutcome,
                         outcomeDetail=None, eventIdentifier=None,
                         linkObjectList=[], eventDate=None):
    """
    Actually create our PREMIS Event XML
    """

    eventXML = etree.Element(PREMIS + "event", nsmap=PREMIS_NSMAP)
    eventIDXML = etree.SubElement(eventXML, PREMIS + "eventIdentifier")
    eventTypeXML = etree.SubElement(eventXML, PREMIS + "eventType")
    eventTypeXML.text = eventType
    eventIDTypeXML = etree.SubElement(
        eventIDXML, PREMIS + "eventIdentifierType"
    )
    eventIDTypeXML.text = \
        "http://purl.org/net/untl/vocabularies/identifier-qualifiers/#UUID"
    eventIDValueXML = etree.SubElement(
        eventIDXML, PREMIS + "eventIdentifierValue"
    )
    if eventIdentifier:
        eventIDValueXML.text = eventIdentifier
    else:
        eventIDValueXML.text = uuid.uuid4().hex
    eventDateTimeXML = etree.SubElement(eventXML, PREMIS + "eventDateTime")
    if eventDate is None:
        eventDateTimeXML.text = xsDateTime_format(datetime.utcnow())
    else:
        eventDateTimeXML.text = xsDateTime_format(eventDate)
    eventDetailXML = etree.SubElement(eventXML, PREMIS + "eventDetail")
    eventDetailXML.text = eventDetail
    eventOutcomeInfoXML = etree.SubElement(
        eventXML, PREMIS + "eventOutcomeInformation"
    )
    eventOutcomeXML = etree.SubElement(
        eventOutcomeInfoXML, PREMIS + "eventOutcome"
    )
    eventOutcomeXML.text = eventOutcome
    if outcomeDetail:
        eventOutcomeDetailXML = etree.SubElement(
            eventOutcomeInfoXML, PREMIS + "eventOutcomeDetail"
        )
        eventOutcomeDetailNoteXML = etree.SubElement(
            eventOutcomeDetailXML, PREMIS + "eventOutcomeDetailNote"
        )
        eventOutcomeDetailNoteXML.text = outcomeDetail
        # Assuming it's a list of 3-item tuples here [ ( identifier, type, role) ]
    linkAgentIDXML = etree.SubElement(
        eventXML, PREMIS + "linkingAgentIdentifier")
    linkAgentIDTypeXML = etree.SubElement(
        linkAgentIDXML, PREMIS + "linkingAgentIdentifierType"
    )
    linkAgentIDTypeXML.text = \
        "http://purl.org/net/untl/vocabularies/identifier-qualifiers/#URL"
    linkAgentIDValueXML = etree.SubElement(
        linkAgentIDXML, PREMIS + "linkingAgentIdentifierValue"
    )
    linkAgentIDValueXML.text = agentIdentifier
    linkAgentIDRoleXML = etree.SubElement(
        linkAgentIDXML, PREMIS + "linkingAgentRole"
    )
    linkAgentIDRoleXML.text = \
        "http://purl.org/net/untl/vocabularies/linkingAgentRoles/#executingProgram"
    for linkObject in linkObjectList:
        linkObjectIDXML = etree.SubElement(
            eventXML, PREMIS + "linkingObjectIdentifier"
        )
        linkObjectIDTypeXML = etree.SubElement(
            linkObjectIDXML, PREMIS + "linkingObjectIdentifierType"
        )
        linkObjectIDTypeXML.text = linkObject[1]
        linkObjectIDValueXML = etree.SubElement(
            linkObjectIDXML, PREMIS + "linkingObjectIdentifierValue"
        )
        linkObjectIDValueXML.text = linkObject[0]
        if linkObject[2]:
            linkObjectRoleXML = etree.SubElement(
                linkObjectIDXML, PREMIS + "linkingObjectRole"
            )
            linkObjectRoleXML.text = linkObject[2]
    return eventXML


def deleteQueue(destinationRoot, queueArk, debug=False):
    """
    Delete an entry from the queue
    """

    url = urllib.parse.urljoin(destinationRoot, "APP/queue/" + queueArk + "/")
    response, content = doWaitWebRequest(url, "DELETE")
    if response.getcode() != 200:
        raise Exception(
            "Error updating queue %s to url %s.  Response code is %s\n%s" %
            (queueArk, url, response.getcode(), content)
        )


def updateQueue(destinationRoot, queueDict, debug=False):
    """
    With a dictionary that represents a queue entry, update the queue entry with
    the values
    """

    attrDict = bagatom.AttrDict(queueDict)
    url = urllib.parse.urljoin(destinationRoot, "APP/queue/" + attrDict.ark + "/")
    queueXML = bagatom.queueEntryToXML(attrDict)
    urlID = os.path.join(destinationRoot, attrDict.ark)
    uploadXML = bagatom.wrapAtom(queueXML, id=urlID, title=attrDict.ark)
    uploadXMLText = b'<?xml version="1.0"?>\n' + etree.tostring(
        uploadXML, pretty_print=True
    )
    if debug:
        print("Sending XML to %s" % url)
        print(uploadXMLText)
    try:
        response, content = doWebRequest(url, "PUT", data=uploadXMLText)
    except urllib.error.URLError:
        # Sleep a few minutes then give it a second shot before dying
        time.sleep(300)
        response, content = doWebRequest(url, "PUT", data=uploadXMLText)
    if response.getcode() != 200:
        raise Exception(
            "Error updating queue %s to url %s.  Response code is %s\n%s" %
            (attrDict.ark, url, response.getcode(), content)
        )
