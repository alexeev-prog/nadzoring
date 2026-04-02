# Changelog
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
