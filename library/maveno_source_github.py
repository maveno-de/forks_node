#!python
# -*- coding: utf-8 -*-

"""Github Source Package Finder

This ansible module locates properties of the latest version
of a given Github repository.

"""

import requests, re, datetime

from ansible.module_utils.basic import AnsibleModule

from packaging import version
from packaging.specifiers import SpecifierSet


def main():
    """Module function

    :returns: nothing
    """

    args = {'owner': {'required': True, 'type': 'str'},
            'repo': {'required': True, 'type': 'str'},
            'keywords': {'required': False, 'type': 'list'},
            'suffix': {'required': False, 'type': 'str'},
            'constraints': {'required': False, 'type': 'str'}}

    module = AnsibleModule(argument_spec=args)

    startTime = datetime.datetime.now()

    latestReleaseResult = requests.get('https://api.github.com/repos/%s/%s/releases/latest' % (module.params['owner'], module.params['repo']))
    latestReleaseData = latestReleaseResult.json()

    latestReleaseVersion = None
    if 'tag_name' in latestReleaseData:
        tagName = latestReleaseData['tag_name']
        parsedVersion = version.parse(tagName)
        if isinstance(parsedVersion, version.Version):
            latestReleaseVersion = parsedVersion


    tagsResult = requests.get('https://api.github.com/repos/%s/%s/tags' % (module.params['owner'], module.params['repo']))
    tagsData = tagsResult.json()

    availableVersionsList = []

    for tag in tagsData:
        tagVersion = version.parse(tag['name'])

        # Validate tag version
        isTagValid = True
        if not isinstance(tagVersion, version.Version):
            isTagValid = False        
        if tagVersion.is_prerelease:
            isTagValid = False
 
        if isTagValid:
            availableVersionsList.append(tagVersion)

    availableVersionsList = sorted(availableVersionsList, reverse=True)
    
    specifiedVersionsList = availableVersionsList
    if not module.params['constraints'] is None and module.params['constraints'] != '':
        spec = SpecifierSet(module.params['constraints'])
        specifiedVersionsList = list(spec.filter(specifiedVersionsList))

        # TODO: #176 Causing bug when not set
        if not latestReleaseVersion in spec:
            latestReleaseVersion = None

    recommendedVersion = None
    if len(availableVersionsList) >= 1:
        recommendedVersion = availableVersionsList[0]
        if not latestReleaseVersion is None:    
            recommendedVersion = max([availableVersionsList[0], latestReleaseVersion])

    if recommendedVersion is None:
        module.fail_json(msg='No valid version of repository %s/%s can be determined' % (module.params['owner'], module.params['repo']))

    recommendedTagData = next(t for t in tagsData if version.parse(t['name']) == recommendedVersion)
    recommendedUrl = recommendedTagData['tarball_url']

    assetKeywords = module.params['keywords']
    if not assetKeywords is None:
        for asset in latestReleaseData['assets']:
            match = True
            for word in assetKeywords:
                if not word in asset['name']:
                    match = False
                if not module.params['suffix'] is None and not asset['name'].endswith(module.params['suffix']):
                    match = False
            if match:
                recommendedUrl = asset['browser_download_url']

    endTime = datetime.datetime.now()

    result = {

        'changed': False,
        'start': str(startTime),
        'end': str(endTime),
        'delta': str(endTime - startTime),
        'latest_release_version': '' if latestReleaseVersion is None else latestReleaseVersion.base_version,
        'released_versions': [v.base_version for v in availableVersionsList],
        'specified_versions': [v.base_version for v in specifiedVersionsList],
        'recommended_version': recommendedVersion.base_version,
        'recommended_url': recommendedUrl
    }

    module.exit_json(**result)


if __name__ == '__main__':
    main()