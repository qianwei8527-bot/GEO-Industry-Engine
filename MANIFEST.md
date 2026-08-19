# V10.6-PANORAMA-SKELETON-01 全景骨架交付 MANIFEST

- 任务编号：V10.6-PANORAMA-SKELETON-01
- 前置版本：V10.6-R3-FIX2.1-FINAL-FREEZE
- 策略调整：先完成全产品骨架和模拟交互，再按价值优先级接入真实后端
- R4 状态：acceptance_blocked
- 是否允许部署：否
- 是否允许提交或推送：否
- 交付包：V10.6-PANORAMA-SKELETON-全景骨架-执行文件.zip

## 文件清单（ZIP 路径 / 仓库源路径 / SHA-256）

`MANIFEST.md` 为本清单文件，不计算自身哈希；ZIP 内路径全部为 ASCII。

| ZIP路径（ASCII） | 仓库源路径 | SHA-256 |
| --- | --- | --- |
| docs/18-5_V10.6-PANORAMA-SKELETON-01-report.md | docs/18-5_V10.6-PANORAMA-SKELETON-01-report.md | FBE41B2A236C8F35A69B83DFAEDC0FB304702D047C5EA0EFAD6C3757095ACCAD |
| docs/V10.6-PANORAMA-code-change-list.md | docs/V10.6-PANORAMA-code-change-list.md | A4FC0FE8F4E17872F2A7A5D29381D050EF3AEE3A05C3AA5A3E383C787C25C16E |
| docs/v106-all-pages-design-preview.html | docs/v106-all-pages-design-preview.html | 6E345D17EBA3A6F59EF43D29941C66ECEDF07028E1E0DEEAB6E8CD33A6A028D6 |
| config/panorama/page-registry.json | config/panorama/page-registry.json | 535B1822657DA88529D96D7192582136F07ED12AD34B45654843DE4D18897426 |
| config/panorama/fixture-registry.json | config/panorama/fixture-registry.json | 367E67826ADC267D49276446A8F65E3FC9E291C79F6EE17ACAA9695E465FC60B |
| config/panorama/capability-map.json | config/panorama/capability-map.json | 69AD89A768898D72E0793F0F7136E0F1983B387DDC2D4AE9276681412D8E4153 |
| frontend/src/app/panorama/page.tsx | frontend/src/app/panorama/page.tsx | 9DAF397B8C0B42724791BB16F4D191610D3F1BEF32FA8A3CE0A849253A82728C |
| frontend/src/app/v106-all-pages-design-preview/route.ts | frontend/src/app/v106-all-pages-design-preview/route.ts | 3D2B9923A75F32604F766F14F8470D2CEE5D8D35992F01825FDEEE07983A072F |
| frontend/src/components/panorama/panorama-explorer.tsx | frontend/src/components/panorama/panorama-explorer.tsx | D8991E53901BFA4D6E8C6A106769AC37DD807962C1A4CEA99BB4B2D4673C4F1C |
| frontend/src/lib/panorama/types.ts | frontend/src/lib/panorama/types.ts | 370275A21F85EAC52BB46A3126C04705BD28069378650B0B864EC70F904CB663 |
| frontend/src/components/app-shell/surface-config.ts | frontend/src/components/app-shell/surface-config.ts | 2A1E708F79E796016C4B8DD76151B8CDE9FF00FA7CC72AA5DCD3DB46754E290B |
| frontend/src/components/Header.tsx | frontend/src/components/Header.tsx | C075C0CE133AFE13ABD470BE25C31BFB6251687B23D9A70863542340A475C3B6 |
| frontend/scripts/check-v106-preview.mjs | frontend/scripts/check-v106-preview.mjs | 50AB49AAF19827E85AFB5483CE72C6FB67D6B472A5461D63D18BF35CF6394AD5 |
| frontend/scripts/capture-v106-panorama-screenshots.mjs | frontend/scripts/capture-v106-panorama-screenshots.mjs | 5AB4D0B89436AA109F5A19EB623DC262C909784F5B58A241D7CFCD89C79F2197 |
| frontend/tests/operations/operations-adapter.test.ts | frontend/tests/operations/operations-adapter.test.ts | 32801640D6EB1D96DF7B0A8E11C16C5692AC0054BDE5842D9D4B68D05B856751 |
| scripts/check_v106_panorama_skeleton.py | scripts/check_v106_panorama_skeleton.py | 81D9722E28C02696616CECA47ACB4AEDB73E5C7668DA98B0684F507A4B7E4D8D |
| scripts/generate_v106_panorama_fixtures.py | scripts/generate_v106_panorama_fixtures.py | 953BB2980C76305A3D1817CD971C1278C64C8CCAC57E969D357D475AFA6AEE80 |
| scripts/build_v106_panorama_manifest.py | scripts/build_v106_panorama_manifest.py | 5502B7618661B55A170E691A3D1AD6B60BB99F04A853B43ADBD34B8184B9EB33 |
| scripts/verify_v106_panorama_package.py | scripts/verify_v106_panorama_package.py | 942EEF7BE53A2D75D790EB8AC9CE5D945C45241F8D927FADD6100B5D6FAD1D86 |
| docs/generated_images/V10.6-PANORAMA-01-overview.png | docs/generated_images/V10.6-PANORAMA-01-overview.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-NARROW-governance.png | docs/generated_images/V10.6-PANORAMA-NARROW-governance.png | 7A945E7FEF34ACB28D84E93541247D0397AEE6E919E31E8AC832892F37E72B31 |
| docs/generated_images/V10.6-PANORAMA-NARROW-operations.png | docs/generated_images/V10.6-PANORAMA-NARROW-operations.png | 07BA3172C22B0517CFA15E45DB1CEC58B129592C7F408E0B3C4CCED55E276AD3 |
| docs/generated_images/V10.6-PANORAMA-NARROW-owner.png | docs/generated_images/V10.6-PANORAMA-NARROW-owner.png | EC27F708EE70567621E9895DF0EC31499C54DD42784B7106E98EFDA9CFFCC32C |
| docs/generated_images/V10.6-PANORAMA-NARROW-public.png | docs/generated_images/V10.6-PANORAMA-NARROW-public.png | A2004D5451F98756296286235C00E81D879F0C8E008D8B1E4CDF0831A84008C3 |
| docs/generated_images/V10.6-PANORAMA-PAGE-backend-data.png | docs/generated_images/V10.6-PANORAMA-PAGE-backend-data.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-backend-flow.png | docs/generated_images/V10.6-PANORAMA-PAGE-backend-flow.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-backend-primitives.png | docs/generated_images/V10.6-PANORAMA-PAGE-backend-primitives.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-backend-runtime.png | docs/generated_images/V10.6-PANORAMA-PAGE-backend-runtime.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-backend-security.png | docs/generated_images/V10.6-PANORAMA-PAGE-backend-security.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-gov-approvals.png | docs/generated_images/V10.6-PANORAMA-PAGE-gov-approvals.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-gov-audit.png | docs/generated_images/V10.6-PANORAMA-PAGE-gov-audit.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-gov-collective.png | docs/generated_images/V10.6-PANORAMA-PAGE-gov-collective.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-gov-evidence.png | docs/generated_images/V10.6-PANORAMA-PAGE-gov-evidence.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-gov-external-actions.png | docs/generated_images/V10.6-PANORAMA-PAGE-gov-external-actions.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-gov-permissions.png | docs/generated_images/V10.6-PANORAMA-PAGE-gov-permissions.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-gov-realm-claims.png | docs/generated_images/V10.6-PANORAMA-PAGE-gov-realm-claims.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-gov-retention.png | docs/generated_images/V10.6-PANORAMA-PAGE-gov-retention.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-gov-risk.png | docs/generated_images/V10.6-PANORAMA-PAGE-gov-risk.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-mid-assets.png | docs/generated_images/V10.6-PANORAMA-PAGE-mid-assets.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-mid-customer-positioning.png | docs/generated_images/V10.6-PANORAMA-PAGE-mid-customer-positioning.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-mid-demand.png | docs/generated_images/V10.6-PANORAMA-PAGE-mid-demand.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-mid-evidence.png | docs/generated_images/V10.6-PANORAMA-PAGE-mid-evidence.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-mid-governance.png | docs/generated_images/V10.6-PANORAMA-PAGE-mid-governance.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-mid-identity.png | docs/generated_images/V10.6-PANORAMA-PAGE-mid-identity.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-mid-policy.png | docs/generated_images/V10.6-PANORAMA-PAGE-mid-policy.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-mid-project.png | docs/generated_images/V10.6-PANORAMA-PAGE-mid-project.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-mid-tools.png | docs/generated_images/V10.6-PANORAMA-PAGE-mid-tools.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-mid-workflow.png | docs/generated_images/V10.6-PANORAMA-PAGE-mid-workflow.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-mid-world.png | docs/generated_images/V10.6-PANORAMA-PAGE-mid-world.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-ops-agents.png | docs/generated_images/V10.6-PANORAMA-PAGE-ops-agents.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-ops-alerts.png | docs/generated_images/V10.6-PANORAMA-PAGE-ops-alerts.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-ops-capabilities.png | docs/generated_images/V10.6-PANORAMA-PAGE-ops-capabilities.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-ops-connectors.png | docs/generated_images/V10.6-PANORAMA-PAGE-ops-connectors.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-ops-overview.png | docs/generated_images/V10.6-PANORAMA-PAGE-ops-overview.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-ops-realms.png | docs/generated_images/V10.6-PANORAMA-PAGE-ops-realms.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-ops-reports.png | docs/generated_images/V10.6-PANORAMA-PAGE-ops-reports.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-ops-runtime.png | docs/generated_images/V10.6-PANORAMA-PAGE-ops-runtime.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-ops-system.png | docs/generated_images/V10.6-PANORAMA-PAGE-ops-system.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-ops-workflows.png | docs/generated_images/V10.6-PANORAMA-PAGE-ops-workflows.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-owner-collective.png | docs/generated_images/V10.6-PANORAMA-PAGE-owner-collective.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-owner-customers.png | docs/generated_images/V10.6-PANORAMA-PAGE-owner-customers.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-owner-execution.png | docs/generated_images/V10.6-PANORAMA-PAGE-owner-execution.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-owner-intel.png | docs/generated_images/V10.6-PANORAMA-PAGE-owner-intel.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-owner-market.png | docs/generated_images/V10.6-PANORAMA-PAGE-owner-market.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-owner-policy.png | docs/generated_images/V10.6-PANORAMA-PAGE-owner-policy.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-owner-projects.png | docs/generated_images/V10.6-PANORAMA-PAGE-owner-projects.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-owner-results.png | docs/generated_images/V10.6-PANORAMA-PAGE-owner-results.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-owner-today.png | docs/generated_images/V10.6-PANORAMA-PAGE-owner-today.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-owner-tools.png | docs/generated_images/V10.6-PANORAMA-PAGE-owner-tools.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-panorama.png | docs/generated_images/V10.6-PANORAMA-PAGE-panorama.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-public-client.png | docs/generated_images/V10.6-PANORAMA-PAGE-public-client.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-public-home.png | docs/generated_images/V10.6-PANORAMA-PAGE-public-home.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-public-intake.png | docs/generated_images/V10.6-PANORAMA-PAGE-public-intake.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-PAGE-public-market.png | docs/generated_images/V10.6-PANORAMA-PAGE-public-market.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-STATE-canvas-blocked.png | docs/generated_images/V10.6-PANORAMA-STATE-canvas-blocked.png | DB1050443185E898D133E9EC7AE9ED9535C975F54F0ACFB7E5EEAF8C97059BFA |
| docs/generated_images/V10.6-PANORAMA-STATE-canvas-empty.png | docs/generated_images/V10.6-PANORAMA-STATE-canvas-empty.png | 55A1BB74EADEFF6775399A45F5111A69E7D13875755620A67C63311533C8D663 |
| docs/generated_images/V10.6-PANORAMA-STATE-canvas-error.png | docs/generated_images/V10.6-PANORAMA-STATE-canvas-error.png | 6EF1FD9A36F3A7D2FBA26E4DC4DF9BE7C05F84F4A203A9E70F8250BE5E817CED |
| docs/generated_images/V10.6-PANORAMA-STATE-canvas-loading.png | docs/generated_images/V10.6-PANORAMA-STATE-canvas-loading.png | B57F91AF2CD8271046012E7B9EF5F618113DAB73149AF70A85B4781B2E80D504 |
| docs/generated_images/V10.6-PANORAMA-STATE-canvas-no_permission.png | docs/generated_images/V10.6-PANORAMA-STATE-canvas-no_permission.png | 23DFA71E0ACE08C2883E19DF432A955D9157FC55FF1E0CCA56A8F0636178E11A |
| docs/generated_images/V10.6-PANORAMA-STATE-canvas-normal.png | docs/generated_images/V10.6-PANORAMA-STATE-canvas-normal.png | 6AB531BF911E4B8BDCDC1B4049C0E30810FE6FB9F350AE37780652C00995254A |
| docs/generated_images/V10.6-PANORAMA-STATE-canvas-partial.png | docs/generated_images/V10.6-PANORAMA-STATE-canvas-partial.png | 06A30D83C1B5EF9F46E1B1B4F442506A16E30E07B4786A7BF6E260791E6A804E |
| docs/generated_images/V10.6-PANORAMA-STATE-config-blocked.png | docs/generated_images/V10.6-PANORAMA-STATE-config-blocked.png | 694D3DC520F9EA6079F46A227CEED456387D5B61DCE8FA3B33CAFA6ED000551B |
| docs/generated_images/V10.6-PANORAMA-STATE-config-empty.png | docs/generated_images/V10.6-PANORAMA-STATE-config-empty.png | F7CF33B89E4127DCF39A152F1F8BED82DA27B5E77483C27AF0B9373AA3CC97D8 |
| docs/generated_images/V10.6-PANORAMA-STATE-config-error.png | docs/generated_images/V10.6-PANORAMA-STATE-config-error.png | 9FF661B24281692213FD722C0318C7D3644FA57F22A792E2A0BBFDF2B460ADDE |
| docs/generated_images/V10.6-PANORAMA-STATE-config-loading.png | docs/generated_images/V10.6-PANORAMA-STATE-config-loading.png | 7F2CFA55DD1F9245ADF99CA8529A06A657AC2F78B57BCFF4C47E13D018A0ED66 |
| docs/generated_images/V10.6-PANORAMA-STATE-config-no_permission.png | docs/generated_images/V10.6-PANORAMA-STATE-config-no_permission.png | F4811C4FB75ACF33B52046B7A154C2F371D7204DB486C80F09600A8B3EDE9CD2 |
| docs/generated_images/V10.6-PANORAMA-STATE-config-normal.png | docs/generated_images/V10.6-PANORAMA-STATE-config-normal.png | 9625735C4726ADA0E381E05CB5D9BF99354D0B4FE454C921EC40ED0F53145FF0 |
| docs/generated_images/V10.6-PANORAMA-STATE-config-partial.png | docs/generated_images/V10.6-PANORAMA-STATE-config-partial.png | 2BC1B48B9006B5B58932B6B6B8E6E9878C3778EEABF4AB08C7A69E3DDA42D2EB |
| docs/generated_images/V10.6-PANORAMA-STATE-detail-blocked.png | docs/generated_images/V10.6-PANORAMA-STATE-detail-blocked.png | 22019BBC92495CB598A0878B04E744AF202944EEDE2A896C918B044D7520C414 |
| docs/generated_images/V10.6-PANORAMA-STATE-detail-empty.png | docs/generated_images/V10.6-PANORAMA-STATE-detail-empty.png | 1E46877666F5C49B7ED3CA884ED6E74719442C56CD2704B08DDCC2CE751A058E |
| docs/generated_images/V10.6-PANORAMA-STATE-detail-error.png | docs/generated_images/V10.6-PANORAMA-STATE-detail-error.png | C69AB6F346EB9F1AFACA43088AAEFBF8B50110E9B2570DD309D2FA9550942FAC |
| docs/generated_images/V10.6-PANORAMA-STATE-detail-loading.png | docs/generated_images/V10.6-PANORAMA-STATE-detail-loading.png | D191FB778F1212F4E3A406A6D8B904415BDB6AACABDE4AC5800F88E10AB65F04 |
| docs/generated_images/V10.6-PANORAMA-STATE-detail-no_permission.png | docs/generated_images/V10.6-PANORAMA-STATE-detail-no_permission.png | 1A2E7880273369106D3BD3B8A7050910BF426B8195F0B7559D06752B78D5D614 |
| docs/generated_images/V10.6-PANORAMA-STATE-detail-normal.png | docs/generated_images/V10.6-PANORAMA-STATE-detail-normal.png | AADE142111A174C22A16F9B4C827E109DB4129093BBE7D7EE8E6FAB4545C64FE |
| docs/generated_images/V10.6-PANORAMA-STATE-detail-partial.png | docs/generated_images/V10.6-PANORAMA-STATE-detail-partial.png | 7C69022E065EAAECBB8D76B018D619692F531636877F6B0B3F5C767286580BA4 |
| docs/generated_images/V10.6-PANORAMA-STATE-list-blocked.png | docs/generated_images/V10.6-PANORAMA-STATE-list-blocked.png | 9E4A21D05FBF2B5990E9155017B6ED7F8F163734D837770B1518F129049A262A |
| docs/generated_images/V10.6-PANORAMA-STATE-list-empty.png | docs/generated_images/V10.6-PANORAMA-STATE-list-empty.png | 94F2FDC688F67A39051C58AA0774DC10E72FB5D61B58F0B113C2FB0683070B70 |
| docs/generated_images/V10.6-PANORAMA-STATE-list-error.png | docs/generated_images/V10.6-PANORAMA-STATE-list-error.png | 0A0BEDA26184317C0D430E9545F0E02DCDD4B0DE45378C30B48FDAEDA3F08FD6 |
| docs/generated_images/V10.6-PANORAMA-STATE-list-loading.png | docs/generated_images/V10.6-PANORAMA-STATE-list-loading.png | 065E1E28F7CF94603A2053D2DA22A6558EFADF25A24EFDFD0990368FB20210AB |
| docs/generated_images/V10.6-PANORAMA-STATE-list-no_permission.png | docs/generated_images/V10.6-PANORAMA-STATE-list-no_permission.png | 91290FE3774D052DDFFCE09898DBA54DE4A39AD9B5A10EA804209A63D39F4D81 |
| docs/generated_images/V10.6-PANORAMA-STATE-list-normal.png | docs/generated_images/V10.6-PANORAMA-STATE-list-normal.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-STATE-list-partial.png | docs/generated_images/V10.6-PANORAMA-STATE-list-partial.png | 35E9F89C9985BAF764FCD0464FAC8CCEA85E674B623E636A4BF2D9622F08DC8C |
| docs/generated_images/V10.6-PANORAMA-STATE-management-blocked.png | docs/generated_images/V10.6-PANORAMA-STATE-management-blocked.png | 0B6D9B7FD5CB05DB5F76216349AC1EA11F2EE8C6B58A3864C141DAAB107B74B5 |
| docs/generated_images/V10.6-PANORAMA-STATE-management-empty.png | docs/generated_images/V10.6-PANORAMA-STATE-management-empty.png | BCD46A05A7DDC65F7A7E9D3D559168C776C27B7A79CE70BAE0EA74BF60C9F168 |
| docs/generated_images/V10.6-PANORAMA-STATE-management-error.png | docs/generated_images/V10.6-PANORAMA-STATE-management-error.png | 98607B77F22A1DCEC4947B8F96535C1E1CBE6DA9649C6A23281B1AD3A793795F |
| docs/generated_images/V10.6-PANORAMA-STATE-management-loading.png | docs/generated_images/V10.6-PANORAMA-STATE-management-loading.png | F4423267FC4344CB607650E78F3236D6F50D6F5B821215127E002A8F6EF22B8B |
| docs/generated_images/V10.6-PANORAMA-STATE-management-no_permission.png | docs/generated_images/V10.6-PANORAMA-STATE-management-no_permission.png | 3123512609C1BA02BEEFC49BD5CA7EED79CAF2766C755330BB0286770E5CB9EB |
| docs/generated_images/V10.6-PANORAMA-STATE-management-normal.png | docs/generated_images/V10.6-PANORAMA-STATE-management-normal.png | 039666B3DFECC64AF283DB147099D6F81937447667C151A7A123B31BBA36A9D9 |
| docs/generated_images/V10.6-PANORAMA-STATE-management-partial.png | docs/generated_images/V10.6-PANORAMA-STATE-management-partial.png | 60BFF803F3D746A776633D0672A1CABB1FF5621534F9E8022FBBD3CAB8D88F88 |
| docs/generated_images/V10.6-PANORAMA-STATE-workbench-blocked.png | docs/generated_images/V10.6-PANORAMA-STATE-workbench-blocked.png | BEFCED9A18643C4FA3CD74390BCD8D61AAAE3C6C0C9C1D492F902A2FB317B28A |
| docs/generated_images/V10.6-PANORAMA-STATE-workbench-empty.png | docs/generated_images/V10.6-PANORAMA-STATE-workbench-empty.png | 44C2A3F83E48329297DC7D63680E81D272DDCF3C587A29DA2992133AD0DB8B6E |
| docs/generated_images/V10.6-PANORAMA-STATE-workbench-error.png | docs/generated_images/V10.6-PANORAMA-STATE-workbench-error.png | 4643B351D2D2AB6DF8F830B8F4D15D4BB2ED33AC1ED4EB9F3D3ADA5C1AD27CC1 |
| docs/generated_images/V10.6-PANORAMA-STATE-workbench-loading.png | docs/generated_images/V10.6-PANORAMA-STATE-workbench-loading.png | 80B3F80C82304F7974AC5BE549D92976FDA00BEC5B738A0F15147CA6741C7B40 |
| docs/generated_images/V10.6-PANORAMA-STATE-workbench-no_permission.png | docs/generated_images/V10.6-PANORAMA-STATE-workbench-no_permission.png | 31B014F0EE531F0A40EA9F83F9ED000FA11815D96FDAAEDDD537EE21086C253B |
| docs/generated_images/V10.6-PANORAMA-STATE-workbench-normal.png | docs/generated_images/V10.6-PANORAMA-STATE-workbench-normal.png | 145762B71A4DE4F980FE0264FB8CDCBFC43DAEDC865916D8CE9FC0844DB82A4F |
| docs/generated_images/V10.6-PANORAMA-STATE-workbench-partial.png | docs/generated_images/V10.6-PANORAMA-STATE-workbench-partial.png | 3AF25CF4ADDFF989BACF7857997F3133EFE9ED3B9898BEC875F08991DB82923C |

## 测试结果摘要

- 前端测试：28 passed。
- TypeScript：通过。
- lint：通过，仅仓库原有 4 项 warning。
- production build：通过，55 个路由，含 `/panorama`。
- 预览检查：PASS pages=50 meta=50 registry=50 fixtures=50。
- 骨架完整性：PASS pages=50 fixtures=50 midplatforms=10 bases=3。
- 截图与路由 Smoke：PASS pages=50 states=42 narrow=4 errors=0。

## 未完成项

- R5、今日工作真实聚合、政策/市场/态势/共同治理真实业务未开发。
- R4 保持 `acceptance_blocked`，待策略确认后再继续。

## 已知风险

- 全景骨架使用 Fixture 模拟数据，不伪装成真实数据。
- 后续真实 API 接入时，通过统一 Adapter 替换 Fixture，不重写页面。

## 敏感信息检查结果

- 未包含 `.env`、Token、API Key、数据库、缓存、日志、`.next`、`node_modules` 或旧 ZIP。
- 所有截图来自脱机预览与本地 `/panorama` Fixture 路由。
