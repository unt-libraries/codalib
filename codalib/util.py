try:
    # the json module was included in the stdlib in python 2.6
    # http://docs.python.org/library/json.html
    import json
except ImportError:
    # simplejson 2.0.9 is available for python 2.4+
    # http://pypi.python.org/pypi/simplejson/2.0.9
    # simplejson 1.7.3 is available for python 2.3+
    # http://pypi.python.org/pypi/simplejson/1.7.3
    import simplejson as json
from lxml import etree
import uuid
from datetime import datetime, tzinfo, timedelta
from . import bagatom
import urllib2
import urlparse
import sys
import tempfile
import os
import time
import subprocess

# not really thrilled about duplicating these globals here -- maybe define them in coda.bagatom?
PREMIS_NAMESPACE = "info:lc/xmlns/premis-v2"
PREMIS = "{%s}" % PREMIS_NAMESPACE
PREMIS_NSMAP = {"premis": PREMIS_NAMESPACE}
svn_version_path = "/usr/bin/svnversion"

# constants for time parsing/formatting
XSDT_FMT = "%Y-%m-%dT%H:%M:%S" # this is a stub
XSDT_TZ_OFFSET = 19 # this should never change

class InvalidXSDateTime(Exception):
    pass


class XSDateTimezone(tzinfo):
    """ 
    Concrete subclass of tzinfo for making sense of timezone offsets.
    Not really worried about localization here, just +/-HHMM
    """

    def __init__(self, hours=0, minutes=0, sign=1):
        self.minutes = hours*60+minutes
        self.minutes *= sign

    def utcoffset(self, dt):
        return timedelta(minutes=self.minutes)

    def dst(self, dt):
        return timedelta(0)

def xsDateTime_parse(xdt_str):
    """
    Parses xsDateTime strings of form 2017-01-27T14:58:00+0600, etc.
    Returns datetime with tzinfo, if offset included.
    """


    try:
        # this won't parse the offset (or other tzinfo)
        naive_dt = datetime.strptime(xdt_str[0:XSDT_TZ_OFFSET], XSDT_FMT)
    except:
        raise InvalidXSDateTime("Malformed date/time ('%s')." % (xdt_str, ))
    naive_len = XSDT_TZ_OFFSET
    offset_len = len(xdt_str) - naive_len
    offset_str = xdt_str[-offset_len:]
    offset_hourse = None
    offset_minutes = None
    offset_sign = 1
    parsed = None
    if not offset_len:
        parsed = naive_dt
    elif offset_len is 6: # +0000
        if offset_str[0] not in "+-":
            raise InvalidXSDateTime("Malformed offset (missing sign).")
        elif offset_str[0] is '-':
            offset_sign = -1
        try:
            offset_hours = int(offset_str[1:3])
        except:
            raise InvalidXSDateTime("Malformed offset (invalid hours '%s')"
                % (offset_str[1:3], )
            )
        if offset_str[3] is not ':':
            raise InvalidXSDateTime("Colon missing in offset.")
        try:
            offset_minutes = int(offset_str[4:6])
        except:
            raise InvalidXSDateTime("Malformed offset (invalid minutes '%s')"
                % (offset_str[4:6], )
            )
        offset = offset_hours*60.0+offset_minutes
        offset *= offset_sign
        timezone = XSDateTimezone(offset_hours, offset_minutes, offset_sign)
        parsed = naive_dt.replace(tzinfo=timezone)
    elif offset_len is 1: # Z
        if offset_str is 'Z':
            parsed = naive_dt.replace(tzinfo=XSDateTimezone())
        else:
            raise InvaildXSDateTime("Unrecognized timezone identifier '%s'." %
                (offset_str, )
            )
    else:
        raise InvalidXSDateTime("Malformed offset '%s'." % (offset_str, ))
    return parsed

def xsDateTime_format(xdt):
    xdt_str = xdt.strftime(XSDT_FMT)
    offset = xdt.utcoffset()
    if offset is None:
        return xdt_str
    offset_hours = offset.days*24+offset.seconds/(60*60)
    offset_minutes = (offset.seconds % (60*60))/60
    xdt_str += "{:+03d}:{:02d}".format(offset_hours, offset_minutes)
    return xdt_str


def parseVocabularySources(jsonFilePath):
    choiceList = []
    jsonString = open(jsonFilePath, "r").read()
    jsonDict = json.loads(jsonString)
    terms = jsonDict["terms"]
    for term in terms:
        choiceList.append((term['name'], term['label']))
    return choiceList


class HEADREQUEST(urllib2.Request):
    def get_method(self):
        return "HEAD"


class PUTREQUEST(urllib2.Request):
    def get_method(self):
        return "PUT"


class DELETEREQUEST(urllib2.Request):
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
            response = urllib2.urlopen(HEADREQUEST(url))
        except urllib2.URLError:
            pass
        if response is not None and isinstance(response, urllib2.addinfourl):
            if response.getcode() == 200:
                # we're done, yay!
                return
        timeNow = datetime.now()
        timePassed = timeNow - startTime
        if max_seconds and max_seconds < timePassed.seconds:
            return
        print("Waiting on URL %s for %s so far" % (url, timePassed))
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
        except urllib2.URLError:
            completed = False
            waitForURL(url)
    return response, content


def doWebRequest(url, method="GET", data=None, headers={}):
    """
    A urllib2 wrapper to mimic the functionality of http2lib, but with timeout support
    """

    # initialize variables
    response = None
    content = None
    # find condition that matches request
    if method == "HEAD":
        request = HEADREQUEST(url, data=data, headers=headers)
    elif method == "PUT":
        request = PUTREQUEST(url, data=data, headers=headers)
    elif method == "DELETE":
        request = DELETEREQUEST(url, headers=headers)
    elif method == "GET":
        request = urllib2.Request(url, headers=headers)
    # POST?
    else:
        request = urllib2.Request(url, data=data, headers=headers)
    response = urllib2.urlopen(request)
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
    atomXMLText = '<?xml version="1.0"?>\n%s' % etree.tostring(
        atomXML, pretty_print=True
    )
    if debug:
        print "Uploading XML to %s\n---\n%s\n---\n" % (webRoot, atomXMLText)
    response = None
    try:
        response, content = doWebRequest(webRoot, "POST", data=atomXMLText)
    except urllib2.URLError:
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
            tf = open(tfPath, "w")
            tf.write(content)
            tf.close()
            sys.stderr.write(
                "Output from webserver available at %s. Response code %s" % (
                    tf.name, response.code
                )
            )
        raise Exception(
            "Error uploading PREMIS Event to %s. Response code is %s" % (
                webRoot, response.code
            )
        )
    return (response, content)


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
        etree.SubElement(eventOutcomeDetailXML, 
                PREMIS + "eventOutcomeDetailNote").text = outcomeDetail
        # assuming it's a list of 3-item tuples here [ ( identifier, type, role) ]
    linkAgentIDXML = etree.SubElement(
        eventXML, PREMIS + "linkingAgentIdentifier"
    )
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


def get_svn_revision(path=None):

    if not path:
        path = os.path.dirname(sys.argv[0])
    path = os.path.abspath(path)
    exec_list = [svn_version_path, path]
    proc = subprocess.Popen(exec_list, stdout=subprocess.PIPE)
    out, errs = proc.communicate()
    return out.strip()


def deleteQueue(destinationRoot, queueArk, debug=False):
    """
    Delete an entry from the queue
    """

    url = urlparse.urljoin(destinationRoot, "APP/queue/" + queueArk + "/")
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
    url = urlparse.urljoin(destinationRoot, "APP/queue/" + attrDict.ark + "/")
    queueXML = bagatom.queueEntryToXML(attrDict)
    urlID = os.path.join(destinationRoot, attrDict.ark)
    uploadXML = bagatom.wrapAtom(queueXML, id=urlID, title=attrDict.ark)
    uploadXMLText = '<?xml version="1.0"?>\n' + etree.tostring(
        uploadXML, pretty_print=True
    )
    if debug:
        print "Sending XML to %s" % url
        print uploadXMLText
    try:
        response, content = doWebRequest(url, "PUT", data=uploadXMLText)
    except:
        # sleep a few minutes then give it a second shot before dying
        time.sleep(300)
        response, content = doWebRequest(url, "PUT", data=uploadXMLText)
    if response.getcode() != 200:
        raise Exception(
            "Error updating queue %s to url %s.  Response code is %s\n%s" %
            (attrDict.ark, url, response.getcode(), content)
        )
