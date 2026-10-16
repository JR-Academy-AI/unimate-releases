# 牛小匠 UniMate downloads

Desktop study and writing companion by JR Academy. Application source remains in a separate private repository.

## Mac — 0.1.2

Developer ID signed, Apple notarized and stapled. Choose the build for your Mac:

- [Apple Silicon (ARM64) DMG](https://github.com/JR-Academy-AI/unimate-releases/releases/download/v0.1.2/unimate-mac-arm64-0.1.2.dmg)
- [Intel (x64) DMG](https://github.com/JR-Academy-AI/unimate-releases/releases/download/v0.1.2/unimate-mac-x64-0.1.2.dmg)
- [Release notes, ZIP packages and SHA256 checksums](https://github.com/JR-Academy-AI/unimate-releases/releases/tag/v0.1.2)

## Windows — 0.1.3-beta.1 unsigned test version

- [Windows x64 installer](https://github.com/JR-Academy-AI/unimate-releases/releases/download/v0.1.3-beta.1/unimate-win-x64-0.1.3-beta.1.exe)
- [Release notes, update metadata and SHA256 checksums](https://github.com/JR-Academy-AI/unimate-releases/releases/tag/v0.1.3-beta.1)

**自动更新已启用：** 默认后台检查和下载新版，安装重启前可确认。Windows 测试版使用独立更新通道，保留用户关闭自动检查或下载的选择。

**旧版需手动安装一次：** 0.1.2-beta.1 及更早的 Windows 包未配置更新地址，不能自动取得这次更新。请先下载并安装 0.1.3-beta.1，之后可以使用自动更新。

**Windows 未签名测试版：** 尚无 Authenticode 证书，Windows 可能显示“未知发布者”或 SmartScreen 提示。请只使用本仓库的文件并核对 SHA256，不要关闭系统安全保护。

GitHub-hosted Windows CI verified installation, visible login, reopening, a real installer update, automatic restart, synthetic profile preservation and corrupt-download rejection. The restarted process and renderer were observed through Windows; the synthetic profile was reopened on a fresh debugging port for data and UI inspection.

- [Cloud source checks](https://github.com/JR-Academy-AI/unimate-desktop/actions/runs/38900393010)
- [Installed Windows update acceptance](https://github.com/JR-Academy-AI/unimate-desktop/actions/runs/38900393511)
- [Public publishing and byte readback](https://github.com/JR-Academy-AI/unimate-releases/actions/runs/38901404128)

[All releases](https://github.com/JR-Academy-AI/unimate-releases/releases)

Public assets contain installers, updater metadata, checksums and sanitized release evidence. Private application source, credentials, signing keys, source maps and build logs stay outside the public release repository.
