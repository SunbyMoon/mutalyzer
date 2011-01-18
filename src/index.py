#!/usr/bin/python

"""
The HTML publisher.

These functions appear as HTML pages on the web server.

Public methods:
    - index(req)        ; The mutation checker page.
    - Variant_info(req) ; The I{g.} to I{c.} and vice versa interface for LOVD.
    - download(req)     ; The download page.

@requires: Mutalyzer
@requires: VarInfo
@requires: pydoc
@requires: webservice
@requires: string

@requires: mod_python import apache
@requires: mod_python import Session
@requires: mod_python import util

@requires: Modules.Parser
@requires: Modules.Mapper
@requires: Modules.Web
@requires: Modules.Config
@requires: Modules.Output
@requires: Modules.Db
@requires: Modules.Scheduler
@requires: Modules.Retriever
@requires: Modules.File
"""

import Mutalyzer
import VarInfo
import pydoc
import webservice
import string
#import sys

from mod_python import apache, Session, util
from mod_python import Session, util

from Modules import Parser
from Modules import Mapper
from Modules import Web
from Modules import Config
from Modules import Output
from Modules import Db
from Modules import Scheduler
from Modules import Retriever
from Modules import File

class InputException(Exception):
    """
    @todo: documentation
    """
    pass

def snp(req) :
    """
    @todo: documentation
    
    @arg req: the HTTP request
    @type req: object
    @return: compiled TAL template
    @rtype: object
    """
    C = Config.Config()
    O = Output.Output(__file__, C.Output)
    W = Web.Web()

    rsId = None
    if req.form :
        rsId = req.form.get('rsId', None)
    if rsId :
        O.addMessage(__file__, -1, "INFO", "Received rs%s" % rsId)
        R = Retriever.Retriever(C.Retriever, O, None)
        R.snpConvert(rsId)
        O.addMessage(__file__, -1, "INFO", "Finished processing rs%s" % rsId)
    #if

    args = {
        "snp"      : O.getOutput("snp"),
        "messages" : O.getMessages(),
        "summary"  : O.Summary()[2],
        "lastpost" : rsId
    }

    return W.tal("HTML", "templates/snp.html", args)
#snp


def index(req) :
    """
    @todo: documentation
    
    @arg req: the HTTP request
    @type req: object
    @return: compiled TAL template
    @rtype: object
    """
    W = Web.Web()
    return W.tal("HTML", "templates/index.html", {})
#index

def help(req) :
    """
    @todo: documentation
    
    @arg req: the HTTP request
    @type req: object
    @return: compiled TAL template
    @rtype: object
    """
    W = Web.Web()
    return W.tal("HTML", "templates/help.html", {})
#help

def faq(req) :
    """
    @todo: documentation
    
    @arg req: the HTTP request
    @type req: object
    @return: compiled TAL template
    @rtype: object
    """
    W = Web.Web()
    return W.tal("HTML", "templates/FAQ.html", {})
#faq

def exercise(req) :
    """
    @todo: documentation
    
    @arg req: the HTTP request
    @type req: object
    @return: compiled TAL template
    @rtype: object
    """
    W = Web.Web()
    return W.tal("HTML", "templates/exercise.html", {})
#exercise

def about(req) :
    """
    @todo: documentation
    
    @arg req: the HTTP request
    @type req: object
    @return: compiled TAL template
    @rtype: object
    """
    W = Web.Web()
    return W.tal("HTML", "templates/about.html", {})
#about

def nameGenerator(req):
    """
    @todo: documentation
    
    @arg req: the HTTP request
    @type req: object
    @return: compiled TAL template
    @rtype: object
    """
    W = Web.Web()
    return W.tal("HTML", "templates/generator.html", {})
#generator

def check(req) :
    """
    The mutation checker page.

    If the incoming request has a form, run Mutalyzer. The output of
    Mutalyzer is used together with a version and the last posted value
    to make an HTML page from a TAL template.

    @arg req: The request: req.form['mutationName'] ; A description of a variant
    @type req: object

    @return: a compiled TAL template containing the results of Mutalyzer
    @rtype: object
    """

    W = Web.Web()
    C = Config.Config()
    O = Output.Output(__file__, C.Output)

    name = ""
    reply = ""
    if req.form :
        name = req.form.get('mutationName', None)
    else:
        session = Session.Session(req)
        session.load()
        name = session.get("mut", None)
        #Remove from session
        session["mut"] = None
        session.save()
    if name:
        O.addMessage(__file__, -1, "INFO", "Received variant %s" % name)
        RD = Mutalyzer.process(name, C, O)
        O.addMessage(__file__, -1, "INFO", "Finished processing variant %s" % \
                     name)
    #if
    errors, warnings, summary = O.Summary()
    recordType = O.getIndexedOutput("recordType",0)
    reference = O.getIndexedOutput("reference", 0)
    if recordType == "LRG" :
        reference += ".xml"
    else :
        reference += ".gb"

    pe = O.getOutput("parseError")
    if pe :
        pe[0] = pe[0].replace('<', "&lt;")

    genomicDNA = True
    if O.getIndexedOutput("molType", 0) == 'n' :
        genomicDNA = False

    args = {
        "lastpost"           : name,
        "messages"           : O.getMessages(),
        "summary"            : summary,
        "parseError"         : pe,
        "errors"             : errors,
        "genomicDescription" : W.urlEncode([O.getIndexedOutput(
                                   "genomicDescription", 0)])[0],
        "chromDescription"   : O.getIndexedOutput("genomicChromDescription", 0),
        "genomicDNA"         : genomicDNA,
        "visualisation"      : O.getOutput("visualisation"),
        "descriptions"       : W.urlEncode(O.getOutput("descriptions")),
        "protDescriptions"   : O.getOutput("protDescriptions"),
        "oldProtein"         : O.getOutput("oldProteinFancy"),
        "altStart"           : O.getIndexedOutput("altStart", 0),
        "altProtein"         : O.getOutput("altProteinFancy"),
        "newProtein"         : O.getOutput("newProteinFancy"),
        "exonInfo"           : O.getOutput("exonInfo"),
        "cdsStart_g"         : O.getIndexedOutput("cdsStart_g", 0),
        "cdsStart_c"         : O.getIndexedOutput("cdsStart_c", 0),
        "cdsStop_g"          : O.getIndexedOutput("cdsStop_g", 0),
        "cdsStop_c"          : O.getIndexedOutput("cdsStop_c", 0),
        "restrictionSites"   : O.getOutput("restrictionSites"),
        "legends"            : O.getOutput("legends"),
        "reference"          : reference
    }

    if req.method == 'GET' and req.form :
        args["interactive"] = False
        ret = W.tal_old("HTML", "templates/check.html", args)
    else :
        args["interactive"] = True
        ret = W.tal("HTML", "templates/check.html", args)
    del W
    return ret
#check

def getGS(req):
    """
    LOVD bypass to get the correct GeneSymbol incl Transcript variant.

    Used by LOVD to get the correct transcript variant out of a genomic
    record. LOVD uses a genomic reference (NC_?) in combination with a gene
    symbol to pass variant info to mutalyzer. Mutalyzer 1.0 was only using
    the first transcript. LOVD supplies the NM of the transcript needed but
    this was ignored. This helper allows LOVD to get the requested
    transcript variant from a genomic reference.

    @arg req: The request:
        - req.form['mutationName'] ; the mutationname without gene symbol
        - re.form['variantRecord'] ; the NM reference of the variant
        - re.form['forward']       ; if set this forwards the request to the name
                                     checker
    @type req:
    
    @return:
        - string ; The GeneSymbol with the variant notation
        - web    ; If forward is set the request is forwarded to check
    """
    W = Web.Web()
    C = Config.Config()
    O = Output.Output(__file__, C.Output)

    if not req.form:
        return "Error in input"
    mutationName = req.form.get("mutationName", None)
    variantRecord = req.form.get("variantRecord", None)
    forward = req.form.get("forward", None)

    # We are only interested in the legend
    Mutalyzer.process(mutationName, C, O)

    legends = O.getOutput("legends")

    # Filter the transcript from the legend
    legends = [l for l in legends if "_v" in l[0]]
    for l in legends:
        if l[1] == variantRecord:
            if forward:
                p,a = mutationName.split(':')
                req.form["mutationName"] = p+'('+l[0]+'):'+a
                return check(req)
            else:
                return l[0]
    return "Transcript not found"#+`legends`
#getGS


def checkForward(req) :
    """
    @arg req:
    @type req:
    
    @todo: documentation
    """
    session = Session.Session(req)
    session['mut'] = req.form.get("mutationName", None)
    session.save()
    util.redirect(req, "check", permanent=False)
#checkForward


def syntaxCheck(req) :
    """
    Checks the syntax of a variant

    @arg req: The request:
              req.form['variant']  ; A description of the variant
    @type req: object

    @return: An HTML page containing the remark if the variant syntax is OK or
             not
    @rtype: string
    """

    W = Web.Web()
    C = Config.Config() # Read the configuration file.
    O = Output.Output(__file__, C.Output)
    variant = req.form.get("variant", None)
    if variant:
        if variant.find(',') >= 0:
            O.addMessage(__file__, 2, "WCOMMASYNTAX",
                    "Comma's are not allowed in the syntax, autofixed")
            variant = variant.replace(',', '')
            #args["variant"]=variant
        P = Parser.Nomenclatureparser(O)
        parsetree = P.parse(variant)
        #if not parsetree :
        #    args["messages"].append("This variant does not have the right"
        #    args["messages"].extend(O.getMessages())
        #else :
        #    args["messages"].append("The syntax of this variant is OK!")
    #if

    pe = O.getOutput("parseError")
    if pe :
        pe[0] = pe[0].replace('<', "&lt;")

    args = {
        "variant"       : variant,
        "messages"      : O.getMessages(),
        "parseError"    : pe,
        "debug"         : ""
    }
    ret = W.tal("HTML", "templates/parse.html", args)
    del W
    return ret
#checkingSyntax

def positionConverter(req):
    """
    @arg req:
    @type req:
    
    @todo: documentation
    """
    W = Web.Web()
    C = Config.Config()
    O = Output.Output(__file__, C.Output)

    if not req.form: req.form = {}
    build = req.form.get("build", "")
    variant = req.form.get("variant", "")

    avail_builds = C.Db.dbNames[::-1]

    if build :
        avail_builds.remove(build)
        avail_builds.insert(0, build)
    #if

    attr = {
        "avail_builds" : avail_builds,
        "variant"      : variant,
        "gName"        : "",
        "cNames"       : [],
        "messages"     : [],
        "errors"       : [],
        "debug"        : []
        }

    if build and variant:
        converter = Mapper.Converter(build, C, O)

        #Conver chr accNo to NC number
        variant = converter.correctChrVariant(variant)

        if variant :
            if not(":c." in variant or ":g." in variant):
                #Bad name
                P = Parser.Nomenclatureparser(O)
                parsetree = P.parse(variant)
            #if

            if ":c." in variant:
                # Do the c2chrom dance
                variant = converter.c2chrom(variant)
            if variant and ":g." in variant:
                # Do the g2c dance
                variants = converter.chrom2c(variant, "dict")
                if variants:
                    attr["gName"] = variant
                    output = ["%-10s:\t%s" % (key[:10], "\n\t\t".join(value))\
                            for key, value in variants.items()]
                    attr["cNames"].extend(output)
                #if
            #if
        #if

        attr["errors"].extend(O.getMessages())
    return W.tal("HTML", "templates/converter.html", attr)
#positionConverter

def Variant_info(req) :
    """
    The I{g.} to I{c.} and vice versa interface for LOVD.

    @arg req: The request:
      - req.form['LOVD_ver'] ; The version of the calling LOVD
      - req.form['build']    ; The human genome build (hg19 assumed)
      - req.form['acc']      ; The accession number (NM number)
      - req.form['var']      ; A description of the variant
    @type req: object

    @return: An HTML page containing the results of Variant_info
    @rtype: string
    """

    W = Web.Web()

    LOVD_ver = req.form['LOVD_ver']
    build = req.form['build']
    acc = req.form['acc']
    var = req.form.get("var", "")

    result = W.run(VarInfo.main, LOVD_ver, build, acc, var)

    if LOVD_ver == "2.0-23" : # Obsoleted error messages, remove when possible.
        import re

        return re.sub("^Error \(.*\):", "Error:", result)
    #if
    return result
#Variant_info

def webservices(req) :
    """
    The download page.

    @arg req: The request
    @type req: object

    @return: An HTML page
    @rtype: object
    """

    W = Web.Web()

    ret = W.tal("HTML", "templates/webservices.html", {})
    del W
    return ret
#download

def __checkInt(inpv, refname):
    """
    @arg inpv:
    @type inpv:
    @arg refname:
    @type refname:
    
    @todo: documentation
    """
    #remove , . and -
    inpv = inpv.replace(',','').replace('.','').replace('-','')
    try:
        return int(inpv)
    except ValueError, e:
        raise InputException("Expected an integer in field: %s" % refname)

def upload(req) :
    """
    @arg req:
    @type req:
    
    @return:
    @rtype:
    
    @todo: documentation
    """

    C = Config.Config()
    maxUploadSize = C.Retriever.maxDldSize

    O = Output.Output(__file__, C.Output)
    D = Db.Cache(C.Db)
    R = Retriever.GenBankRetriever(C.Retriever, O, D)

    UD, errors = "", []

    if req.method == 'POST' :
        try:
            if req.form["invoermethode"] == "file" :
                length = req.headers_in.get('Content-Length')
                if not length :
                    req.status = apache.HTTP_LENGTH_REQUIRED
                    req.write("Content length required.")
                    return None
                #if
                if int(length) > maxUploadSize :
                    req.status = apache.HTTP_REQUEST_ENTITY_TOO_LARGE
                    req.write("Upload limit exceeded.")
                    return None
                #if
                UD = R.uploadrecord(req.form["bestandsveld"].file.read())
            #if
            elif req.form["invoermethode"] == "url" :
                UD = R.downloadrecord(req.form["urlveld"])
            #if
            elif req.form["invoermethode"] == "gene" :
                geneName = req.form["genesymbol"]
                organism = req.form["organism"]
                upStream = __checkInt((req.form["5utr"]),
                        "5' flanking nucleotides")
                downStream = __checkInt((req.form["3utr"]),
                        "3' flanking nucleotides")
                UD = R.retrievegene(geneName, organism, upStream, downStream)
            #if
            elif req.form["invoermethode"] == "chr" :
                accNo = req.form["chracc"]
                start = __checkInt((req.form["start"]),
                        "Start position")
                stop = __checkInt((req.form["stop"]),
                        "Stop position")
                orientation = int(req.form["orientation"])
                UD = R.retrieveslice(accNo, start, stop, orientation)
            #if
            else:
                #unknown "invoermethode"
                raise InputException("Wrong method selected")
        except InputException, e:
            #DUMB USERS
            errors.append(e)
        finally:
            if not UD:
                #Something went wrong
                errors += ["The request could not be completed"]
                errors.extend(O.getMessages())
    #if

    W = Web.Web()
    args = {
        "UD"      : UD,
        "maxSize" : float(maxUploadSize) / 1048576,
        "errors"  : errors
    }
    ret = W.tal("HTML", "templates/gbupload.html", args)
    del W
    return ret
#upload

def progress(req):
    """
    Progress page for batch runs

    @arg req:
    @type req:
    
    @return:
    @rtype:
    
    @todo: documentation
    """
    W = Web.Web()
    C = Config.Config()
    O = Output.Output(__file__, C.Output)

    attr = {"percentage"    : 0}

    try:
        jobID = int(req.form["jobID"])
        total = int(req.form["totalJobs"])
    except Exception, e:
        return
    D = Db.Batch(C.Db)
    left = D.entriesLeftForJob(jobID)
    percentage = int(100 - (100 * left / float(total)))
    if req.form.get("ajax", None):
        if percentage == 100:
            #download url, check if file still exists
            ret = "OK"
        else:
            ret = percentage
        return ret
    else:
        #Return progress html page
        return W.tal("HTML", "templates/progress.html", attr)


def batch(req, batchType=None):
    """
    Batch function to add batch jobs to the Database

    @arg batchType: Type of the batch job
    @type batchType: string
    
    
    @arg req: the HTTP request
    @type req: object
    @return: compiled TAL template
    @rtype: object
    
    @todo: documentation
    """
    W = Web.Web()
    C = Config.Config()
    O = Output.Output(__file__, C.Output)

    attr = {"messages"      : [],
            "errors"        : [],
            "debug"         : [],
            "batchTypes"    : ["NameChecker",
                               "SyntaxChecker",
                               "PositionConverter"],
            "hideTypes"     : batchType and 'none' or '',
            "selected"      : "0",
            "batchType"     : batchType or "",
            "avail_builds"  : C.Db.dbNames[::-1],
            "jobID"         : None,
            "totalJobs"     : None
         }

    # Use an empty dictionary if no form is filed
    if not(req.form): req.form = {}

    #get email and inFile
    email = req.form.get("batchEmail", None)
    inFile = req.form.get("batchFile", None)
    arg1 = req.form.get("arg1", "")

    #Make sure the correct page is displayed for an entrypoint
    batchType =  req.form.get("batchType", batchType or "NameChecker")
    if batchType in attr["batchTypes"]:
        attr["selected"] = str(attr["batchTypes"].index(batchType))

    if email and W.isEMail(email) and inFile:
        D = Db.Batch(C.Db)
        S = Scheduler.Scheduler(C.Scheduler, D)
        FileInstance = File.File(C.File, O)

        # Generate the fromhost URL from which the results can be fetched
        fromHost = "http://%s%s" % (
            req.hostname, req.uri.rsplit("/", 1)[0]+"/")

        job = FileInstance.parseBatchFile(inFile.file)
        if job is None:
            O.addMessage(__file__, 4, "PRSERR", "Could not parse input"
                " file, please check your file format.")
        else:
            #TODO: Add Binair Switches to toggle some events
            attr["jobID"] =\
                    S.addJob("BINSWITHCES", email, job, fromHost, batchType, arg1)
            attr["totalJobs"] = len(job) or 1
            attr["messages"].append("Your file has been parsed and the job"
                " is scheduled, you will receive an email when the job is "
                "finished.")

        attr["errors"].extend(O.getMessages())

    return W.tal("HTML", "templates/batch.html", attr)
#batch

def disclaimer(req) :
    """
    @arg req: the HTTP request
    @type req: object
    @return: compiled TAL template
    @rtype: object
    
    @todo: documentation
    """
    W = Web.Web()
    return W.tal("HTML", "templates/disclaimer.html", [])
#disclaimer

def batchNameChecker(req):
    """
    @arg req:
    @type req:
    
    @return:
    @rtype:
    
    @todo: documentation
    """
    return batch(req, "NameChecker")
#batchCheck

def batchPositionConverter(req):
    """
    @arg req:
    @type req:
    
    @return:
    @rtype:
    
    @todo: documentation
    """
    return batch(req, "PositionConverter")
#batchConvert

def batchSyntaxChecker(req):
    return batch(req, "SyntaxChecker")
#batchCheckSyntaxch

def documentation(req) :
    """
    Generate documentation for the webservice.

    @arg req: The HTTP request
    @type req: object

    @return: An HTML page
    @rtype: string
    """

    htmldoc = pydoc.HTMLDoc()
    doc = "<html><body>%s</body></html>" % htmldoc.docmodule(webservice)
    return doc
#documentation

#TODO: taltest.html does not exist
def taltest(req) :
    """
    @arg req: the HTTP request
    @type req: object
    @return: compiled TAL template
    @rtype: object
    
    @todo: taltest.html does not exist
    @todo: documentation
    """
    W = Web.Web()
    C = Config.Config()
    variant = ""
    finalbuilds = []
    availBuilds = C.Db.dbNames  # available builds in config file
    for x in availBuilds :
        builds = {}
        builds["build"] = x
        finalbuilds.append(builds)
#    build = availBuilds[len(availBuilds)-1] # default to the highest build
    build = "hg18"
    args = {
        "build" : build,
        "avail_builds" : finalbuilds,
        "variant"  : variant
        }
    ret = W.tal("HTML", "templates/taltest.html", args)
    del W
    return ret
#taltest