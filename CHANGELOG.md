# Changelog

## 2026-10-16

- 新增仅在 GitHub 托管 runner 验证安装包回执、发布允许清单内二进制及回读哈希的发布流程（release）。

- 加强 Windows 公开发布门槛，要求两次启动的登录表单真实可见，拒绝旧加载页验收凭据。

- 修复 GitHub 草稿尚无公开 tag 时的 Release 查询，继续使用同一草稿上传与验证，避免重复发布。

- 修复新建草稿的列表同步延迟，直接使用创建返回的 Release ID，保持同版本发布幂等（binary promotion）。
