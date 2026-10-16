"""GitHub Actions-only promotion of verified UniMate installers; no private repo token."""
import base64, concurrent.futures, hashlib, json, os, pathlib, re, subprocess, tempfile, urllib.parse, urllib.request, zipfile
import yaml
REPO='JR-Academy-AI/unimate-releases'
def require(ok, message):
    if not ok: raise RuntimeError(message)
def gh(*args):
    return subprocess.check_output(['gh', *args], text=True).strip()
def digest(data): return hashlib.sha256(data).hexdigest()
require(os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('GITHUB_REPOSITORY')==REPO, 'Wrong publisher environment')
require(os.environ.get('GITHUB_REF')=='refs/heads/main', 'Publish from reviewed public main only')
require(os.environ.get('CONFIRM')=='publish-unimate', 'Explicit promotion confirmation required')
version=os.environ['VERSION']; channel=os.environ['CHANNEL']; source=os.environ['SOURCE_COMMIT']
require(re.fullmatch(r'\d+\.\d+\.\d+',version) and re.fullmatch(r'[a-f0-9]{40}',source), 'Invalid release identity')
require(channel in ['mac','windows'], 'Unknown platform')
sources=sorted(json.loads(os.environ['SOURCES']),key=lambda row:(row['platform'],row['arch']))
expected={('mac','arm64'),('mac','x64')} if channel=='mac' else {('win','x64')}
require(len(sources)==len(expected) and {(s['platform'],s['arch']) for s in sources}==expected, 'Missing or duplicate architectures')
root=pathlib.Path(tempfile.mkdtemp(prefix='unimate-promotion-')); output=root/'assets'; output.mkdir()
assets={}; receipts=[]; manifests=[]
def download(row):
    url=row['url']; parsed=urllib.parse.urlparse(url)
    require(parsed.scheme=='https' and not parsed.username and not parsed.password and parsed.hostname.endswith('.blob.core.windows.net'), 'Unexpected artifact download host')
    require(re.fullmatch(r'sha256:[a-f0-9]{64}',row['digest']), 'Missing authenticated artifact digest')
    print('::add-mask::'+url)
    target=root/(row['platform']+'-'+row['arch']+'.zip')
    with urllib.request.urlopen(url,timeout=180) as response, target.open('wb') as f:
        while chunk:=response.read(1024*1024): f.write(chunk)
    require('sha256:'+digest(target.read_bytes())==row['digest'], 'Artifact archive digest mismatch')
    return row,target
for row,archive in concurrent.futures.ThreadPoolExecutor(max_workers=3).map(download,sources):
    with zipfile.ZipFile(archive) as z:
        require(all('/' not in n.rstrip('/') and not n.startswith('.') for n in z.namelist()), 'Artifact contains unexpected paths')
        receipt=json.loads(z.read('receipt.json'))
        require(receipt['sourceCommit']==source and (receipt['platform'],receipt['arch'])==(row['platform'],row['arch']), 'Receipt provenance mismatch')
        require(receipt['installed'] is True and receipt['smoke']['syntheticProfilePreserved'] is True and len(receipt['smoke']['rounds'])==2 and receipt['smoke']['modelCalls']==0, 'Missing installed/reopen acceptance')
        if channel=='windows': require(all(r.get('loginVisible') is True for r in receipt['smoke']['rounds']), 'Windows loading-screen receipt is not acceptance')
        required=[f'unimate-mac-{row["arch"]}-{version}.{ext}' for ext in ['dmg','zip']] if channel=='mac' else [f'unimate-win-x64-{version}-beta.1.exe']
        require(receipt['version']==(version if channel=='mac' else version+'-beta.1'), 'Wrong version')
        require((receipt['signed'] and receipt['notarized']) if channel=='mac' else (receipt['unsignedPreview'] and not receipt['signed']), 'Wrong signing contract')
        rows=receipt['artifacts']; names=[a['name'] for a in rows]
        require(all(n in names for n in required) and all(n in required or n.removesuffix('.blockmap') in required for n in names), 'Non-allowlisted public asset')
        for item in rows:
            data=z.read(item['name'])
            require(len(data)==item['size'] and digest(data)==item['sha256'] and base64.b64encode(hashlib.sha512(data).digest()).decode()==item['sha512'], 'Installer integrity mismatch')
            require(item['name'] not in assets, 'Duplicate asset')
            (output/item['name']).write_bytes(data); assets[item['name']]=item
        if channel=='mac': manifests.append(yaml.safe_load(z.read('latest-mac.yml')))
        receipts.append(receipt)
tag='v'+version if channel=='mac' else 'v'+version+'-beta.1'
if channel=='mac':
    entries=[]
    for manifest in manifests:
        require(str(manifest['version'])==version, 'Wrong updater version')
        for item in manifest['files']:
            name=urllib.parse.unquote(urllib.parse.urlparse(item['url']).path.rsplit('/',1)[-1])
            require(name in assets and item['sha512']==assets[name]['sha512'], 'Updater hash mismatch')
            entries.append({**item,'url':f'https://github.com/{REPO}/releases/download/{tag}/{name}'})
    require(any('arm64' in a['url'] for a in entries) and any('x64' in a['url'] for a in entries), 'Updater misses an architecture')
    updater={'version':version,'files':entries,'path':entries[0]['url'],'sha512':entries[0]['sha512']}
    (output/'latest-mac.yml').write_text(yaml.safe_dump(updater,sort_keys=False))
(output/'SHA256SUMS').write_text(''.join(f'{item["sha256"]}  {name}\n' for name,item in sorted(assets.items())))
evidence={'sourceCommit':source,'sourceRunIds':sorted({r['runId'] for r in receipts}),'version':tag,'platforms':[{'platform':r['platform'],'arch':r['arch'],'signed':r['signed'],'notarized':r['notarized'],'installed':r['installed'],'smoke':r['smoke'],'artifacts':r['artifacts']} for r in receipts], 'authenticatedAccountAcceptance':False,'upgradeRollbackAcceptance':False}
(output/'release-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
notes=root/'notes.md'
notes.write_text(('Mac ARM64 与 Intel 安装包；Developer ID 签名并通过 Apple 公证。' if channel=='mac' else 'Windows x64 未签名测试版。尚无 Authenticode 证书，Windows 可能显示“未知发布者”或 SmartScreen 安全提示。请只使用本仓库的安装包并核对 SHA256；不要关闭系统安全保护。')+'\n\nCLI 接入：Claude Code、Codex 各 A$8 一次性解锁，模型订阅和用量另计。线上购买入口尚未启用。\n\nSource commit: '+source+'\nInstalled launch/reopen was checked with a synthetic profile; signed-in account, live payment/refund, upgrade/rollback acceptance remain unverified.\n')
view=subprocess.run(['gh','release','view',tag,'--repo',REPO],capture_output=True)
if view.returncode:
    args=['release','create',tag,'--repo',REPO,'--target',os.environ['GITHUB_SHA'],'--draft','--title','牛小匠 '+(version if channel=='mac' else version+' Windows 未签名测试版'),'--notes-file',str(notes)]
    if channel=='windows': args.append('--prerelease')
    gh(*args)
release=next(r for page in json.loads(gh('api',f'repos/{REPO}/releases?per_page=100','--paginate','--slurp')) for r in page if r['tag_name']==tag)
existing={a['name']:a for a in release['assets']}
for file in sorted(output.iterdir()):
    if file.name in existing:
        require(existing[file.name].get('digest')=='sha256:'+digest(file.read_bytes()),'Refusing to overwrite immutable release asset')
    else: gh('release','upload',tag,str(file),'--repo',REPO)
args=['release','edit',tag,'--repo',REPO,'--draft=false','--notes-file',str(notes)]
if channel=='mac': args.extend(['--latest','--prerelease=false'])
else: args.extend(['--prerelease','--latest=false'])
gh(*args)
if channel=='mac':
    if subprocess.run(['gh','release','view','latest','--repo',REPO],capture_output=True).returncode:
        gh('release','create','latest','--repo',REPO,'--target',os.environ['GITHUB_SHA'],'--title','牛小匠稳定更新元数据','--notes','Stable update metadata; installers use immutable versioned URLs.','--latest=false')
    gh('release','upload','latest',str(output/'latest-mac.yml'),'--repo',REPO,'--clobber')
for file in sorted(output.iterdir()):
    url=f'https://github.com/{REPO}/releases/download/{tag}/'+urllib.parse.quote(file.name)
    with urllib.request.urlopen(url,timeout=180) as response: actual=digest(response.read())
    require(actual==digest(file.read_bytes()), 'Public asset readback mismatch')
if channel=='mac':
    with urllib.request.urlopen(f'https://github.com/{REPO}/releases/download/latest/latest-mac.yml',timeout=30) as response: current=response.read()
    require(digest(current)==digest((output/'latest-mac.yml').read_bytes()), 'Stable channel readback mismatch')
print('PUBLISHED_AND_READ_BACK '+tag+' source='+source)
