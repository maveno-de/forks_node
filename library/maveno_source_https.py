#!python
# -*- coding: utf-8 -*-

"""Source Package Finder

This ansible module locates properties of the latest version of a given
source archive from an arbitrary website.

"""

import requests, re, datetime
import urllib.parse

from ansible.module_utils.basic import AnsibleModule

from packaging import version
from packaging.specifiers import SpecifierSet

def main():
    """Module function

    :returns: nothing
    """

    args = {'url': {'required': True, 'type': 'str'},
            'base': {'required': False, 'type': 'str'},
            'filePrefix': {'required': True, 'type': 'str'},
            'hrefPrefix': {'required': False, 'type': 'str'},
            'suffix': {'required': False, 'type': 'str'},
            'separator': {'required': False, 'default': '.', 'type': 'str'},
            'constraints': {'required': False, 'type': 'str'},
            'allowFtp': {'required': False, 'type': 'bool'},
            'simple': {'required': False, 'default': False, 'type': 'bool'},
            'checkResult': {'required': False, 'default': True, 'type': 'bool'}}

    module = AnsibleModule(argument_spec=args)

    startTime = datetime.datetime.now()

    indexUrl = module.params['url']
    baseUrl = module.params['base']
    filePrefix = module.params['filePrefix']
    allowFtp = module.params['allowFtp']
    separator = module.params['separator']
    simple = module.params['simple']     


    if simple:
        mPyVer = re.compile('\d+(\\.\d+){2}')
    else:
        mPyVer = re.compile('(\d+!)?(\d+)(\\' + separator + '\d+)+([-_])?(\.?(a(lpha)?|b(eta)?|c|r(c|ev)?|pre(view)?)\d*)?(\.?(post|dev)\d*)?')


    mFileName = re.compile('[^/]+$')
    
    # NOTE: Ways to extend: filenamePrefix + urlPrefix, ignoreAfterFilenamePrefix, ignoreAfterUrlPrefix, ignoreBeforeSuffix


    res = requests.get(indexUrl)

    # Isolating href strings from URL result
    hrefList = []
    hrefList = list(set(re.findall("[hH][rR][eE][fF]=['\"][^'\"?]+", res.text)))
    hrefList = [re.sub("[hH][rR][eE][fF]=['\"](.+)", '\\1', h) for h in hrefList]
   
    # Remove trailing slashes from hrefs if exists
    hrefList = [h[:-1] if h.endswith('/') else h for h in hrefList]

    # Filtering out href not having required file endings and decode URL characters
    fileSuffices = ('.tar.gz','.tar.bz2','.tgz')
    if not module.params['suffix'] is None:
        fileSuffices = (module.params['suffix'],)
    hrefList = [urllib.parse.unquote(h) for h in hrefList if h.endswith(fileSuffices)]

    # Filtering out href not starting with required prefix
    if not module.params['hrefPrefix'] is None:
        hrefList = [h for h in hrefList if h.startswith(module.params['hrefPrefix'])]


    #module.fail_json(msg=hrefList)

    availableVersions = []
    for fileSuffix in fileSuffices:

        try:

            # Build a list of 3-tuples containing: Version, href value and filename
            availableVersions = availableVersions + [(
                                version.parse(mPyVer.search(mFileName.search(r).group(0)[len(filePrefix):-len(fileSuffix)]).group(0).replace(separator,'.')),  
                                r, 
                                mFileName.search(r).group(0) )
                                for r in hrefList
                                if r.endswith(fileSuffix)
                                and mFileName.search(r).group(0).startswith(filePrefix)]
        except:
            pass


    # Filter out ftp links if not allowed
    if allowFtp is None or allowFtp == False:
        availableVersions = [v for v in availableVersions if not v[1].startswith('ftp')]

    # Filter out legacy and pre-release Versions
    availableVersions = [v for v in availableVersions if isinstance(v[0], version.Version) 
                            and not v[0].is_prerelease]


    # Create list of strings containing the released Versions
    releasedVersionList = list(set([v[0].base_version for v in availableVersions]))


    # Filter out non-complying Versions if constraints are set
    specifiedVersions = availableVersions
    if not module.params['constraints'] is None and module.params['constraints'] != '':

        spec = SpecifierSet(module.params['constraints'])
        specifiedVersions = [u for u in specifiedVersions if u[0] in spec]

        if specifiedVersions is None or len(specifiedVersions) == 0:
            module.fail_json(msg='No sources found complying to specified versions')


    if specifiedVersions is None or len(specifiedVersions) == 0:
        module.fail_json(msg='No sources found')

    # Sort Versions in descending order, so latest appropriate Version is always found in element 0
    specifiedVersions = sorted(specifiedVersions, key=lambda v: v[0], reverse=True)


    # Create list of strings containing the specified Versions
    specifiedVersionList = list(set([v[0].base_version for v in specifiedVersions]))
    
    recommendedVersion = specifiedVersions[0][0]
    recommendedHref = specifiedVersions[0][1]
    recommendedFilename = specifiedVersions[0][2]

    if not baseUrl is None:
        indexUrl = baseUrl

    # Add base URL if href was relative URL
    if recommendedHref.startswith(('http','ftp')):
        recommendedUrl = recommendedHref
    else:
        recommendedUrl = '%s%s%s' % (str(indexUrl[:-1] if indexUrl.endswith('/') else indexUrl),
                                        '/', str(recommendedHref[1:] if recommendedHref.startswith('/') else recommendedHref))

    # Retrieve file type. Also a test if remote file exists.
    recommendedContentType = ''
    if not recommendedHref.startswith(('ftp')) and module.params['checkResult']:
        try:
            r = requests.head(recommendedUrl)
            recommendedContentType = r.headers['Content-Type']
        except requests.exceptions.MissingSchema:
            module.fail_json(msg='Recommended release archive file could not be found! (%s)' % recommendedUrl)

    endTime = datetime.datetime.now()

    result = {

        'changed': False,
        'start': str(startTime),
        'end': str(endTime),
        'delta': str(endTime - startTime),
        'released_versions': releasedVersionList,
        'specified_versions': specifiedVersionList,
        'recommended_version': recommendedVersion.base_version,
        'recommended_url': recommendedUrl,
        'recommended_filename': recommendedFilename,
        'recommended_file_type': recommendedContentType
    }

    module.exit_json(**result)


if __name__ == '__main__':
    main()
