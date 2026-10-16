"""Validate beta update metadata against verified public installer receipts."""
import urllib.parse

def windows_manifest(version, manifest, assets, upgrade):
    expected = version + '-beta.1'
    if manifest.get('version') != expected or upgrade.get('to') != expected or upgrade.get('from') != version + '-beta.0':
        raise ValueError('Wrong beta upgrade identity')
    for field in ['seedFixture', 'tlsVerified', 'checked', 'downloaded', 'installed', 'restarted', 'automaticRestartObserved', 'profilePreserved', 'corruptDownloadRejected']:
        if upgrade.get(field) is not True:
            raise ValueError('Missing Windows upgrade acceptance: ' + field)
    if upgrade.get('channel') != 'beta' or upgrade.get('feedNamespace') != 'windows-beta' or upgrade.get('modelCalls') != 0:
        raise ValueError('Wrong update acceptance contract')
    name = f'unimate-win-x64-{expected}.exe'
    files = manifest.get('files', [])
    if len(files) != 1:
        raise ValueError('Expected exactly one Windows installer')
    item = files[0]
    filename = urllib.parse.unquote(urllib.parse.urlparse(item.get('url', '')).path.rsplit('/', 1)[-1])
    artifact = assets.get(name)
    if filename != name or not artifact or item.get('sha512') != artifact['sha512'] or item.get('size') != artifact['size']:
        raise ValueError('Windows updater installer/hash/size mismatch')
    url = f'https://github.com/JR-Academy-AI/unimate-releases/releases/download/v{expected}/{name}'
    return {'version': expected, 'files': [{'url': url, 'sha512': artifact['sha512'], 'size': artifact['size']}], 'path': url, 'sha512': artifact['sha512']}
