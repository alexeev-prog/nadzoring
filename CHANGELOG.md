# Changelog
## [0.5.0](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.5.0) - 2026-10-28

### Dependencies

- Bump version and add pre commit config([322da09](https://github.com/alexeev-prog/nadzoring/commit/322da09ca5cabe83fc4fc9c94d49085d87ef6146))
- Bump version and add pre commit config (#174)([18921cf](https://github.com/alexeev-prog/nadzoring/commit/18921cf0a41201f898592e63ed9cf118dc96b14e))
## [0.3.0](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.3.0) - 2026-10-28

### Bug Fixes

- Fix: tighten plugin connectors per code review

Narrow ARP exception handling to ARPCacheRetrievalError, serialise ARP
entries with asdict and JSON-safe state. Drop redundant broad excepts
where domain APIs return errors in data; use whois_lookup error field.
Mark boolean connector options as keyword-only. Simplify email and
subdomain probes to match non-raising domain APIs.

Co-authored-by: Cursor <cursoragent@cursor.com>([276a2b4](https://github.com/alexeev-prog/nadzoring/commit/276a2b42c39c7d9450e36efd6849c7c5e911a715))
- Fix: security connector imports, subdomain row errors, and tests

Hoist domain imports to module scope; remove dashed section comments.
SubdomainScanConnector treats optional per-row error like other security
connectors. Add email/subdomain failure-path tests; patch connector module
for monkeypatch compatibility.

Co-authored-by: Cursor <cursoragent@cursor.com>([7965d62](https://github.com/alexeev-prog/nadzoring/commit/7965d621e1dde71b48c14ba799cb42b758dc77ab))

### Build System

- Build(deps): bump astral-sh/setup-uv from 7 to 8.0.0

Bumps [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) from 7 to 8.0.0.
- [Release notes](https://github.com/astral-sh/setup-uv/releases)
- [Commits](https://github.com/astral-sh/setup-uv/compare/v7...v8.0.0)

---
updated-dependencies:
- dependency-name: astral-sh/setup-uv
  dependency-version: 8.0.0
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([2136b16](https://github.com/alexeev-prog/nadzoring/commit/2136b16bce1280b1c0279ef82b68b5117a5c98a7))
- Build(deps): bump astral-sh/setup-uv from 7 to 8.0.0 (#112)([8878a34](https://github.com/alexeev-prog/nadzoring/commit/8878a34b8cb76ea83a7fbc2cea9c2cfcc5af851d))
- Build(deps-dev): bump nox from 2026.2.9 to 2026.4.10

Bumps [nox](https://github.com/wntrblm/nox) from 2026.2.9 to 2026.4.10.
- [Release notes](https://github.com/wntrblm/nox/releases)
- [Changelog](https://github.com/wntrblm/nox/blob/main/CHANGELOG.md)
- [Commits](https://github.com/wntrblm/nox/compare/2026.02.09...2026.04.10)

---
updated-dependencies:
- dependency-name: nox
  dependency-version: 2026.4.10
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([43bd21d](https://github.com/alexeev-prog/nadzoring/commit/43bd21dc70d44ff297016debc818bee713c82aac))
- Build(deps-dev): bump nox from 2026.2.9 to 2026.4.10 (#113)([b6d1984](https://github.com/alexeev-prog/nadzoring/commit/b6d198406463b6d5a41e31987a2e6af00b0ea8fa))
- Build(deps-dev): bump pyrefly from 0.60.1 to 0.60.2

Bumps [pyrefly](https://github.com/facebook/pyrefly) from 0.60.1 to 0.60.2.
- [Release notes](https://github.com/facebook/pyrefly/releases)
- [Commits](https://github.com/facebook/pyrefly/compare/0.60.1...0.60.2)

---
updated-dependencies:
- dependency-name: pyrefly
  dependency-version: 0.60.2
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([2c63872](https://github.com/alexeev-prog/nadzoring/commit/2c638724512672e2bfec466b606f4cb1bd69b14b))
- Build(deps-dev): bump pyrefly from 0.60.1 to 0.60.2 (#114)([b5fcda1](https://github.com/alexeev-prog/nadzoring/commit/b5fcda18d945e74491e680324642cd468f4ce02f))
- Build(deps-dev): bump mypy from 1.20.0 to 1.20.1

Bumps [mypy](https://github.com/python/mypy) from 1.20.0 to 1.20.1.
- [Changelog](https://github.com/python/mypy/blob/master/CHANGELOG.md)
- [Commits](https://github.com/python/mypy/compare/v1.20.0...v1.20.1)

---
updated-dependencies:
- dependency-name: mypy
  dependency-version: 1.20.1
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([c8d0810](https://github.com/alexeev-prog/nadzoring/commit/c8d0810e3722b9885056f609603509996249a808))
- Build(deps-dev): bump pyrefly from 0.60.2 to 0.61.0

Bumps [pyrefly](https://github.com/facebook/pyrefly) from 0.60.2 to 0.61.0.
- [Release notes](https://github.com/facebook/pyrefly/releases)
- [Commits](https://github.com/facebook/pyrefly/compare/0.60.2...0.61.0)

---
updated-dependencies:
- dependency-name: pyrefly
  dependency-version: 0.61.0
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([a253627](https://github.com/alexeev-prog/nadzoring/commit/a2536271f18c07107986f5c9808f178d0731e7a2))
- Build(deps-dev): bump pyrefly from 0.60.2 to 0.61.0 (#116)([5d18a2b](https://github.com/alexeev-prog/nadzoring/commit/5d18a2bbacb86c2ad2e5df066373b68537ef2f5e))
- Build(deps-dev): bump mypy from 1.20.0 to 1.20.1 (#115)([472dd1a](https://github.com/alexeev-prog/nadzoring/commit/472dd1a2881a6d0a33c759118ab62ffe4711d644))
- Build(deps): bump astral-sh/setup-uv from 8.0.0 to 8.1.0

Bumps [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) from 8.0.0 to 8.1.0.
- [Release notes](https://github.com/astral-sh/setup-uv/releases)
- [Commits](https://github.com/astral-sh/setup-uv/compare/v8.0.0...v8.1.0)

---
updated-dependencies:
- dependency-name: astral-sh/setup-uv
  dependency-version: 8.1.0
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([b1080f4](https://github.com/alexeev-prog/nadzoring/commit/b1080f4970ccf98e78fdaad7a31832c2f68ae105))
- Build(deps): bump astral-sh/setup-uv from 8.0.0 to 8.1.0 (#117)([a9bd69c](https://github.com/alexeev-prog/nadzoring/commit/a9bd69c4511033334314d05471257fc7d72471a1))
- Build(deps-dev): bump ruff from 0.15.10 to 0.15.11

Bumps [ruff](https://github.com/astral-sh/ruff) from 0.15.10 to 0.15.11.
- [Release notes](https://github.com/astral-sh/ruff/releases)
- [Changelog](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md)
- [Commits](https://github.com/astral-sh/ruff/compare/0.15.10...0.15.11)

---
updated-dependencies:
- dependency-name: ruff
  dependency-version: 0.15.11
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([6622726](https://github.com/alexeev-prog/nadzoring/commit/662272633b0cfd81b35e6bcfb608c10246d41470))
- Build(deps-dev): bump basedpyright from 1.39.0 to 1.39.2

Bumps [basedpyright](https://github.com/detachhead/basedpyright) from 1.39.0 to 1.39.2.
- [Release notes](https://github.com/detachhead/basedpyright/releases)
- [Commits](https://github.com/detachhead/basedpyright/compare/v1.39.0...v1.39.2)

---
updated-dependencies:
- dependency-name: basedpyright
  dependency-version: 1.39.2
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([f664748](https://github.com/alexeev-prog/nadzoring/commit/f664748e5864389506c43107ff8079c25631b992))
- Build(deps-dev): bump basedpyright from 1.39.0 to 1.39.2 (#118)([fe0dc5e](https://github.com/alexeev-prog/nadzoring/commit/fe0dc5e60f42457e07d6e360ff7f759ec2987798))
- Build(deps-dev): bump ruff from 0.15.10 to 0.15.11 (#119)([be9d918](https://github.com/alexeev-prog/nadzoring/commit/be9d9185714b01c8527fb09e6f4761d40d5acf46))
- Build(deps-dev): bump basedpyright from 1.39.2 to 1.39.3

Bumps [basedpyright](https://github.com/detachhead/basedpyright) from 1.39.2 to 1.39.3.
- [Release notes](https://github.com/detachhead/basedpyright/releases)
- [Commits](https://github.com/detachhead/basedpyright/compare/v1.39.2...v1.39.3)

---
updated-dependencies:
- dependency-name: basedpyright
  dependency-version: 1.39.3
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([369f85a](https://github.com/alexeev-prog/nadzoring/commit/369f85a8b9a0724431d9f5d71ddee673382121cc))
- Build(deps-dev): bump pyrefly from 0.61.0 to 0.62.0

Bumps [pyrefly](https://github.com/facebook/pyrefly) from 0.61.0 to 0.62.0.
- [Release notes](https://github.com/facebook/pyrefly/releases)
- [Commits](https://github.com/facebook/pyrefly/compare/0.61.0...0.62.0)

---
updated-dependencies:
- dependency-name: pyrefly
  dependency-version: 0.62.0
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([a1db110](https://github.com/alexeev-prog/nadzoring/commit/a1db1108f7eee07082f548ad7fb7aaac9f603bbb))
- Build(deps-dev): bump pyrefly from 0.61.0 to 0.62.0 (#121)([d5b11df](https://github.com/alexeev-prog/nadzoring/commit/d5b11df4ddc899b96dfce9876a185025e9504955))
- Build(deps-dev): bump basedpyright from 1.39.2 to 1.39.3 (#122)([7815bab](https://github.com/alexeev-prog/nadzoring/commit/7815bab7c3ef8275cd145bd1dfac53e994549380))
- Build(deps): bump certifi from 2026.2.25 to 2026.4.22

Bumps [certifi](https://github.com/certifi/python-certifi) from 2026.2.25 to 2026.4.22.
- [Commits](https://github.com/certifi/python-certifi/compare/2026.02.25...2026.04.22)

---
updated-dependencies:
- dependency-name: certifi
  dependency-version: 2026.4.22
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([8c2013e](https://github.com/alexeev-prog/nadzoring/commit/8c2013e990a0590475c4bda895acc80f69fe6d2f))
- Build(deps): bump click from 8.3.2 to 8.3.3

Bumps [click](https://github.com/pallets/click) from 8.3.2 to 8.3.3.
- [Release notes](https://github.com/pallets/click/releases)
- [Changelog](https://github.com/pallets/click/blob/main/CHANGES.rst)
- [Commits](https://github.com/pallets/click/compare/8.3.2...8.3.3)

---
updated-dependencies:
- dependency-name: click
  dependency-version: 8.3.3
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([8c8b8f3](https://github.com/alexeev-prog/nadzoring/commit/8c8b8f3c2662e22e21c23f92112e57581f6613c7))
- Build(deps-dev): bump mypy from 1.20.1 to 1.20.2

Bumps [mypy](https://github.com/python/mypy) from 1.20.1 to 1.20.2.
- [Changelog](https://github.com/python/mypy/blob/master/CHANGELOG.md)
- [Commits](https://github.com/python/mypy/compare/v1.20.1...v1.20.2)

---
updated-dependencies:
- dependency-name: mypy
  dependency-version: 1.20.2
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([620c931](https://github.com/alexeev-prog/nadzoring/commit/620c931bc9d585a13876c6557ca412e3460f1473))
- Build(deps-dev): bump mypy from 1.20.1 to 1.20.2 (#123)([9f14f6c](https://github.com/alexeev-prog/nadzoring/commit/9f14f6ced85beacce4c8d4d12ec17c94a12ab541))
- Build(deps): bump click from 8.3.2 to 8.3.3 (#125)([0deb673](https://github.com/alexeev-prog/nadzoring/commit/0deb673c1a569caacb490762b3865b1cbfeb2018))
- Build(deps): bump certifi from 2026.2.25 to 2026.4.22 (#124)([483a926](https://github.com/alexeev-prog/nadzoring/commit/483a9264a821d73272bf4a412e6f090f7a906271))
- Build(deps-dev): bump ruff from 0.15.11 to 0.15.12

Bumps [ruff](https://github.com/astral-sh/ruff) from 0.15.11 to 0.15.12.
- [Release notes](https://github.com/astral-sh/ruff/releases)
- [Changelog](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md)
- [Commits](https://github.com/astral-sh/ruff/compare/0.15.11...0.15.12)

---
updated-dependencies:
- dependency-name: ruff
  dependency-version: 0.15.12
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([b04e28a](https://github.com/alexeev-prog/nadzoring/commit/b04e28add7e723f533c957bf4e4571afe821f259))
- Build(deps-dev): bump pyrefly from 0.62.0 to 0.63.1

Bumps [pyrefly](https://github.com/facebook/pyrefly) from 0.62.0 to 0.63.1.
- [Release notes](https://github.com/facebook/pyrefly/releases)
- [Commits](https://github.com/facebook/pyrefly/compare/0.62.0...0.63.1)

---
updated-dependencies:
- dependency-name: pyrefly
  dependency-version: 0.63.1
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([8826155](https://github.com/alexeev-prog/nadzoring/commit/88261557dc629754890780fed778ec5c5a2fc3ac))
- Build(deps-dev): bump git-cliff from 2.12.0 to 2.13.1

Bumps [git-cliff](https://github.com/orhun/git-cliff) from 2.12.0 to 2.13.1.
- [Release notes](https://github.com/orhun/git-cliff/releases)
- [Changelog](https://github.com/orhun/git-cliff/blob/main/CHANGELOG.md)
- [Commits](https://github.com/orhun/git-cliff/compare/v2.12.0...v2.13.1)

---
updated-dependencies:
- dependency-name: git-cliff
  dependency-version: 2.13.1
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([9ebd1a5](https://github.com/alexeev-prog/nadzoring/commit/9ebd1a5467f061165ed0798f3ae4cc5fd3da582a))
- Build(deps): bump cryptography from 46.0.7 to 47.0.0

Bumps [cryptography](https://github.com/pyca/cryptography) from 46.0.7 to 47.0.0.
- [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/pyca/cryptography/compare/46.0.7...47.0.0)

---
updated-dependencies:
- dependency-name: cryptography
  dependency-version: 47.0.0
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([c82c98b](https://github.com/alexeev-prog/nadzoring/commit/c82c98baa538d25697de01c93706503b20caf0a8))
- Build(deps): bump cryptography from 46.0.7 to 47.0.0 (#126)([b0787a4](https://github.com/alexeev-prog/nadzoring/commit/b0787a47a5f8ff2e5cd413fe05993da2f968bbe8))
- Build(deps-dev): bump git-cliff from 2.12.0 to 2.13.1 (#127)([c438018](https://github.com/alexeev-prog/nadzoring/commit/c43801897a0353744c573b8b73ee2af6fc7d9288))
- Build(deps-dev): bump pyrefly from 0.62.0 to 0.63.1 (#130)([4793f51](https://github.com/alexeev-prog/nadzoring/commit/4793f51af7b8b8755640864784f148f707da6f52))
- Build(deps-dev): bump ruff from 0.15.11 to 0.15.12 (#128)([1b27702](https://github.com/alexeev-prog/nadzoring/commit/1b2770235be2fcd1c2b59b84c8b4b954d244351a))
- Build(deps-dev): bump types-requests

Bumps [types-requests](https://github.com/python/typeshed) from 2.33.0.20260408 to 2.33.0.20260503.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-requests
  dependency-version: 2.33.0.20260503
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([7c04860](https://github.com/alexeev-prog/nadzoring/commit/7c04860d5f61b4d9260b730c9c855205373f614d))
- Build(deps-dev): bump types-requests from 2.33.0.20260408 to 2.33.0.20260503 (#131)([512de42](https://github.com/alexeev-prog/nadzoring/commit/512de424f8dd9e9c5f8134d4cc98efae9e201d00))
- Build(deps): bump cryptography from 47.0.0 to 48.0.0

Bumps [cryptography](https://github.com/pyca/cryptography) from 47.0.0 to 48.0.0.
- [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/pyca/cryptography/compare/47.0.0...48.0.0)

---
updated-dependencies:
- dependency-name: cryptography
  dependency-version: 48.0.0
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([ace1abc](https://github.com/alexeev-prog/nadzoring/commit/ace1abc612df88bcffbf38410db9d8110a762d70))
- Build(deps): bump cryptography from 47.0.0 to 48.0.0 (#133)([3b66909](https://github.com/alexeev-prog/nadzoring/commit/3b669094aa8850b3825dd31cf00f180ab63cdc87))
- Build(deps-dev): bump mypy from 1.20.2 to 2.0.0

Bumps [mypy](https://github.com/python/mypy) from 1.20.2 to 2.0.0.
- [Changelog](https://github.com/python/mypy/blob/master/CHANGELOG.md)
- [Commits](https://github.com/python/mypy/compare/v1.20.2...v2.0.0)

---
updated-dependencies:
- dependency-name: mypy
  dependency-version: 2.0.0
  dependency-type: direct:development
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([fc7ea34](https://github.com/alexeev-prog/nadzoring/commit/fc7ea34e9e93e478c7e4c985871a6d9c2a72cbec))
- Build(deps-dev): bump pyrefly from 0.63.1 to 0.64.0

Bumps [pyrefly](https://github.com/facebook/pyrefly) from 0.63.1 to 0.64.0.
- [Release notes](https://github.com/facebook/pyrefly/releases)
- [Commits](https://github.com/facebook/pyrefly/compare/0.63.1...0.64.0)

---
updated-dependencies:
- dependency-name: pyrefly
  dependency-version: 0.64.0
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([a4d8fc3](https://github.com/alexeev-prog/nadzoring/commit/a4d8fc37910ee33e43b942eb02bbef38330ed55d))
- Build(deps-dev): bump pyrefly from 0.63.1 to 0.64.0 (#134)([d70c201](https://github.com/alexeev-prog/nadzoring/commit/d70c201bebac4f1b750b86351605df0bf76b5f74))
- Build(deps-dev): bump mypy from 1.20.2 to 2.0.0 (#135)([bc191c9](https://github.com/alexeev-prog/nadzoring/commit/bc191c9e757b0d3072107389a843471c8e96c7df))
- Build(deps-dev): bump mypy from 2.0.0 to 2.1.0

Bumps [mypy](https://github.com/python/mypy) from 2.0.0 to 2.1.0.
- [Changelog](https://github.com/python/mypy/blob/master/CHANGELOG.md)
- [Commits](https://github.com/python/mypy/compare/v2.0.0...v2.1.0)

---
updated-dependencies:
- dependency-name: mypy
  dependency-version: 2.1.0
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([1a291e2](https://github.com/alexeev-prog/nadzoring/commit/1a291e203bca2d76ae3b001ac7d1a5f7cd70e25f))
- Build(deps): bump pandas from 3.0.2 to 3.0.3

Bumps [pandas](https://github.com/pandas-dev/pandas) from 3.0.2 to 3.0.3.
- [Release notes](https://github.com/pandas-dev/pandas/releases)
- [Commits](https://github.com/pandas-dev/pandas/compare/v3.0.2...v3.0.3)

---
updated-dependencies:
- dependency-name: pandas
  dependency-version: 3.0.3
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([88833a1](https://github.com/alexeev-prog/nadzoring/commit/88833a1e789279a0b4e61409a6f866e82f7088be))
- Build(deps-dev): bump types-pysocks

Bumps [types-pysocks](https://github.com/python/typeshed) from 1.7.1.20260408 to 1.7.1.20260508.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-pysocks
  dependency-version: 1.7.1.20260508
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([a0b1567](https://github.com/alexeev-prog/nadzoring/commit/a0b15675ce71dccd6ecb55aebc7e10c01d490867))
- Build(deps-dev): bump types-pyyaml

Bumps [types-pyyaml](https://github.com/python/typeshed) from 6.0.12.20260408 to 6.0.12.20260510.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-pyyaml
  dependency-version: 6.0.12.20260510
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([78aa79f](https://github.com/alexeev-prog/nadzoring/commit/78aa79f5575b39222bc621f45589831d562ff70d))
- Build(deps-dev): bump types-tabulate

Bumps [types-tabulate](https://github.com/python/typeshed) from 0.10.0.20260408 to 0.10.0.20260508.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-tabulate
  dependency-version: 0.10.0.20260508
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([b113423](https://github.com/alexeev-prog/nadzoring/commit/b11342348c2a3366837186fe174856908e710a9b))
- Build(deps-dev): bump types-tqdm from 4.67.3.20260408 to 4.67.3.20260508

Bumps [types-tqdm](https://github.com/python/typeshed) from 4.67.3.20260408 to 4.67.3.20260508.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-tqdm
  dependency-version: 4.67.3.20260508
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([ec5c9c6](https://github.com/alexeev-prog/nadzoring/commit/ec5c9c68aff94ef2e11d8ab3d4eff82c41661a36))
- Build(deps-dev): bump basedpyright from 1.39.3 to 1.39.4

Bumps [basedpyright](https://github.com/detachhead/basedpyright) from 1.39.3 to 1.39.4.
- [Release notes](https://github.com/detachhead/basedpyright/releases)
- [Commits](https://github.com/detachhead/basedpyright/compare/v1.39.3...v1.39.4)

---
updated-dependencies:
- dependency-name: basedpyright
  dependency-version: 1.39.4
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([c573529](https://github.com/alexeev-prog/nadzoring/commit/c5735294705e49249f6001de8e361b9d04d7a639))
- Build(deps-dev): bump types-requests

Bumps [types-requests](https://github.com/python/typeshed) from 2.33.0.20260503 to 2.33.0.20260513.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-requests
  dependency-version: 2.33.0.20260513
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([c085b5a](https://github.com/alexeev-prog/nadzoring/commit/c085b5ac83ee0e313a1a27c2e3c062ed7b23b0ac))
- Build(deps-dev): bump pyrefly from 0.64.0 to 1.0.0

Bumps [pyrefly](https://github.com/facebook/pyrefly) from 0.64.0 to 1.0.0.
- [Release notes](https://github.com/facebook/pyrefly/releases)
- [Commits](https://github.com/facebook/pyrefly/compare/0.64.0...1.0.0)

---
updated-dependencies:
- dependency-name: pyrefly
  dependency-version: 1.0.0
  dependency-type: direct:development
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([f34b887](https://github.com/alexeev-prog/nadzoring/commit/f34b8879fde64ef10342b11fc6354658f3a4139b))
- Build(deps-dev): bump ruff from 0.15.12 to 0.15.13

Bumps [ruff](https://github.com/astral-sh/ruff) from 0.15.12 to 0.15.13.
- [Release notes](https://github.com/astral-sh/ruff/releases)
- [Changelog](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md)
- [Commits](https://github.com/astral-sh/ruff/compare/0.15.12...0.15.13)

---
updated-dependencies:
- dependency-name: ruff
  dependency-version: 0.15.13
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([f57961d](https://github.com/alexeev-prog/nadzoring/commit/f57961d81637226a117a38f4d1025e16cdba12ba))
- Build(deps): bump actions/checkout from 4 to 7.0.0

Bumps [actions/checkout](https://github.com/actions/checkout) from 4 to 7.0.0.
- [Release notes](https://github.com/actions/checkout/releases)
- [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
- [Commits](https://github.com/actions/checkout/compare/v4...v7)

---
updated-dependencies:
- dependency-name: actions/checkout
  dependency-version: 7.0.0
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([b4b21d0](https://github.com/alexeev-prog/nadzoring/commit/b4b21d0ce1875840b767cee342c585b3d5ff6451))
- Build(deps): bump actions/setup-python from 6 to 7

Bumps [actions/setup-python](https://github.com/actions/setup-python) from 6 to 7.
- [Release notes](https://github.com/actions/setup-python/releases)
- [Commits](https://github.com/actions/setup-python/compare/v6...v7)

---
updated-dependencies:
- dependency-name: actions/setup-python
  dependency-version: '7'
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([3fd8096](https://github.com/alexeev-prog/nadzoring/commit/3fd8096bdcbd92d94b4cc4b1393550f77553c427))
- Build(deps): bump astral-sh/setup-uv from 8.1.0 to 9.0.0

Bumps [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) from 8.1.0 to 9.0.0.
- [Release notes](https://github.com/astral-sh/setup-uv/releases)
- [Commits](https://github.com/astral-sh/setup-uv/compare/v8.1.0...v9.0.0)

---
updated-dependencies:
- dependency-name: astral-sh/setup-uv
  dependency-version: 9.0.0
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([d069ad3](https://github.com/alexeev-prog/nadzoring/commit/d069ad3a15bf098b0eb5e37f6f3a379d0eb1b107))
- Build(deps): bump astral-sh/setup-uv from 8.1.0 to 9.0.0 (#159)([f6de7a2](https://github.com/alexeev-prog/nadzoring/commit/f6de7a2146206dc277296da65945adef1aac6501))
- Build(deps): bump actions/setup-python from 6 to 7 (#158)([e0b80ce](https://github.com/alexeev-prog/nadzoring/commit/e0b80ce96415f3ffdf386ea63981bd6de41b92cc))
- Build(deps): bump astral-sh/setup-uv from 9.0.0 to 10.3.0

Bumps [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) from 9.0.0 to 10.3.0.
- [Release notes](https://github.com/astral-sh/setup-uv/releases)
- [Commits](https://github.com/astral-sh/setup-uv/compare/v9.0.0...v10.3.0)

---
updated-dependencies:
- dependency-name: astral-sh/setup-uv
  dependency-version: 10.3.0
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([542e8a2](https://github.com/alexeev-prog/nadzoring/commit/542e8a232ab26076602e76e4d979d967f9dce305))
- Build(deps): bump astral-sh/setup-uv from 9.0.0 to 10.3.0 (#162)([431bc74](https://github.com/alexeev-prog/nadzoring/commit/431bc74a078c2d4735de3fe432c93c0b18774f86))
- Build(deps): bump actions/checkout from 4 to 7.0.0 (#157)([6d70909](https://github.com/alexeev-prog/nadzoring/commit/6d70909fbf007d2e3ec1f78e000f3b9e0de0275a))
- Build(deps-dev): bump ruff from 0.15.12 to 0.15.13 (#147)([f68ab08](https://github.com/alexeev-prog/nadzoring/commit/f68ab0855c2d7e566077f7ccd910f8371c72879b))
- Build(deps-dev): bump pyrefly from 0.64.0 to 1.0.0 (#146)([cc0d3db](https://github.com/alexeev-prog/nadzoring/commit/cc0d3dbc18ee5fdf35a7f91d83a7b20de14c16cb))
- Build(deps-dev): bump types-requests from 2.33.0.20260503 to 2.33.0.20260513 (#145)([c22d186](https://github.com/alexeev-prog/nadzoring/commit/c22d1861efebfa27da9724fc471431143c076eda))
- Build(deps-dev): bump basedpyright from 1.39.3 to 1.39.4 (#144)([2fab802](https://github.com/alexeev-prog/nadzoring/commit/2fab8025fdffa887d7ea40048c509ef0cff19297))
- Build(deps-dev): bump types-tqdm from 4.67.3.20260408 to 4.67.3.20260508 (#141)([3e632c3](https://github.com/alexeev-prog/nadzoring/commit/3e632c32884f4fa012be68e8e96e34403e7fb5e3))
- Build(deps-dev): bump types-tabulate from 0.10.0.20260408 to 0.10.0.20260508 (#139)([ee92f84](https://github.com/alexeev-prog/nadzoring/commit/ee92f84509369cf420b5b047edb0f5f3ec8a7f5b))
- Build(deps-dev): bump types-pyyaml from 6.0.12.20260408 to 6.0.12.20260510 (#138)([800c978](https://github.com/alexeev-prog/nadzoring/commit/800c9784efb9bf75522d30756c77e71dc3df68bf))
- Build(deps-dev): bump types-pysocks from 1.7.1.20260408 to 1.7.1.20260508 (#137)([3870a12](https://github.com/alexeev-prog/nadzoring/commit/3870a1287555a180c51ea96c052f660b94e29ebb))
- Build(deps): bump pandas from 3.0.2 to 3.0.3 (#143)([0cc5d61](https://github.com/alexeev-prog/nadzoring/commit/0cc5d61baccc21f64fb1d99e815bd1fdcffec1ff))
- Build(deps-dev): bump mypy from 2.0.0 to 2.1.0 (#142)([292f183](https://github.com/alexeev-prog/nadzoring/commit/292f183cee635e810e00a557104eea1690502eea))
- Build(deps-dev): bump basedpyright from 1.39.4 to 1.40.2

Bumps [basedpyright](https://github.com/detachhead/basedpyright) from 1.39.4 to 1.40.2.
- [Release notes](https://github.com/detachhead/basedpyright/releases)
- [Commits](https://github.com/detachhead/basedpyright/compare/v1.39.4...v1.40.2)

---
updated-dependencies:
- dependency-name: basedpyright
  dependency-version: 1.40.2
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([c9f24e5](https://github.com/alexeev-prog/nadzoring/commit/c9f24e5f837bf0e4a60411123491bbc8f7df6bdb))
- Build(deps): bump scapy from 2.7.0 to 2.8.0

Bumps [scapy](https://github.com/secdev/scapy) from 2.7.0 to 2.8.0.
- [Release notes](https://github.com/secdev/scapy/releases)
- [Commits](https://github.com/secdev/scapy/compare/v2.7.0...v2.8.0)

---
updated-dependencies:
- dependency-name: scapy
  dependency-version: 2.8.0
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([5928e9d](https://github.com/alexeev-prog/nadzoring/commit/5928e9de9066ec509e815193c1843b9bb1406143))
- Build(deps): bump scapy from 2.7.0 to 2.8.0 (#170)([e56d996](https://github.com/alexeev-prog/nadzoring/commit/e56d9968b47776ba1e86124052a613ae84710fb4))
- Build(deps-dev): bump basedpyright from 1.39.4 to 1.40.2 (#169)([3a8bcdd](https://github.com/alexeev-prog/nadzoring/commit/3a8bcdd3ed27091b808848f48afcdcabf65a4a92))
- Build(deps): bump astral-sh/setup-uv from 10.3.0 to 10.3.1

Bumps [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) from 10.3.0 to 10.3.1.
- [Release notes](https://github.com/astral-sh/setup-uv/releases)
- [Commits](https://github.com/astral-sh/setup-uv/compare/v10.3.0...v10.3.1)

---
updated-dependencies:
- dependency-name: astral-sh/setup-uv
  dependency-version: 10.3.1
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([8622a04](https://github.com/alexeev-prog/nadzoring/commit/8622a04d9a7ababc2d91ab52c9529a288a631c98))
- Build(deps-dev): bump types-tqdm from 4.67.3.20260508 to 4.70.0.20260906

Bumps [types-tqdm](https://github.com/python/typeshed) from 4.67.3.20260508 to 4.70.0.20260906.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-tqdm
  dependency-version: 4.70.0.20260906
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([43747df](https://github.com/alexeev-prog/nadzoring/commit/43747dfd573c7d42625ea2110cd043262e48e846))
- Build(deps-dev): bump pyrefly from 1.0.0 to 1.4.0

Bumps [pyrefly](https://github.com/facebook/pyrefly) from 1.0.0 to 1.4.0.
- [Release notes](https://github.com/facebook/pyrefly/releases)
- [Commits](https://github.com/facebook/pyrefly/compare/1.0.0...1.4.0)

---
updated-dependencies:
- dependency-name: pyrefly
  dependency-version: 1.4.0
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([9bcd80b](https://github.com/alexeev-prog/nadzoring/commit/9bcd80b5b9560ecb8aa650565bdae8e4aa0557ea))
- Build(deps-dev): bump types-pyyaml

Bumps [types-pyyaml](https://github.com/python/typeshed) from 6.0.12.20260510 to 6.0.12.20260906.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-pyyaml
  dependency-version: 6.0.12.20260906
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([0476efe](https://github.com/alexeev-prog/nadzoring/commit/0476efefa333bfe2b62797faf35264eb04170cc4))
- Build(deps): bump tqdm from 4.67.3 to 4.70.1

Bumps [tqdm](https://github.com/tqdm/tqdm) from 4.67.3 to 4.70.1.
- [Release notes](https://github.com/tqdm/tqdm/releases)
- [Commits](https://github.com/tqdm/tqdm/compare/v4.67.3...v4.70.1)

---
updated-dependencies:
- dependency-name: tqdm
  dependency-version: 4.70.1
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([9f6f85f](https://github.com/alexeev-prog/nadzoring/commit/9f6f85f3f467f19d0bc14ce8e1a7b34b6b4c27c4))
- Build(deps): bump tqdm from 4.67.3 to 4.70.1 (#168)([e91436a](https://github.com/alexeev-prog/nadzoring/commit/e91436a76b810943b842eb0fafaffa85886a7af1))
- Build(deps-dev): bump types-pyyaml from 6.0.12.20260510 to 6.0.12.20260906 (#167)([8b57759](https://github.com/alexeev-prog/nadzoring/commit/8b57759addea7e1f4c1803df7d56ec5f47e70f40))
- Build(deps-dev): bump pyrefly from 1.0.0 to 1.4.0 (#166)([f714a10](https://github.com/alexeev-prog/nadzoring/commit/f714a10c476ff615dca7bb77385f582c514d5cc2))
- Build(deps-dev): bump types-tqdm from 4.67.3.20260508 to 4.70.0.20260906 (#165)([8bea363](https://github.com/alexeev-prog/nadzoring/commit/8bea363fa7e34f50258be0aa8ca8726cc1a73039))
- Build(deps): bump astral-sh/setup-uv from 10.3.0 to 10.3.1 (#164)([8d2ba1a](https://github.com/alexeev-prog/nadzoring/commit/8d2ba1a9d8550513d1db29212e2cd9c9ff731838))

### Dependencies

- Bump dev-version([0f86ee3](https://github.com/alexeev-prog/nadzoring/commit/0f86ee351f341e285627289b35aa35483f9e0761))

### Documentation

- Docs: update CHANGELOG.md for v0.2.2 [skip ci]([4de773f](https://github.com/alexeev-prog/nadzoring/commit/4de773fe4d024ea2e0e86b40e5fdc4bb6a502375))
- Docs: document keyword-only connector args; align tests and examples

Update plugin tests to pass explicit keyword flags for connectors that use
kw_only fields; add coverage for WHOIS, email security, subdomain scan, SSL
full mode, and registry.build forwarding. Extend plugins.rst and package
docstrings with registry examples that register all used connectors.

Co-authored-by: Cursor <cursoragent@cursor.com>([13604db](https://github.com/alexeev-prog/nadzoring/commit/13604db69e2c7258976a8783be86209fc8483a27))
- Docs: add LLM-friendly documentation([fe3ed02](https://github.com/alexeev-prog/nadzoring/commit/fe3ed0219d878c64f1740f16aff28a0d2025ce73))
- Docs: update llms-full documentation([b6505e3](https://github.com/alexeev-prog/nadzoring/commit/b6505e3d36ea3f6afa85d2fa6309c62d0c5a7683))
- Docs: add LLM-friendly documentation (#160)([6f70bdb](https://github.com/alexeev-prog/nadzoring/commit/6f70bdb8ebd85d6e27fd42768ece2dd0fdf93fb7))
- Docs: fix poly([67fe9d7](https://github.com/alexeev-prog/nadzoring/commit/67fe9d7f04e838b53743b9b35cddefcaf1d5cc9c))

### Features

- Feat: add plugin connector framework with tests and docs

Co-authored-by: Cursor <cursoragent@cursor.com>([d6dc7e5](https://github.com/alexeev-prog/nadzoring/commit/d6dc7e5260bca01d7519f676a5484c2737864b18))
- Feat: add plugin connector framework with tests and docs (#132)

closes #51([b9eff6f](https://github.com/alexeev-prog/nadzoring/commit/b9eff6f02ac5cc23f114b8e7dc0150e539773264))
- Add interactive shell (issue 109) with tests([872fc63](https://github.com/alexeev-prog/nadzoring/commit/872fc634e89f9397534662b3cc53e8f727f07523))
- Add interactive shell (issue 109) with tests (#163)([0aafdc4](https://github.com/alexeev-prog/nadzoring/commit/0aafdc4144051b7bfffae4a771d242873cf32099))
- Add core command group (issue 91)([0aae0b5](https://github.com/alexeev-prog/nadzoring/commit/0aae0b506350b249c24bff51739a59620a78b2a0))
- Add core command group (issue 91) (#171)([414ea9b](https://github.com/alexeev-prog/nadzoring/commit/414ea9bed07f710f093424e423c93eee89e2ae05))

### Other Changes

- Update gitignore([833de83](https://github.com/alexeev-prog/nadzoring/commit/833de83e524b2c55820c6b20a21e4232fbb7e737))
- Achieve 100% tests coverage([d2b2e48](https://github.com/alexeev-prog/nadzoring/commit/d2b2e487ae47b06a9dbe76fed1e637c7a864f49c))
- Achive 100% test coverage with codestyle([0d220b1](https://github.com/alexeev-prog/nadzoring/commit/0d220b18339db993627ad5b5dd4b8ea2f2b6f198))
- Achieve 100% tests coverage (#172)([6bb2530](https://github.com/alexeev-prog/nadzoring/commit/6bb25302ed8a93b89a3f241b6555c3db58ca76d1))
- Update readme([2bbd81b](https://github.com/alexeev-prog/nadzoring/commit/2bbd81b048f44f15346569f81f133ec3c49bcdb2))
## [0.2.2](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.2.2) - 2026-04-19

### Bug Fixes

- Fix DNS health scoring broken and fix whois_lookup always reports 'Command not found'([bbc5406](https://github.com/alexeev-prog/nadzoring/commit/bbc54069f7f88d8b280dce15447fd9f25ac4a1fd))
- Fix code-issues with error handling (from review)([3ce1131](https://github.com/alexeev-prog/nadzoring/commit/3ce113115108c51b1cd3b5618b575fb8dbe27ce5))
- Fix: apply CodeRabbit auto-fixes

Fixed 1 file(s) based on 3 unresolved review comments.

Co-authored-by: CodeRabbit <noreply@coderabbit.ai>([bfd3349](https://github.com/alexeev-prog/nadzoring/commit/bfd334955e563ab28928ea9dacdfaa5a4bc525a9))
- Fix whois-lookup output([2710e6b](https://github.com/alexeev-prog/nadzoring/commit/2710e6b6db970ead0b9f9822d979097666c0dbc9))
- Fix whois-lookup output([7b3134a](https://github.com/alexeev-prog/nadzoring/commit/7b3134a8ff9fe131d963177ee237c618703f04f3))
- Fix error-handling issues([3475446](https://github.com/alexeev-prog/nadzoring/commit/3475446a2280698180b676f6fd6b0e9ec1d82f99))
- Fix: add requests support for proxies([e166736](https://github.com/alexeev-prog/nadzoring/commit/e1667366103c4bb0b09b13bad4e52dc9bbec648b))

### Build System

- Build(deps): bump click from 8.3.1 to 8.3.2

Bumps [click](https://github.com/pallets/click) from 8.3.1 to 8.3.2.
- [Release notes](https://github.com/pallets/click/releases)
- [Changelog](https://github.com/pallets/click/blob/main/CHANGES.rst)
- [Commits](https://github.com/pallets/click/compare/8.3.1...8.3.2)

---
updated-dependencies:
- dependency-name: click
  dependency-version: 8.3.2
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([3eeeebb](https://github.com/alexeev-prog/nadzoring/commit/3eeeebb16ee2cddb68c2c80e8fbcec6edc5977bd))
- Build(deps): bump click from 8.3.1 to 8.3.2 (#90)([0e5bc78](https://github.com/alexeev-prog/nadzoring/commit/0e5bc7839066a9f8ae00b48ea678c0313b21e774))
- Build(deps-dev): bump pyrefly from 0.59.1 to 0.60.0

Bumps [pyrefly](https://github.com/facebook/pyrefly) from 0.59.1 to 0.60.0.
- [Release notes](https://github.com/facebook/pyrefly/releases)
- [Commits](https://github.com/facebook/pyrefly/compare/0.59.1...0.60.0)

---
updated-dependencies:
- dependency-name: pyrefly
  dependency-version: 0.60.0
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([082049f](https://github.com/alexeev-prog/nadzoring/commit/082049fe68fb83d96ea31e429bf97ffee265b6b1))
- Build(deps-dev): bump pyrefly from 0.59.1 to 0.60.0 (#95)([c80893d](https://github.com/alexeev-prog/nadzoring/commit/c80893d50afdb1861aeb37b160124fb2941b805b))
- Build(deps): bump actions/upload-pages-artifact from 4 to 5

Bumps [actions/upload-pages-artifact](https://github.com/actions/upload-pages-artifact) from 4 to 5.
- [Release notes](https://github.com/actions/upload-pages-artifact/releases)
- [Commits](https://github.com/actions/upload-pages-artifact/compare/v4...v5)

---
updated-dependencies:
- dependency-name: actions/upload-pages-artifact
  dependency-version: '5'
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([09a00cf](https://github.com/alexeev-prog/nadzoring/commit/09a00cf9a2243129d1b7610bd608846f8e3750df))
- Build(deps): bump actions/upload-pages-artifact from 4 to 5 (#98)([0369c14](https://github.com/alexeev-prog/nadzoring/commit/0369c149c46f61512c2aa79d5dca05fc16efb6b7))
- Build(deps): bump cryptography from 46.0.6 to 46.0.7 (#99)

Bumps [cryptography](https://github.com/pyca/cryptography) from 46.0.6 to 46.0.7.
- [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/pyca/cryptography/compare/46.0.6...46.0.7)

---
updated-dependencies:
- dependency-name: cryptography
  dependency-version: 46.0.7
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>([ca9b882](https://github.com/alexeev-prog/nadzoring/commit/ca9b8824f692d5b2b9d44730eaa47a029f1dfa5c))
- Build(deps-dev): bump pytest from 9.0.2 to 9.0.3 (#100)

Bumps [pytest](https://github.com/pytest-dev/pytest) from 9.0.2 to 9.0.3.
- [Release notes](https://github.com/pytest-dev/pytest/releases)
- [Changelog](https://github.com/pytest-dev/pytest/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/pytest-dev/pytest/compare/9.0.2...9.0.3)

---
updated-dependencies:
- dependency-name: pytest
  dependency-version: 9.0.3
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>([e1c3259](https://github.com/alexeev-prog/nadzoring/commit/e1c32597a7dc8f96e8eb78748d61685f805d21d2))
- Build(deps-dev): bump types-requests

Bumps [types-requests](https://github.com/python/typeshed) from 2.33.0.20260402 to 2.33.0.20260408.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-requests
  dependency-version: 2.33.0.20260408
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([a2020ed](https://github.com/alexeev-prog/nadzoring/commit/a2020edefdedd766552e267ea7ba31c25abf2fe3))
- Build(deps-dev): bump types-tqdm from 4.67.3.20260402 to 4.67.3.20260408

Bumps [types-tqdm](https://github.com/python/typeshed) from 4.67.3.20260402 to 4.67.3.20260408.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-tqdm
  dependency-version: 4.67.3.20260408
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([2c12b1e](https://github.com/alexeev-prog/nadzoring/commit/2c12b1eb83eecdf5bad8048ea7a1bf59b530eb74))
- Build(deps-dev): bump types-pyyaml

Bumps [types-pyyaml](https://github.com/python/typeshed) from 6.0.12.20250915 to 6.0.12.20260408.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-pyyaml
  dependency-version: 6.0.12.20260408
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([5549be8](https://github.com/alexeev-prog/nadzoring/commit/5549be88afa45ec3b7a89685b75ced0e2098c019))
- Build(deps-dev): bump types-tabulate

Bumps [types-tabulate](https://github.com/python/typeshed) from 0.10.0.20260308 to 0.10.0.20260408.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-tabulate
  dependency-version: 0.10.0.20260408
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([772040d](https://github.com/alexeev-prog/nadzoring/commit/772040d25ee5e4cd58682239dca2f936a7c93c69))
- Build(deps-dev): bump types-tabulate from 0.10.0.20260308 to 0.10.0.20260408 (#101)

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>([acb0da4](https://github.com/alexeev-prog/nadzoring/commit/acb0da4bc8a2bf6a7faae3d4fa1d65061e8aec5b))
- Build(deps-dev): bump types-pyyaml from 6.0.12.20250915 to 6.0.12.20260408 (#102)([5390aee](https://github.com/alexeev-prog/nadzoring/commit/5390aeec73e7e894a56ceac08c355bf622dae12c))
- Build(deps-dev): bump types-tqdm from 4.67.3.20260402 to 4.67.3.20260408 (#103)([4ba26e0](https://github.com/alexeev-prog/nadzoring/commit/4ba26e02c21b7a8b98851fef2fcf5c7ececbb0fa))
- Build(deps-dev): bump types-requests from 2.33.0.20260402 to 2.33.0.20260408 (#104)([31d82a4](https://github.com/alexeev-prog/nadzoring/commit/31d82a4ca68bda2a5ef1826968e524ece4a6eefe))
- Build(deps-dev): bump pyrefly from 0.60.0 to 0.60.1

Bumps [pyrefly](https://github.com/facebook/pyrefly) from 0.60.0 to 0.60.1.
- [Release notes](https://github.com/facebook/pyrefly/releases)
- [Commits](https://github.com/facebook/pyrefly/compare/0.60.0...0.60.1)

---
updated-dependencies:
- dependency-name: pyrefly
  dependency-version: 0.60.1
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([eccc7c5](https://github.com/alexeev-prog/nadzoring/commit/eccc7c55afdeac9b9b7a71167d7c5e7b72f071e7))
- Build(deps-dev): bump ruff from 0.15.9 to 0.15.10

Bumps [ruff](https://github.com/astral-sh/ruff) from 0.15.9 to 0.15.10.
- [Release notes](https://github.com/astral-sh/ruff/releases)
- [Changelog](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md)
- [Commits](https://github.com/astral-sh/ruff/compare/0.15.9...0.15.10)

---
updated-dependencies:
- dependency-name: ruff
  dependency-version: 0.15.10
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([d640ceb](https://github.com/alexeev-prog/nadzoring/commit/d640ceb5e778841e2913034621bce036f462dee1))
- Build(deps-dev): bump ruff from 0.15.9 to 0.15.10 (#107)([b3f4e5e](https://github.com/alexeev-prog/nadzoring/commit/b3f4e5e789bac856b5ac0120604f008353e96c78))
- Build(deps-dev): bump pyrefly from 0.60.0 to 0.60.1 (#106)([fd99e9d](https://github.com/alexeev-prog/nadzoring/commit/fd99e9d5a2540e15103a8e0415ca0ee664fd2a37))

### CI/CD

- Ci: remove myst-parser from sphinx-docs([6d5f3c8](https://github.com/alexeev-prog/nadzoring/commit/6d5f3c85a796337470ee99ecd3a0b0e50cf810f6))

### Dependencies

- Bump dev-version([1db9169](https://github.com/alexeev-prog/nadzoring/commit/1db91691a9147486d82a737abbffa7e12b5558d0))

### Documentation

- Docs: update CHANGELOG.md for v0.2.1 [skip ci]([382ae95](https://github.com/alexeev-prog/nadzoring/commit/382ae950f90cda83ddbc48ac0274c08758ea3abe))
- Docs/refactor: lint tests and update readme([6f35f8d](https://github.com/alexeev-prog/nadzoring/commit/6f35f8d398fb9cd3c489a7b2d340b669481a4e6e))
- Docs/codestyle: update docs and codestyle([19648cd](https://github.com/alexeev-prog/nadzoring/commit/19648cd304ff9f09d643a07eab9db5554921f5b6))
- Docs: update error handling docs([a15fead](https://github.com/alexeev-prog/nadzoring/commit/a15fead7affc5dfabd90e79e3ed7209bc46b1832))
- Docs: add proxy usage guide in docs([eb88ce9](https://github.com/alexeev-prog/nadzoring/commit/eb88ce920ab8c41f745b0841e2bfd9e1f019e8ca))

### Features

- Feat/tests: enhance type safety of errors types and improves error handling([2f6257c](https://github.com/alexeev-prog/nadzoring/commit/2f6257c478587eca934692eccd02f8230e7fe975))
- Feat: add proxy (http, https, socks5, socks4) support([90533db](https://github.com/alexeev-prog/nadzoring/commit/90533db500280384303cd848d8695f69cc778c7f))
- Feat: add proxy (http, https, socks5, socks4) support (#108)([8724aea](https://github.com/alexeev-prog/nadzoring/commit/8724aea1e920ab49f1b3cfb146bddb27aee2ad9d))

### Other Changes

- Update readme([8228433](https://github.com/alexeev-prog/nadzoring/commit/82284335ebfdb6ee3b707b64a3b725f9ceb77f76))
- 📝 Add docstrings to `tests/network_base_tests`

Docstrings generation was requested by @alexeev-prog.

* https://github.com/alexeev-prog/nadzoring/pull/92#issuecomment-4235430501

The following files were modified:

* `tests/test_network_base/test_ping_address.py`
* `tests/test_network_base/test_traceroute.py`([3df9e81](https://github.com/alexeev-prog/nadzoring/commit/3df9e81fc6a372d3519fed88fb16b08a6a73e642))
- Add docstrings to `tests/network_base_tests` (#93)([15d84e3](https://github.com/alexeev-prog/nadzoring/commit/15d84e331eed6a28a5f4603142c99cd60d6be3b6))
- Update project logo and preview([da0687f](https://github.com/alexeev-prog/nadzoring/commit/da0687f6a99df9a4ac7d6eee7530207032eee870))
- Update project logo and preview (#96)([cbe44c3](https://github.com/alexeev-prog/nadzoring/commit/cbe44c39b8fabe09b3663b6872963ad35bba02cf))
- Update readme([988e3e1](https://github.com/alexeev-prog/nadzoring/commit/988e3e1e4ef1b2ba2648e9968ac7567e09fbbc54))
- Update readme([0174021](https://github.com/alexeev-prog/nadzoring/commit/0174021d617fb9cc4cf4bfea1d05513900c9c9cf))
- Update readme([eb58ae0](https://github.com/alexeev-prog/nadzoring/commit/eb58ae01be568f3ec7a8d48f4e2b50463db97657))
- Update readme([e7b41ce](https://github.com/alexeev-prog/nadzoring/commit/e7b41ceee56fc7e15c561668f43ede1e0d9395bb))
- Update readme([ed242d6](https://github.com/alexeev-prog/nadzoring/commit/ed242d6c556ece28d893126e6808f2a2a961aa14))
- Update readme([1c448c9](https://github.com/alexeev-prog/nadzoring/commit/1c448c93e5c4b24ac5357e20d6d58da89c630e6e))
- Upload social-preview([5ea865c](https://github.com/alexeev-prog/nadzoring/commit/5ea865c7d9d1a7e48c9d04f07fc93617b2bc36a7))
- Update readme([259bd6d](https://github.com/alexeev-prog/nadzoring/commit/259bd6d0ba93f4d76dca51aa62540e25c801458e))
- Update readme([a7a7238](https://github.com/alexeev-prog/nadzoring/commit/a7a7238dbd9832696563bd0d75ba618ae800ac30))
- Update agents.md with andrej-karparty recommendations([06b5105](https://github.com/alexeev-prog/nadzoring/commit/06b5105d494fe57ab90b6d146d197ade72150bd7))
- Typing: fix mypy issue with Incompatible types([531bf10](https://github.com/alexeev-prog/nadzoring/commit/531bf10a56d4e4fbd5ab29793860760fa412d0b6))
- Update src/nadzoring/security/check_website_ssl_cert.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([d419d92](https://github.com/alexeev-prog/nadzoring/commit/d419d926cdd63779b6e92f296875b1409ffe7a0e))
- Update src/nadzoring/security/http_headers.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([fe2af94](https://github.com/alexeev-prog/nadzoring/commit/fe2af944acea05aa907f8a95e30b75933481fa34))
- Update src/nadzoring/arp/cache.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([c8878d7](https://github.com/alexeev-prog/nadzoring/commit/c8878d7c34be7d76a2fe7867b748387d5eebcfd8))
- Update src/nadzoring/arp/cache.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([9df3b1a](https://github.com/alexeev-prog/nadzoring/commit/9df3b1aed428ed50127da4e00dc0c29b5c741369))
- Update src/nadzoring/network_base/whois_lookup.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([53cc396](https://github.com/alexeev-prog/nadzoring/commit/53cc396ffb226871e42991395e1caa4ea1f7d902))
- Reach 100% tests coverage for network-base([3710c13](https://github.com/alexeev-prog/nadzoring/commit/3710c135c0dbeeee776048dca3e07077fe4f9c7e))
- Enhance type safety and improve error handling (#105)([8128c74](https://github.com/alexeev-prog/nadzoring/commit/8128c745ae8ee7e3464f453e5ec9e49e3725caf8))
- Update src/nadzoring/utils/decorators.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([ac6e332](https://github.com/alexeev-prog/nadzoring/commit/ac6e332907dee8abc694a9dd031f1a1b5c562c60))
- Update src/nadzoring/security/subdomain_scan.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([a856ffb](https://github.com/alexeev-prog/nadzoring/commit/a856ffbbb4f90c6daa1e6e8a1e9850b9fd8512bf))

### Testing

- Tests: reach 100% tests coverage for network-base([6357511](https://github.com/alexeev-prog/nadzoring/commit/6357511a27ac7c6eb7a6db87eb0120fd427063e9))
- Tests: reach 100% tests coverage for network-base (#92)([8b0fc0a](https://github.com/alexeev-prog/nadzoring/commit/8b0fc0a439f15afd2e7a0822977e1c65cd19f1d0))
## [0.2.1](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.2.1) - 2026-04-11

### Bug Fixes

- Fix: resolve tqdm[Never] TypeError for Python 3.12+ compatibility
- Created dockerignore file / Docker.md / Dockerfile
- Replaced all 	qdm[Never] annotations with plain 	qdm
- Fixed compatibility issue with Python 3.12 type checkers
- No functional changes([72c5de0](https://github.com/alexeev-prog/nadzoring/commit/72c5de0fe74a038812ee98ce647816f2cecb2ead))
- Fix: remove python-versions from noxfile([715a378](https://github.com/alexeev-prog/nadzoring/commit/715a3784f58904bc22b1928b717a5d55fe08ba37))
- Fix: fix tests errors and fix mypy error in 3.12([27dc667](https://github.com/alexeev-prog/nadzoring/commit/27dc66784505d63a88499e10579785e496be657a))

### Build System

- Build(deps): bump astral-sh/setup-uv from 5 to 7

Bumps [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) from 5 to 7.
- [Release notes](https://github.com/astral-sh/setup-uv/releases)
- [Commits](https://github.com/astral-sh/setup-uv/compare/v5...v7)

---
updated-dependencies:
- dependency-name: astral-sh/setup-uv
  dependency-version: '7'
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([0ef2593](https://github.com/alexeev-prog/nadzoring/commit/0ef2593c621912b2739ba9305655258fd170056f))
- Build(deps): bump astral-sh/setup-uv from 5 to 7 (#72)([d27942e](https://github.com/alexeev-prog/nadzoring/commit/d27942e29864344ca3cd360d0907b52d124fa5a7))
- Build(deps): bump aiohttp from 3.13.3 to 3.13.5

---
updated-dependencies:
- dependency-name: aiohttp
  dependency-version: 3.13.5
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([0de76b9](https://github.com/alexeev-prog/nadzoring/commit/0de76b96e3b8dc85578be5b47594d7e51cd5378a))
- Build(deps-dev): bump types-requests

Bumps [types-requests](https://github.com/python/typeshed) from 2.32.4.20260107 to 2.33.0.20260327.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-requests
  dependency-version: 2.33.0.20260327
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([c5a1bbb](https://github.com/alexeev-prog/nadzoring/commit/c5a1bbb2de1582e8d827dd13ce0869a4495e8175))
- Build(deps): bump certifi from 2026.1.4 to 2026.2.25

Bumps [certifi](https://github.com/certifi/python-certifi) from 2026.1.4 to 2026.2.25.
- [Commits](https://github.com/certifi/python-certifi/compare/2026.01.04...2026.02.25)

---
updated-dependencies:
- dependency-name: certifi
  dependency-version: 2026.2.25
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([17623b8](https://github.com/alexeev-prog/nadzoring/commit/17623b8e8a2c4721efd65ff663832ff436a9da0c))
- Build(deps): bump tabulate from 0.9.0 to 0.10.0

Bumps [tabulate](https://github.com/astanin/python-tabulate) from 0.9.0 to 0.10.0.
- [Changelog](https://github.com/astanin/python-tabulate/blob/master/CHANGELOG)
- [Commits](https://github.com/astanin/python-tabulate/compare/v0.9.0...v0.10.0)

---
updated-dependencies:
- dependency-name: tabulate
  dependency-version: 0.10.0
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([0ccfb91](https://github.com/alexeev-prog/nadzoring/commit/0ccfb913fae2704d12f658de3613e352b8193dd4))
- Build(deps-dev): bump pytest-cov from 7.0.0 to 7.1.0

Bumps [pytest-cov](https://github.com/pytest-dev/pytest-cov) from 7.0.0 to 7.1.0.
- [Changelog](https://github.com/pytest-dev/pytest-cov/blob/master/CHANGELOG.rst)
- [Commits](https://github.com/pytest-dev/pytest-cov/compare/v7.0.0...v7.1.0)

---
updated-dependencies:
- dependency-name: pytest-cov
  dependency-version: 7.1.0
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([a7f2fe8](https://github.com/alexeev-prog/nadzoring/commit/a7f2fe82802fa933d64e56c54b361d7149e0768e))
- Build(deps-dev): bump basedpyright from 1.38.3 to 1.39.0

Bumps [basedpyright](https://github.com/detachhead/basedpyright) from 1.38.3 to 1.39.0.
- [Release notes](https://github.com/detachhead/basedpyright/releases)
- [Commits](https://github.com/detachhead/basedpyright/compare/v1.38.3...v1.39.0)

---
updated-dependencies:
- dependency-name: basedpyright
  dependency-version: 1.39.0
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([03c931e](https://github.com/alexeev-prog/nadzoring/commit/03c931e8f541564254ad08dcddf2c74b6f69eb27))
- Build(deps-dev): bump ruff from 0.15.1 to 0.15.8

Bumps [ruff](https://github.com/astral-sh/ruff) from 0.15.1 to 0.15.8.
- [Release notes](https://github.com/astral-sh/ruff/releases)
- [Changelog](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md)
- [Commits](https://github.com/astral-sh/ruff/compare/0.15.1...0.15.8)

---
updated-dependencies:
- dependency-name: ruff
  dependency-version: 0.15.8
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([64800db](https://github.com/alexeev-prog/nadzoring/commit/64800dba577dc22e192bed18af602417d11a6aae))
- Build(deps): bump pandas from 3.0.1 to 3.0.2

Bumps [pandas](https://github.com/pandas-dev/pandas) from 3.0.1 to 3.0.2.
- [Release notes](https://github.com/pandas-dev/pandas/releases)
- [Commits](https://github.com/pandas-dev/pandas/compare/v3.0.1...v3.0.2)

---
updated-dependencies:
- dependency-name: pandas
  dependency-version: 3.0.2
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([4222a6b](https://github.com/alexeev-prog/nadzoring/commit/4222a6b606b42aeae2d0fdf01dc9be27c461b3bb))
- Build(deps-dev): bump mypy from 1.19.1 to 1.20.0

Bumps [mypy](https://github.com/python/mypy) from 1.19.1 to 1.20.0.
- [Changelog](https://github.com/python/mypy/blob/master/CHANGELOG.md)
- [Commits](https://github.com/python/mypy/compare/v1.19.1...v1.20.0)

---
updated-dependencies:
- dependency-name: mypy
  dependency-version: 1.20.0
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([b3d5013](https://github.com/alexeev-prog/nadzoring/commit/b3d50132e1a1be05ddb86543d902291ab9deea7a))
- Build(deps-dev): bump mypy from 1.19.1 to 1.20.0 (#73)([e5efa42](https://github.com/alexeev-prog/nadzoring/commit/e5efa4237aab2546dab726f96d9ef518e2a0ec77))
- Build(deps): bump pandas from 3.0.1 to 3.0.2 (#80)([1a73e2b](https://github.com/alexeev-prog/nadzoring/commit/1a73e2b15e971053be1b5c777973e8d946363da8))
- Build(deps-dev): bump ruff from 0.15.1 to 0.15.8 (#74)([29c3541](https://github.com/alexeev-prog/nadzoring/commit/29c3541d6f4901c6f56694634532087cbab710e1))
- Build(deps-dev): bump pyrefly from 0.56.0 to 0.59.0

Bumps [pyrefly](https://github.com/facebook/pyrefly) from 0.56.0 to 0.59.0.
- [Release notes](https://github.com/facebook/pyrefly/releases)
- [Commits](https://github.com/facebook/pyrefly/compare/0.56.0...0.59.0)

---
updated-dependencies:
- dependency-name: pyrefly
  dependency-version: 0.59.0
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>([cde0a68](https://github.com/alexeev-prog/nadzoring/commit/cde0a6846f3f8940fa1b31533ff69da0ef572948))
- Build(deps-dev): bump pyrefly from 0.56.0 to 0.59.0 (#75)([8e8f73e](https://github.com/alexeev-prog/nadzoring/commit/8e8f73e2ee547a9151cf960a32890945cd15637d))
- Build(deps-dev): bump basedpyright from 1.38.3 to 1.39.0 (#76)([8bea5ed](https://github.com/alexeev-prog/nadzoring/commit/8bea5ed73a26db9601e59514a8940cc4b6cd2925))
- Build(deps-dev): bump pytest-cov from 7.0.0 to 7.1.0 (#77)([955fd0f](https://github.com/alexeev-prog/nadzoring/commit/955fd0f27a98e710aa48f342fe19d3c8ef7baa72))
- Build(deps): bump tabulate from 0.9.0 to 0.10.0 (#79)([76e21e0](https://github.com/alexeev-prog/nadzoring/commit/76e21e073b9d344584d1b0ddf9f5f90bbe266fd8))
- Build(deps): bump certifi from 2026.1.4 to 2026.2.25 (#81)([0c634a5](https://github.com/alexeev-prog/nadzoring/commit/0c634a5876e393396a22271886f992c2cfe45742))
- Build(deps-dev): bump types-requests from 2.32.4.20260107 to 2.33.0.20260327 (#82)([60ac7a6](https://github.com/alexeev-prog/nadzoring/commit/60ac7a60b4880587694f4083ad8001058c3a380d))
- Build(deps): bump aiohttp from 3.13.3 to 3.13.5 (#78)([e4c6c67](https://github.com/alexeev-prog/nadzoring/commit/e4c6c67356c19e53631f5a7554764e6f9fb73dc7))
- Build(deps): bump cryptography from 46.0.5 to 46.0.6

Bumps [cryptography](https://github.com/pyca/cryptography) from 46.0.5 to 46.0.6.
- [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/pyca/cryptography/compare/46.0.5...46.0.6)

---
updated-dependencies:
- dependency-name: cryptography
  dependency-version: 46.0.6
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([1eeed01](https://github.com/alexeev-prog/nadzoring/commit/1eeed0183371fc4262c494dd719f37a42d9eab6e))
- Build(deps): bump cryptography from 46.0.5 to 46.0.6 (#84)([28814b2](https://github.com/alexeev-prog/nadzoring/commit/28814b253cae0bb0df84f72cc7b216e4b11613d5))
- Build(deps-dev): bump pyrefly from 0.59.0 to 0.59.1

Bumps [pyrefly](https://github.com/facebook/pyrefly) from 0.59.0 to 0.59.1.
- [Release notes](https://github.com/facebook/pyrefly/releases)
- [Commits](https://github.com/facebook/pyrefly/compare/0.59.0...0.59.1)

---
updated-dependencies:
- dependency-name: pyrefly
  dependency-version: 0.59.1
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([6a3b972](https://github.com/alexeev-prog/nadzoring/commit/6a3b972689c2aa233ddba93494312d6cd1cd10fd))
- Build(deps-dev): bump pyrefly from 0.59.0 to 0.59.1 (#85)([44a5eb5](https://github.com/alexeev-prog/nadzoring/commit/44a5eb50c35d2c095071521e1f4c2b02cedf8fd1))
- Build(deps-dev): bump ruff from 0.15.8 to 0.15.9

Bumps [ruff](https://github.com/astral-sh/ruff) from 0.15.8 to 0.15.9.
- [Release notes](https://github.com/astral-sh/ruff/releases)
- [Changelog](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md)
- [Commits](https://github.com/astral-sh/ruff/compare/0.15.8...0.15.9)

---
updated-dependencies:
- dependency-name: ruff
  dependency-version: 0.15.9
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([a807938](https://github.com/alexeev-prog/nadzoring/commit/a80793855bfb57da729ceb26a52bcb2814d42928))
- Build(deps-dev): bump types-requests

Bumps [types-requests](https://github.com/python/typeshed) from 2.33.0.20260327 to 2.33.0.20260402.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-requests
  dependency-version: 2.33.0.20260402
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([9719b1c](https://github.com/alexeev-prog/nadzoring/commit/9719b1cbcf20422e0bbe1f1ea314550a22cb80ea))
- Build(deps-dev): bump types-tqdm from 4.67.3.20260303 to 4.67.3.20260402

Bumps [types-tqdm](https://github.com/python/typeshed) from 4.67.3.20260303 to 4.67.3.20260402.
- [Commits](https://github.com/python/typeshed/commits)

---
updated-dependencies:
- dependency-name: types-tqdm
  dependency-version: 4.67.3.20260402
  dependency-type: direct:development
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>([3c68141](https://github.com/alexeev-prog/nadzoring/commit/3c68141220893f56d479b43356332d90ae5b776a))
- Build(deps-dev): bump types-tqdm from 4.67.3.20260303 to 4.67.3.20260402 (#86)([c0b9428](https://github.com/alexeev-prog/nadzoring/commit/c0b94287b8713c0ff363c5b3550219e9ba68eb40))
- Build(deps-dev): bump types-requests from 2.33.0.20260327 to 2.33.0.20260402 (#87)([db150e6](https://github.com/alexeev-prog/nadzoring/commit/db150e698fcd041d46196883533cb645fe93bcec))
- Build(deps-dev): bump ruff from 0.15.8 to 0.15.9 (#88)([ff81db4](https://github.com/alexeev-prog/nadzoring/commit/ff81db432f3f7dfbb545d10568dc1ffe572a1dbe))

### Dependencies

- Bump dev-version([b8190cd](https://github.com/alexeev-prog/nadzoring/commit/b8190cdb2ff9df80274a2d2c1dc81319c30d8f71))

### Documentation

- Docs: update CHANGELOG.md for v0.2.0 [skip ci]([9f5d4ca](https://github.com/alexeev-prog/nadzoring/commit/9f5d4ca96f3c5cb58d4af38f7c39275151f02b20))
- Docs: update readme for bumb versions to 0.2.1([333437c](https://github.com/alexeev-prog/nadzoring/commit/333437c735960a6ee385f3f52ab750cd35fe1ef3))

### Features

- Add completions command group, tests and documentation([82f21ee](https://github.com/alexeev-prog/nadzoring/commit/82f21ee48a34adfd29c7440df1c64cc142b8c169))
- Add completions command group, tests and documentation (#89)([1283e3b](https://github.com/alexeev-prog/nadzoring/commit/1283e3b2d27f939f68b378bb3f6a2e8ec66fdf11))

### Other Changes

- Update docs/index([e63e0d5](https://github.com/alexeev-prog/nadzoring/commit/e63e0d5bbe62200f166cadfa5514b895a88455d0))
- Update docs/index([3a0e26a](https://github.com/alexeev-prog/nadzoring/commit/3a0e26a91968145cc4d241e6d026d89424217b88))
- Update community files([b841c6d](https://github.com/alexeev-prog/nadzoring/commit/b841c6d3687308cef1b44145865c1b2595504513))
- Update deps and github conf([07574c6](https://github.com/alexeev-prog/nadzoring/commit/07574c6e61c290bf3340a81a0bbbc2f6d6289ff0))
- Feature/dockerize (#83)([69a6c6b](https://github.com/alexeev-prog/nadzoring/commit/69a6c6bd4dbb14a2f3fcb57c0b4b2c95c99a11fe))
- Update gitignore([728bd68](https://github.com/alexeev-prog/nadzoring/commit/728bd68faadca5d1d954bcb3275906666f8cd5a7))
- Update src/nadzoring/commands/completions_commands.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([7868315](https://github.com/alexeev-prog/nadzoring/commit/78683150683bd6688f4e04d699214f7671546c5d))
- Update src/nadzoring/cli.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([ad893f3](https://github.com/alexeev-prog/nadzoring/commit/ad893f32333037d42feac32a7b3db4073d88af9e))

### Testing

- Test files([b84eced](https://github.com/alexeev-prog/nadzoring/commit/b84eced926b7353fb20947a4a4c1aa06836fe64a))
## [0.2.0](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.2.0) - 2026-04-02

### Bug Fixes

- Fix: remove "| grep UP" in ipv4_local_cli.py([9d0be33](https://github.com/alexeev-prog/nadzoring/commit/9d0be33fae0ca486d202a186c81434804e144278))
- Fix linters warnings&errors([69bb03a](https://github.com/alexeev-prog/nadzoring/commit/69bb03a1ef7266efd398d9913567d7d2d1d0e668))
- Fix: fix typing errors, update network-base commands timeout options, update common_cli_options([1efc42f](https://github.com/alexeev-prog/nadzoring/commit/1efc42fe9ba25c5cf035a6fa52b8cbb44e252874))

### Build System

- Build(deps): bump actions/deploy-pages from 4 to 5

Bumps [actions/deploy-pages](https://github.com/actions/deploy-pages) from 4 to 5.
- [Release notes](https://github.com/actions/deploy-pages/releases)
- [Commits](https://github.com/actions/deploy-pages/compare/v4...v5)

---
updated-dependencies:
- dependency-name: actions/deploy-pages
  dependency-version: '5'
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([4bcf226](https://github.com/alexeev-prog/nadzoring/commit/4bcf2261cba6272820e841acb502804ddf038850))
- Build(deps): bump actions/deploy-pages from 4 to 5 (#68)([de85b5f](https://github.com/alexeev-prog/nadzoring/commit/de85b5f1e897fe47d43bf81367b14c18990ba50a))

### CI/CD

- Ci: add basic mypy typing check in python-package workflow([e05f1f9](https://github.com/alexeev-prog/nadzoring/commit/e05f1f9edd8500de38804a4240749da5fe6f7c11))
- Ci: update python-package CI([b8c1e9d](https://github.com/alexeev-prog/nadzoring/commit/b8c1e9d5127154561b9568142236b3c3c67554a8))
- Ci: update python-package CI([7bd3885](https://github.com/alexeev-prog/nadzoring/commit/7bd3885cc95b5ddc6bfc2b70f2effdea3e6db432))
- Ci: update python-package CI([22f9826](https://github.com/alexeev-prog/nadzoring/commit/22f9826c985669e201f149944ba01295d4c106a0))
- Ci: fix python-package CI([530ac81](https://github.com/alexeev-prog/nadzoring/commit/530ac81ed148529c786be057afa1f718d766658c))
- Ci: fix python-package CI([1f6f8fe](https://github.com/alexeev-prog/nadzoring/commit/1f6f8febea967be58b00537bb6bc3c126071a30e))
- Ci: fix python-package CI and deps([ec34eb5](https://github.com/alexeev-prog/nadzoring/commit/ec34eb552d0f75bff2b76c99774a099089b1cd65))
- Ci: fix noxfile([6936a3d](https://github.com/alexeev-prog/nadzoring/commit/6936a3df23129852252c816abb1334ffeffc8ec8))
- Ci: add AI policy([d03394e](https://github.com/alexeev-prog/nadzoring/commit/d03394e78b7cc50c7b706bb484ea163d3461280d))

### Code Refactoring

- Refactor: update codestyle([3db49fd](https://github.com/alexeev-prog/nadzoring/commit/3db49fd635de9e08b22e3e27336c18519271eaf2))
- Refactor: fix typing issues, remove ty([daafaed](https://github.com/alexeev-prog/nadzoring/commit/daafaeddd2057873ef2ed90340370c1aeddbf841))
- Refactor: fix typing issues, remove ty (#56)([a3f6002](https://github.com/alexeev-prog/nadzoring/commit/a3f60024abc7a24bd09dee4b439614e934b97fb8))
- Refactor: update code style and constants([d25d91c](https://github.com/alexeev-prog/nadzoring/commit/d25d91c95cff16b5684176923c48d54b9dc925eb))
- Refactor: update code style and constants (#57)([013cfaf](https://github.com/alexeev-prog/nadzoring/commit/013cfaf018bc39102b2b3d7c5b495b697f0f7cde))
- Refactor: replacing shell=true with shlex.split, and replacing grep with an internal function([9075df8](https://github.com/alexeev-prog/nadzoring/commit/9075df89a91d75dc2a0e0ca21f0febcb2f79e77b))
- Refactor/fix: refactor tests and fix timeout([d16ffbc](https://github.com/alexeev-prog/nadzoring/commit/d16ffbc0836e5b5d3feb1e8a1dad1188f04df4ae))

### Documentation

- Docs: update CHANGELOG.md for v0.1.9 [skip ci]([ab1c66c](https://github.com/alexeev-prog/nadzoring/commit/ab1c66c141e5ff0c8178f4889665d35d2a6e9951))
- Docs: update version([c6cc4d7](https://github.com/alexeev-prog/nadzoring/commit/c6cc4d7afac49fa917ae2b42462ccdbfa63f6fac))
- Docs/ci: update readme and integrate coveralls([333ae3b](https://github.com/alexeev-prog/nadzoring/commit/333ae3ba23fd085b041a92d498d9d5ed1a6d407a))
- Docs: update readme([ff4f9a5](https://github.com/alexeev-prog/nadzoring/commit/ff4f9a53e59bf84d40394468448154dfc76330ef))
- Docs: update readme([a19de8f](https://github.com/alexeev-prog/nadzoring/commit/a19de8fec5f399d3d2165e9a13d25560402faaa2))
- Docs: update readme([c54a958](https://github.com/alexeev-prog/nadzoring/commit/c54a958da05f146acd2d03ef085c81661dd603d9))
- Docs/ci: create workflow for publish, update docs([9bb196c](https://github.com/alexeev-prog/nadzoring/commit/9bb196c3b75bf2cc49205b73fd5b1512432607d1))

### Features

- Add tests for network_base module([6ac7f5c](https://github.com/alexeev-prog/nadzoring/commit/6ac7f5c23a07cd86ee2a6acbab35dbb993ff129f))
- Add tests for network_base module (#67)([2bb56d6](https://github.com/alexeev-prog/nadzoring/commit/2bb56d62e63faa6bfd959bbe3d90dacc4b786490))
- Feat: create utils.timeout and unify timeout configuration([3c3d5bd](https://github.com/alexeev-prog/nadzoring/commit/3c3d5bda3eee8a62106bb3926777eb4657f80010))
- Feature: unify all timeouts to TimeoutConfig([84c2e08](https://github.com/alexeev-prog/nadzoring/commit/84c2e08ed8c03a920c7ff611cf25a422255c58b5))
- Feat: Implement unified timeout handling architecture with TimeoutConfig (#71)([ac53843](https://github.com/alexeev-prog/nadzoring/commit/ac538433028649a9fbcfa26baa958c6aa597e11b))

### Other Changes

- Bump actions/setup-python from 5 to 6

Bumps [actions/setup-python](https://github.com/actions/setup-python) from 5 to 6.
- [Release notes](https://github.com/actions/setup-python/releases)
- [Commits](https://github.com/actions/setup-python/compare/v5...v6)

---
updated-dependencies:
- dependency-name: actions/setup-python
  dependency-version: '6'
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([d50b4b4](https://github.com/alexeev-prog/nadzoring/commit/d50b4b42f5d564c503101e0234439fedd34bbc33))
- Bump actions/setup-python from 5 to 6 (#55)([4233796](https://github.com/alexeev-prog/nadzoring/commit/4233796ceb6162db3fc93baa4374a6e59bcf3e88))
- Update src/nadzoring/commands/dns_commands.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([fb95ce9](https://github.com/alexeev-prog/nadzoring/commit/fb95ce9eb580b65ab79fd23f6add03b288154448))
- Update src/nadzoring/network_base/domain_info.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([1e54f37](https://github.com/alexeev-prog/nadzoring/commit/1e54f37b97b56dad4ee535872590a80ec201bff1))
- Update readme([f0bfeb5](https://github.com/alexeev-prog/nadzoring/commit/f0bfeb53bff43345548ce0f6567e3663ff8bb932))
- Update deps([b1c8ee5](https://github.com/alexeev-prog/nadzoring/commit/b1c8ee56638990ecb318b6e53a3715c40e2e0248))
- Fix WHOIS table formatting and datetime display([a3df54c](https://github.com/alexeev-prog/nadzoring/commit/a3df54ccc1a4da321040ef743412eed2b970466f))
- Fix CLI exception handling and WHOIS docstring formatting

- Updated cli.py to raise ClickException using 'raise ... from e' for proper exception chaining
- Adjusted whois_command docstring in dns_commands.py to fit a single line
- Fixed line wrapping in formatters.py to comply with Ruff line-length checks
- Only modified files that were touched during current work
- All modified files pass Ruff linting checks([ca55bcc](https://github.com/alexeev-prog/nadzoring/commit/ca55bcc41dfe6b72837ca6544ac746f014448234))
- Address review feedback and fix test failures([1410265](https://github.com/alexeev-prog/nadzoring/commit/1410265ec0fb53d365a7ae0ae1316f3912ba9117))
- Fix dns whois command registration and restore router_ip docstring([f18688f](https://github.com/alexeev-prog/nadzoring/commit/f18688f73f9956fc770359e7dfc3c08adb096b98))
- Fix lint issues from review([219aaa2](https://github.com/alexeev-prog/nadzoring/commit/219aaa2bad2d0cd1fa0d88caf3a6504be40d02b6))
- Handle ASCII-only IPv4 normalization([048c083](https://github.com/alexeev-prog/nadzoring/commit/048c083f2413c71acdd186bce37584ea75537a1a))
- Move WHOIS logic out of CLI and simplify main entrypoint([757cd55](https://github.com/alexeev-prog/nadzoring/commit/757cd553ca5a98c4f0ab6cc14d2ed273e9a45840))
- Keep WHOIS errors in CLI layer([2375196](https://github.com/alexeev-prog/nadzoring/commit/2375196eecf0e59c998ea5807eeda1b775d0ae80))
- Update CONTRIBUTING guide([95b8ffd](https://github.com/alexeev-prog/nadzoring/commit/95b8ffd080dbf3648f37693077c277c5a1078047))
- Update readme([89d7339](https://github.com/alexeev-prog/nadzoring/commit/89d7339401ea89393b17fa4f18e7bf4a78929868))
- Replace shell=True with safe argument lists (#66)([b274752](https://github.com/alexeev-prog/nadzoring/commit/b274752c7594d57425b4b3e4ad14458bee804ef0))
- Improve error messages with actionable suggestions #46 (#64)([6d8c105](https://github.com/alexeev-prog/nadzoring/commit/6d8c105999d03d3f92dd9c4388b0a9fe885a6bb5))
- Update readme([9e7f6ae](https://github.com/alexeev-prog/nadzoring/commit/9e7f6ae1228ca6977b021979d3a1774c1ba3e65e))
- Update readme([fcf7e6a](https://github.com/alexeev-prog/nadzoring/commit/fcf7e6ac684b543ee8215d28259b6fdb02c6163a))
- Small fix for docs([bf6b1a7](https://github.com/alexeev-prog/nadzoring/commit/bf6b1a7cc680457a3ace3381e9b5987ec1db322b))
- Update readme (issue #69)([f8ece03](https://github.com/alexeev-prog/nadzoring/commit/f8ece03d3ae028b712c35e1f57282a54f1833062))
- Update readme([cb3bcf1](https://github.com/alexeev-prog/nadzoring/commit/cb3bcf191dc770450c1545ed4875241c23665dc9))

### Testing

- Tests: add tests for nadzoring.utils, setup pytest and update contributing guide([ab70204](https://github.com/alexeev-prog/nadzoring/commit/ab70204bd2888e06ae97d0ddcfac2a76ac28436a))
- Tests: Create tests for nadzoring.utils (#65)([9cf228d](https://github.com/alexeev-prog/nadzoring/commit/9cf228de5e262807832712b468e3614410587cbd))
- Tests: create more tests for network_base module (~90% coverage)([d83a5c9](https://github.com/alexeev-prog/nadzoring/commit/d83a5c9311ab4db36014a72e323f5f47fb443d3f))
- Tests: create more tests for network_base module (#70)([f252e58](https://github.com/alexeev-prog/nadzoring/commit/f252e58e93292804e0804ed8b25190b423c305e2))
- Tests/fix: fix issues with TimeoutConfig for dns, and update tests([1e7920a](https://github.com/alexeev-prog/nadzoring/commit/1e7920a66097351c1991479c43cf88404068625a))
## [0.1.9](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.1.9) - 2026-03-18

### Bug Fixes

- Fix typo in changelog([7823596](https://github.com/alexeev-prog/nadzoring/commit/7823596f48543620db67bc462a39da27493ef7ca))
- Fix british spelling in readme([8e7654d](https://github.com/alexeev-prog/nadzoring/commit/8e7654d20e7b68235306dc4c492df9d2c725682e))

### Build System

- Build: release 0.1.9([1da60dd](https://github.com/alexeev-prog/nadzoring/commit/1da60ddca68f0313291ebd1f94fef38258cca828))

### CI/CD

- Workflow: add doc_request in issue templates, update noxfile and deps([b126805](https://github.com/alexeev-prog/nadzoring/commit/b12680520106bed4ae3287d8b375d24f6808cd83))

### Code Refactoring

- Refactor: update ruff linter rules and update codestyle([fd5f986](https://github.com/alexeev-prog/nadzoring/commit/fd5f986b6b82ef0664220ff142a61b4461d481c9))

### Code Style

- Style: sort dns utils imports for ruff lint([fba4b4e](https://github.com/alexeev-prog/nadzoring/commit/fba4b4edd9bf6b0d502383f0de223ed9ebb2dba2))

### Documentation

- Docs: update CHANGELOG.md for v0.1.8 [skip ci]([60021e4](https://github.com/alexeev-prog/nadzoring/commit/60021e411cacdb30dc2db9d9230dfcddb1544836))
- Docs: update readme([ecdafbf](https://github.com/alexeev-prog/nadzoring/commit/ecdafbf2b5c671a2b9ebaf16db5e4d5cc984c3b7))
- Docs: update readme([553c71c](https://github.com/alexeev-prog/nadzoring/commit/553c71c99e23611c3250bd56190c465b24f03713))
- Docs: update readme([84c9b34](https://github.com/alexeev-prog/nadzoring/commit/84c9b34656a6f489d6b38efe59fc8b312dc4e417))
- Docs: update readme([ad48278](https://github.com/alexeev-prog/nadzoring/commit/ad48278c5acb4f013390d5aaa3e9797a84ca0382))
- Docs: update article([5e5c54a](https://github.com/alexeev-prog/nadzoring/commit/5e5c54ad84bf66b90553fe33e43202184f8a5d09))
- Docs: add missing Examples sections for new async DNS APIs([217f9f2](https://github.com/alexeev-prog/nadzoring/commit/217f9f25f3d0769ec5362a67b314eb56c7008a49))

### Features

- Feat: add active service detection for target hosts (network-base)([0646707](https://github.com/alexeev-prog/nadzoring/commit/0646707c738c04242721e3a3e6387f631c049eec))
- Feat: add command detect-service in network-base([8577696](https://github.com/alexeev-prog/nadzoring/commit/8577696daf4f6d1daad0e8c4dfd8a566b0d99c4b))
- Add MDC instruction for cursor IDE([39b5f13](https://github.com/alexeev-prog/nadzoring/commit/39b5f13f2908e9693a89dbafb8f548c12e7d2de2))
- Add SKILL.md file([698fd80](https://github.com/alexeev-prog/nadzoring/commit/698fd808a0f04424189395c3395b9ed1d1a4f6f0))
- Feat: add YAML output format support([73d3c0e](https://github.com/alexeev-prog/nadzoring/commit/73d3c0e9923d27d5cf2dba761ae68c528092c0c1))

### Other Changes

- Oops, missed another typo([a28a977](https://github.com/alexeev-prog/nadzoring/commit/a28a9777c98892dd673e1fe6863d448f92ce0c2d))
- Oops, missed the architecture docs too([9b55e97](https://github.com/alexeev-prog/nadzoring/commit/9b55e97ac280853fc12b9cecf5baf89d75b8d7dc))
- Create SECURITY.md([eb0f514](https://github.com/alexeev-prog/nadzoring/commit/eb0f5147527136c0216349248b9780d25ded835d))
- Update readme([2506225](https://github.com/alexeev-prog/nadzoring/commit/25062254bac63c03e737678cfed7f62b19645796))
- Add safe async DNS benchmark API([39b6e26](https://github.com/alexeev-prog/nadzoring/commit/39b6e263f6f438cad707a91a8f06ae330e6d8137))
- Add safe async DNS benchmark API and stabilize fallback behavior (#53)([bd6134c](https://github.com/alexeev-prog/nadzoring/commit/bd6134c891a7039a8a7613dec29dfe2a875a513d))
- Update codestyle([3a42f8d](https://github.com/alexeev-prog/nadzoring/commit/3a42f8de3a3299851aa6a9b248bdb5646b36b560))
- Update version([ac9be2a](https://github.com/alexeev-prog/nadzoring/commit/ac9be2ae3bf77f17a29e8a808e041717be413ed8))
- Adds `sphinx.ext.linkcode` to the Sphinx configuration (#54)([90407a5](https://github.com/alexeev-prog/nadzoring/commit/90407a5fafbfa6ee76e770dc5b8a56e0f3812bce))
## [0.1.8](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.1.8) - 2026-03-14

### Bug Fixes

- Fix: use per-socket timeout instead of process-global setdefaulttimeout to eliminate race conditions in concurrent subdomain scanning([d17208d](https://github.com/alexeev-prog/nadzoring/commit/d17208df43e00f0f70269db9b8be7b555fb7093c))
- Fix match wildcasrd DNS names in SAN entries([3f756bd](https://github.com/alexeev-prog/nadzoring/commit/3f756bd1a1bcc9d345a1946e447c382969995304))
- Fix: correct misleading chain_valid field in SSL certificate check([1b9d940](https://github.com/alexeev-prog/nadzoring/commit/1b9d94022f6a7f0016c4d1627fbb7becb05b9a37))

### Documentation

- Docs: update CHANGELOG.md [skip ci]([6e75ac4](https://github.com/alexeev-prog/nadzoring/commit/6e75ac454f5333aa709b5e5e2f72f4f0bbaba53f))
- Docs: update CHANGELOG.md [skip ci]([4465bcf](https://github.com/alexeev-prog/nadzoring/commit/4465bcfe7986ec63925ab7e033781f72f01bca79))

### Features

- Add error handling for dns resolution in _query_txt([9b3ee14](https://github.com/alexeev-prog/nadzoring/commit/9b3ee14e7e4b6201cf787e9eb6e2a8c4dc0e0855))
- Add git-cliff and update changelog([8d00ee5](https://github.com/alexeev-prog/nadzoring/commit/8d00ee5a2eba1a51aa84274978a58b3ca49886d2))

### Other Changes

- Update docs workflow([b767a9b](https://github.com/alexeev-prog/nadzoring/commit/b767a9b449d2cd606edee1bd6b48378b4bf9ac97))
- Update dependencies([bb88160](https://github.com/alexeev-prog/nadzoring/commit/bb88160da583b9aa072125dd592efe3840faca10))
- Fix unreachable DNS fallback code in _get_dns_records([3aa0be0](https://github.com/alexeev-prog/nadzoring/commit/3aa0be0d5b1d22f8f2a971cfd7a4a43932c348d8))
- Update changelog workflow([0737064](https://github.com/alexeev-prog/nadzoring/commit/07370641214488a9e0137ff91ef4f1f60901404f))
- Update workflow([a858547](https://github.com/alexeev-prog/nadzoring/commit/a858547b891bd50f726566deabb1e225f75ad95a))
- Update workflow and git-cliff([7d05e77](https://github.com/alexeev-prog/nadzoring/commit/7d05e77be0923079acf85c00a0a3e2ce352d4219))
- Update changelog.md([fb89dba](https://github.com/alexeev-prog/nadzoring/commit/fb89dba55ee44fc4d715587a20aa53bc65b580f1))
## [0.1.7](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.1.7) - 2026-03-14

### Bug Fixes

- Fix typing issues([e8b8e0a](https://github.com/alexeev-prog/nadzoring/commit/e8b8e0af1480796e24091168c729077f3a11c9e1))
- Fix potential issues from code review([71714ab](https://github.com/alexeev-prog/nadzoring/commit/71714ab3a5708f28db551bddd9fbd75913578a80))

### Features

- Create security command group and add check-ssl-expiry command([b1355c1](https://github.com/alexeev-prog/nadzoring/commit/b1355c13c376f699cfc577e868729a75d33d99b8))
- Create parse-url command in network-base group([6a164a6](https://github.com/alexeev-prog/nadzoring/commit/6a164a6743f788474b86458eff1d1ac53ac9f747))
- Add domain info, email, http headers, subdomains, ssl monitorr commands, update docs and deps([6f464d8](https://github.com/alexeev-prog/nadzoring/commit/6f464d8764830284299bb58fea2615b4f5fbf462))

### Other Changes

- Update typing, updaqte readme and update dependenices([814eecd](https://github.com/alexeev-prog/nadzoring/commit/814eecdb1b9d963f3b757e8b28dca893cd9b80ca))
- Update readme([d4d8ff7](https://github.com/alexeev-prog/nadzoring/commit/d4d8ff75afda8f7a618939aa6e2d68bc48fca791))
- Update readme([c4d9f2b](https://github.com/alexeev-prog/nadzoring/commit/c4d9f2ba88fa1ef0ab255aa294984b45a8a01c21))
- Update typing([efaf893](https://github.com/alexeev-prog/nadzoring/commit/efaf89364affbcddd3dd196df2f7b58556710d96))
- Update readme([b900a61](https://github.com/alexeev-prog/nadzoring/commit/b900a61625c241435553ea78563d2d9b1735acad))
- Update readme([fd2235e](https://github.com/alexeev-prog/nadzoring/commit/fd2235e4b689f25d0d356405eba9af6eb5461eb2))
- Update network commands([b9de859](https://github.com/alexeev-prog/nadzoring/commit/b9de859d5449fe0048e6118860837bd216dfd30c))
- Update src/nadzoring/commands/security_commands.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([013c40f](https://github.com/alexeev-prog/nadzoring/commit/013c40ff17e49bf3333db204c6ecfa40e4467328))
- Update src/nadzoring/security/check_website_ssl_cert.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([53ad47e](https://github.com/alexeev-prog/nadzoring/commit/53ad47e4035d6aa8b4548929ecdbc42d81657296))
- Update src/nadzoring/security/check_website_ssl_cert.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([3509e4a](https://github.com/alexeev-prog/nadzoring/commit/3509e4aa43ac88d11d5e1802a4985c8b8919de3f))
- Update src/nadzoring/network_base/parse_url.py

Co-authored-by: devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>([a595164](https://github.com/alexeev-prog/nadzoring/commit/a595164c155ecf1cf50ba02281ed644cb1734548))
- Update docs([af53f47](https://github.com/alexeev-prog/nadzoring/commit/af53f47594444aa9828277745937af502c757ed7))
- Update docs([3845ecb](https://github.com/alexeev-prog/nadzoring/commit/3845ecbcd96bdd93b866f1fece7565c464f91f4a))
## [0.1.6](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.1.6) - 2026-03-07

### Bug Fixes

- Fix linter errors([77d8adf](https://github.com/alexeev-prog/nadzoring/commit/77d8adf944a14fb97f30b1e96cf598906eab9363))

### Code Refactoring

- Refactor: improve typing annotations([0d1d453](https://github.com/alexeev-prog/nadzoring/commit/0d1d4535570b01eb54054857f9e44aa1296b6c6a))
- Refactor: core-modules (dns_lookup, utils, network_base) and improve docs (add more documentation)([5ef1d68](https://github.com/alexeev-prog/nadzoring/commit/5ef1d68c29f93c4f52d2e826e5a1d53ab4f69c10))

### Documentation

- Docs: update readme and improve docs([e206893](https://github.com/alexeev-prog/nadzoring/commit/e206893ea04a6c19255479fa6192bdf5bff576f4))

### Features

- Feat: add monitor and monitor-report commands([f297d91](https://github.com/alexeev-prog/nadzoring/commit/f297d91437e75e3bba4fd190f6187b417f1f169d))

### Other Changes

- Update readme and versions([3aae4d4](https://github.com/alexeev-prog/nadzoring/commit/3aae4d42a0069781e49ae3c60fd61b43f863e9c6))
- Update changelog([103ad4b](https://github.com/alexeev-prog/nadzoring/commit/103ad4b9975a4885b9969976bc30c54d7d9049c0))
- Update docs & changelog.md([c475b39](https://github.com/alexeev-prog/nadzoring/commit/c475b39fd33bfd9cf40d81de80ed11f55f808f60))
- Update codestyle and typing annotations([4cc42c9](https://github.com/alexeev-prog/nadzoring/commit/4cc42c9c0f5ca44eee69fa52b100c0588d6d46dd))
- Update docs and upload new version: 0.1.6([1a18bba](https://github.com/alexeev-prog/nadzoring/commit/1a18bbae1a5f19410dcc0fa3b5bd5d5400311368))
## [0.1.5](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.1.5) - 2026-03-06

### Bug Fixes

- Fix docs workflow error([2044b89](https://github.com/alexeev-prog/nadzoring/commit/2044b89526ea17f9448bc43a3106cfb1b6ef73c8))
- Fix lint errors([b49de8a](https://github.com/alexeev-prog/nadzoring/commit/b49de8ac513ca68bd8d156f55fab8277dcb6b8d0))
- Fix lint errors([8df04af](https://github.com/alexeev-prog/nadzoring/commit/8df04afeea0c21d3e03ee4351fb243c0b94cb4ca))
- Fix lint errors([fc0ffc9](https://github.com/alexeev-prog/nadzoring/commit/fc0ffc9af0bc884b6ef38ab0e4e8456d1560c194))
- Fix linter errors([35e7ec2](https://github.com/alexeev-prog/nadzoring/commit/35e7ec20431f96a3fcc6e6d014a7e392e09a293a))
- Fix lint error([c43a99a](https://github.com/alexeev-prog/nadzoring/commit/c43a99a1cf153c99e40786af28992bee862cd55d))

### Code Refactoring

- Refactor: update code api, improve code quality([63caf0d](https://github.com/alexeev-prog/nadzoring/commit/63caf0d1d6fde6022cafb111cc80ebf590ca5ebc))

### Other Changes

- Update docs([0000e1f](https://github.com/alexeev-prog/nadzoring/commit/0000e1fa7f57b50233aa62702b5dff04eec01b65))
- Update docs([658b99c](https://github.com/alexeev-prog/nadzoring/commit/658b99c463560a7728cb6826d678c05c6dc6073c))
- Update docs([868ba82](https://github.com/alexeev-prog/nadzoring/commit/868ba82e37076f172552ea8f45f77038faf2474a))
- Update docs([e193f1f](https://github.com/alexeev-prog/nadzoring/commit/e193f1f1288387e81cdb6b64e4186cfdc483e783))
- Update([b93f8d0](https://github.com/alexeev-prog/nadzoring/commit/b93f8d0393d9354cf118cb1d7f43ac6b841d3de5))
- Create pylint.yml([4cf78c0](https://github.com/alexeev-prog/nadzoring/commit/4cf78c09dab6bbbd453949af9c15ae5ca1f9f056))
- Remove pylint workflow([396e873](https://github.com/alexeev-prog/nadzoring/commit/396e873aaf98d07a8710019b0554495834cf123e))
- Update docs (versioning and context7 widget)([7a89167](https://github.com/alexeev-prog/nadzoring/commit/7a89167b6b7ebfa3d7145ab3107785ca4f924552))
- Update docs templates([b1b0789](https://github.com/alexeev-prog/nadzoring/commit/b1b078990f10512ddc4bef8de3c2d9f886f5ed1d))
- Update docs templates([13c8dbd](https://github.com/alexeev-prog/nadzoring/commit/13c8dbdfa64cb93464d29c474f6be94895353cd2))
- Bump actions/upload-pages-artifact from 3 to 4

Bumps [actions/upload-pages-artifact](https://github.com/actions/upload-pages-artifact) from 3 to 4.
- [Release notes](https://github.com/actions/upload-pages-artifact/releases)
- [Commits](https://github.com/actions/upload-pages-artifact/compare/v3...v4)

---
updated-dependencies:
- dependency-name: actions/upload-pages-artifact
  dependency-version: '4'
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([0b1763b](https://github.com/alexeev-prog/nadzoring/commit/0b1763b6ae0786a171a0fc77ed46bf7024a65cec))
- Update docs templates([82c0c81](https://github.com/alexeev-prog/nadzoring/commit/82c0c81ce8c9e1da52aeff60c8053dc5bf14d09b))
- Update docs templates([0f5e61f](https://github.com/alexeev-prog/nadzoring/commit/0f5e61f3005041ac7754a794bf39729a5e08a75a))
- Update docs templates([9e116be](https://github.com/alexeev-prog/nadzoring/commit/9e116bee346eb7a4893fe6a0fc898052e3412ff9))
- Update docs config([5eb2806](https://github.com/alexeev-prog/nadzoring/commit/5eb28060375709a805e33f2467b7d5fa1392d4a8))
- Improve typing annotations in code([ee34a98](https://github.com/alexeev-prog/nadzoring/commit/ee34a9883477ecc7cfa7c763f919f8e1705c4a70))
- Update changelog([680d715](https://github.com/alexeev-prog/nadzoring/commit/680d715f4736f65bc442bf0469eeaba7ecb7ffc6))
- Upload new version: 0.1.5([033617d](https://github.com/alexeev-prog/nadzoring/commit/033617d94b2976147ad3229b32f562d09f043ed8))
## [0.1.4](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.1.4) - 2026-03-04

### Bug Fixes

- Fix test error: network_base.service_on_port unknown->Unknown([ff854de](https://github.com/alexeev-prog/nadzoring/commit/ff854dec517f8680ffb6e2dc3b9ba70f6412e7bc))

### Code Refactoring

- Refactor:update codestyle, docstrings([95cc802](https://github.com/alexeev-prog/nadzoring/commit/95cc802faf98e11d2e3cda67a6116e05c423db68))

### Features

- Add port-scanner command to network-base([8f903e9](https://github.com/alexeev-prog/nadzoring/commit/8f903e9c533bc249e30599b42b8784d60b8930fe))
- Add docs-latest workflow, set docs-stable to publishing release, update docs structure([61980b1](https://github.com/alexeev-prog/nadzoring/commit/61980b16c4b778b9ccb47c8fdc5fcc67b35eb6c8))
- Add http-ping, whois, connections, traceroute, route commands and update docs&readme([573fbe3](https://github.com/alexeev-prog/nadzoring/commit/573fbe3d3bfb170bf82c86640c38436823264df5))
- Add arp spoofing, monitor and cache commands([7afe709](https://github.com/alexeev-prog/nadzoring/commit/7afe709d503ba9938bbf8db13cfc41963d540825))

### Other Changes

- Update docs([4d6f67d](https://github.com/alexeev-prog/nadzoring/commit/4d6f67d81bee6850e05190c0d7d2b83fb963d378))
- Update docstrings, codestyle([c028d3c](https://github.com/alexeev-prog/nadzoring/commit/c028d3ceede175a4c50d81b2dc79dfa2904c785c))
- Update docs([6effb8d](https://github.com/alexeev-prog/nadzoring/commit/6effb8d2672063c98d0c2c9625b1fed6c1fc2279))
- Update init files([e6a7f9a](https://github.com/alexeev-prog/nadzoring/commit/e6a7f9a6d3cabf594bdde391d215bb05bc9cf461))
- Update docs-latest workflow([7ce205e](https://github.com/alexeev-prog/nadzoring/commit/7ce205e1851b739d0efaba61efee684439136a1a))
- Update docs workflow([5ebebf8](https://github.com/alexeev-prog/nadzoring/commit/5ebebf88e7be0c4d2a1afa345017cfc0f93d667b))
- Update docs workflows([5220127](https://github.com/alexeev-prog/nadzoring/commit/52201274fbff72df0b0d181c7cd89af65d3f26d0))
- Update (fix) docs workflows([ebcd0bc](https://github.com/alexeev-prog/nadzoring/commit/ebcd0bcaca0b671fd0995476964cd6be1f136f6e))
- Update (fix) docs workflows([a03a9e9](https://github.com/alexeev-prog/nadzoring/commit/a03a9e9f29ad0bfbadb36a740e32754a799a041d))
- Update docs workflows([27645f9](https://github.com/alexeev-prog/nadzoring/commit/27645f9d3aa59dcf9e4c9a855196d89069cad733))
- Update docs workflows([3aaf4b1](https://github.com/alexeev-prog/nadzoring/commit/3aaf4b1894d4fc108e661146d053db5c4e6e6c0f))
- Update docs workflows([e56c87c](https://github.com/alexeev-prog/nadzoring/commit/e56c87c184b22539ad882dc51f2825dd04bd275d))
- Update docs workflows([cced4f3](https://github.com/alexeev-prog/nadzoring/commit/cced4f38d0586e289d7c21052bda206fddfcf30e))
- Update docs workflows([bc4b66b](https://github.com/alexeev-prog/nadzoring/commit/bc4b66b6bcda5d806140db909962c97f77d530f1))
- Update docs workflows([2e34ff1](https://github.com/alexeev-prog/nadzoring/commit/2e34ff1cc2a7ef64546bf0b2b34962bdfee10fc0))
- Update docs workflows([2a39540](https://github.com/alexeev-prog/nadzoring/commit/2a395409d99aafb012ea5c100afbea9e577e1b6b))
- Update docs workflows([95c2919](https://github.com/alexeev-prog/nadzoring/commit/95c29196a0d4acc9149d5185787ef6d795fda4f8))
- Update docs workflows([49813a3](https://github.com/alexeev-prog/nadzoring/commit/49813a317c530c5224e5668940c260d1c43f49c6))
- Update docs workflows([b9ba880](https://github.com/alexeev-prog/nadzoring/commit/b9ba8802494836161f18474bed05c1ab129b40b0))
- Update docs workflows([bd06f56](https://github.com/alexeev-prog/nadzoring/commit/bd06f56ce2b42f4ecc432ef5473eeb97ac291f43))
- Update docs workflows([44d27db](https://github.com/alexeev-prog/nadzoring/commit/44d27db58b9d26bf4ca13a18c941431dbdfd202b))
- Updatw changelog([3522855](https://github.com/alexeev-prog/nadzoring/commit/3522855786e28eae7b5390cf7ccc1faf05aa174e))
- Updatw docs workflow (fix)([915ff31](https://github.com/alexeev-prog/nadzoring/commit/915ff318063533b8abf9a72aacd6f530f89d34e1))
- Remove index.html([2b9dce7](https://github.com/alexeev-prog/nadzoring/commit/2b9dce76b71ddc398874a21a26bc565a92acd38e))
- Update docs([8e47258](https://github.com/alexeev-prog/nadzoring/commit/8e4725890c2c2ee651e30517ef57191cc6fb1c87))
- Update docs([c2e2794](https://github.com/alexeev-prog/nadzoring/commit/c2e27945ffe5120ee420b43bdb7ee294267e18ac))
- Update docs (fix)([0d1a070](https://github.com/alexeev-prog/nadzoring/commit/0d1a070958610911e53f6723c918a30ea0dc7d4f))
- Update docs (fix)([6542c3c](https://github.com/alexeev-prog/nadzoring/commit/6542c3c554be2d66eb5f67fb7fc72cb477521d14))
- Update docs (fix)([a8da6e0](https://github.com/alexeev-prog/nadzoring/commit/a8da6e08eef4c76ab75af02cd257dfa4678f0cea))
- Update docs (fix)([65fda52](https://github.com/alexeev-prog/nadzoring/commit/65fda52a35ad57afec64be1fa9d08ce99dfe7b33))
- Update docs (fix)([7dfa963](https://github.com/alexeev-prog/nadzoring/commit/7dfa963ead3e27386549af2f245907e88af0adc5))
- Update docs (fix)([214f0a7](https://github.com/alexeev-prog/nadzoring/commit/214f0a70448510c0dc1972d2d4c82b268622cc54))
- Update docs (fix)([4976dee](https://github.com/alexeev-prog/nadzoring/commit/4976deee9857a1d3545999edb80d709048be5417))
- Update docs (fix)([60f7d1d](https://github.com/alexeev-prog/nadzoring/commit/60f7d1d1fe6b8d0cd6def370e991637a9f70644c))
- Update docs (fix)([764a9b0](https://github.com/alexeev-prog/nadzoring/commit/764a9b07ba50d2e09c3143db0bd49390020ceffb))
- Update docs (fix)([372c65a](https://github.com/alexeev-prog/nadzoring/commit/372c65a0be7b46d7395c537d1c0b91a212245ac6))
- Update docs (fix)([9b3ca77](https://github.com/alexeev-prog/nadzoring/commit/9b3ca77695966f06ceb0d8cae951621013be32bd))
- Update docs (fix)([3309157](https://github.com/alexeev-prog/nadzoring/commit/3309157d26184d12d50f3b130749bdf086d66304))
- Update docs (fix)([c270b1d](https://github.com/alexeev-prog/nadzoring/commit/c270b1d650d1ca652755f36954921d8c66e4e8b5))
- Update docs (fix)([86659ce](https://github.com/alexeev-prog/nadzoring/commit/86659ce4b21779544af593b32bc2c805f1a2d8ea))
- Update docs (fix)([792f003](https://github.com/alexeev-prog/nadzoring/commit/792f003a3eb45b0ed76ff3b2a917be030d86c268))
- Update docs (fix)([f5d855c](https://github.com/alexeev-prog/nadzoring/commit/f5d855c58b855ce31b9827e2dbaa71148e2b26ac))
- Update docs (fix)([82611b5](https://github.com/alexeev-prog/nadzoring/commit/82611b59e5fd553ef186aee4b1697a20001cd1e8))
- Update docs (fix)([b81e67e](https://github.com/alexeev-prog/nadzoring/commit/b81e67e2c397880ab7bcbdf8bb1a0c703a4101c2))
- Update docs (fix)([1cdcc35](https://github.com/alexeev-prog/nadzoring/commit/1cdcc3562f12f51d1175e08e0544ce83b29dca46))
- Update docs (fix)([437618e](https://github.com/alexeev-prog/nadzoring/commit/437618e209d917215ad895af8e14a6e5a4ed32ee))
- Update docs (fix)([8757b2e](https://github.com/alexeev-prog/nadzoring/commit/8757b2ed06ad73ea9539e7dd2150c1b10cf753b3))
- Update docs (fix)([e10ed0e](https://github.com/alexeev-prog/nadzoring/commit/e10ed0e545f91863aa76695ae2e5fb4ffd617d18))
- Update docs (fix)([40a6f27](https://github.com/alexeev-prog/nadzoring/commit/40a6f27993ee48560177c9c0ae132470e85682a7))
- Update docs (fix)([6029c8a](https://github.com/alexeev-prog/nadzoring/commit/6029c8a593b47ae1a18e57ab4b87c4811bd642e2))
- Update docs (fix)([cd0362b](https://github.com/alexeev-prog/nadzoring/commit/cd0362ba1b5ca4994d24d9607b252985a9e706bf))
- Update docs (finally([bf29a83](https://github.com/alexeev-prog/nadzoring/commit/bf29a835523cc5d91dd7a2850cdef18ddce97330))
- Update latest-docs([8c151e0](https://github.com/alexeev-prog/nadzoring/commit/8c151e0560c51f7211f21ef111fa66f0c9c88dde))
- Update docs and publish release([73bad5f](https://github.com/alexeev-prog/nadzoring/commit/73bad5f352c399eb8f28fce620fd45874aa1ca9f))
## [0.1.3](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.1.3) - 2026-02-25

### Other Changes

- Update license([e68efbb](https://github.com/alexeev-prog/nadzoring/commit/e68efbb29cfc29741b5aacdd147a5bda03a74c71))
- Update dns-commands and dns lookup, utils([921d512](https://github.com/alexeev-prog/nadzoring/commit/921d51276b2e678effefcbf7ff5bec9aade724c8))
- Update docstring([2fe0587](https://github.com/alexeev-prog/nadzoring/commit/2fe05871e0b8f739ac50b3f9ec3fcd770af92731))
- Update typing([ea14df8](https://github.com/alexeev-prog/nadzoring/commit/ea14df8d7b78be598450cbea55b23988eb738294))
- Update readme and upload 0.1.3([a246608](https://github.com/alexeev-prog/nadzoring/commit/a2466088ff4ff968923cb0010fd7b5c053d25653))
## [0.1.2](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.1.2) - 2026-02-23

### Features

- Add commands for get location by ip and improve network-params([0301430](https://github.com/alexeev-prog/nadzoring/commit/030143040cf4289f026c8c5893114132c0868698))
- Add help for commands([64afd30](https://github.com/alexeev-prog/nadzoring/commit/64afd30a00427af05fcdf48d07b1abd5dd4809c8))
- Create `dns` command group; split architecture cli.py -> commands modules group([926a5ea](https://github.com/alexeev-prog/nadzoring/commit/926a5eae9af473b0048faa45c1da51707fe9266d))

### Other Changes

- Update docs and load 0.1.2([d0b3908](https://github.com/alexeev-prog/nadzoring/commit/d0b39089a8f9a16748dd47a69bd4ba8bad0e5960))
## [0.1.1](https://github.com/alexeev-prog/nadzoring/releases/tag/v0.1.1) - 2026-02-20

### Features

- Create basic structure([ef5dec0](https://github.com/alexeev-prog/nadzoring/commit/ef5dec057758497001394b010dcfe6c7def62f0c))
- Add get-network-params and ping-address commands([113a208](https://github.com/alexeev-prog/nadzoring/commit/113a20855d679499c361fd3b56810c6260be2ede))
- Add public ip to network params; release 0.1.1([eeaae18](https://github.com/alexeev-prog/nadzoring/commit/eeaae18a16077d09efe52ceef289e0c6603f7a49))

### Other Changes

- Initial commit([d1462c8](https://github.com/alexeev-prog/nadzoring/commit/d1462c8621dbffbf488084260507937dcedc6f39))
- Bump actions/setup-python from 5 to 6

Bumps [actions/setup-python](https://github.com/actions/setup-python) from 5 to 6.
- [Release notes](https://github.com/actions/setup-python/releases)
- [Commits](https://github.com/actions/setup-python/compare/v5...v6)

---
updated-dependencies:
- dependency-name: actions/setup-python
  dependency-version: '6'
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>([ab14def](https://github.com/alexeev-prog/nadzoring/commit/ab14defee8ebc8ba976ff67ddc1c46770b3a5ef2))
- Update tests([dac508e](https://github.com/alexeev-prog/nadzoring/commit/dac508e4371aec6586445fd6fa547e373a53cabf))
- Update docs([c0c7425](https://github.com/alexeev-prog/nadzoring/commit/c0c74257ad27c31bef2522a541db32834c9e0444))
- Improve CLI App UX/UI and publish package; update readme([cefba08](https://github.com/alexeev-prog/nadzoring/commit/cefba08c660df0085bd752a4284b359873543f44))
- Update readme([79d5e1e](https://github.com/alexeev-prog/nadzoring/commit/79d5e1e3b1a8b7fc1e0ac09287ad47ff1c25ee0e))
- Update docs([75df49a](https://github.com/alexeev-prog/nadzoring/commit/75df49a4cf5c33641d9fbd73ffc609e1b2636dd8))
- Update docs([ac27677](https://github.com/alexeev-prog/nadzoring/commit/ac276777a56a1744771d1bf9d130660cd7b2196a))
- Update typing([8c1cd9f](https://github.com/alexeev-prog/nadzoring/commit/8c1cd9fc7d8d5dea8b30d84ebf5ccff9da261499))
- Update docs([ca4ce9f](https://github.com/alexeev-prog/nadzoring/commit/ca4ce9f8722613118da634be131cf7fdd9fca552))
