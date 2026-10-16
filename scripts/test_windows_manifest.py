import copy
import unittest
from windows_manifest import windows_manifest

class WindowsManifestTest(unittest.TestCase):
    def setUp(self):
        self.name = 'unimate-win-x64-0.1.3-beta.1.exe'
        self.assets = {self.name: {'sha512': 'fixture-sha512', 'size': 123}}
        self.manifest = {'version': '0.1.3-beta.1', 'files': [{'url': self.name, **self.assets[self.name]}]}
        self.proof = dict.fromkeys(['seedFixture', 'tlsVerified', 'checked', 'downloaded', 'installed', 'restarted', 'profilePreserved', 'corruptDownloadRejected'], True)
        self.proof.update({'from': '0.1.3-beta.0', 'to': '0.1.3-beta.1', 'channel': 'beta', 'feedNamespace': 'windows-beta', 'modelCalls': 0})
    def test_immutable_public_url(self):
        result = windows_manifest('0.1.3', self.manifest, self.assets, self.proof)
        self.assertEqual(result['path'], 'https://github.com/JR-Academy-AI/unimate-releases/releases/download/v0.1.3-beta.1/' + self.name)
    def test_refuses_missing_real_upgrade_gates(self):
        for field in ['tlsVerified', 'installed', 'restarted', 'profilePreserved', 'corruptDownloadRejected']:
            with self.subTest(field=field), self.assertRaises(ValueError):
                windows_manifest('0.1.3', self.manifest, self.assets, {**self.proof, field: False})
    def test_rejects_substitution_and_integrity_mismatch(self):
        for field, value in [('url', 'other.exe'), ('sha512', 'wrong'), ('size', 122)]:
            manifest = copy.deepcopy(self.manifest)
            manifest['files'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                windows_manifest('0.1.3', manifest, self.assets, self.proof)
        with self.assertRaises(ValueError):
            windows_manifest('0.1.3', {**self.manifest, 'version': '0.1.3'}, self.assets, self.proof)

if __name__ == '__main__':
    unittest.main()
