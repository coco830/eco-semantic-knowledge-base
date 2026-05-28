# 共性与特殊性分析

## 方法

本知识库不把行业代码和排污许可类型当作最终企业画像，而把它们作为默认召回入口。真正的知识本体是产污场景、设施/风险单元、证据要求、现场排查项和 EcoCheck 13 维映射。31 条现有规则被收敛为 11 个场景模板，其中 10 个为产污/风险模板，1 个为治理语义补强模板。

## 跨行业共性场景

- `SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER`
- `SCN_WW_PROCESS_AND_TREATMENT`
- `SCN_VOCS_SOLVENT_AND_TREATMENT`
- `SCN_HAZWASTE_STORAGE_TRANSFER`
- `SCN_RAINWATER_ACCIDENT_EMERGENCY`

这些场景可跨医疗、印刷、涂料、塑料、食品饮料、金属结构、水泥、造纸等行业复用。差异主要由原辅料、产能、是否重点管理、是否存在通用工序、是否纳入重点排污单位名录触发。

## 行业特殊场景

- `SCN_MEDICAL_WASTE_RADIATION`
- `SCN_GAS_STATION_VAPOR_UST`
- `SCN_DUST_PARTICULATE_CONTROL`
- `SCN_CHEMICAL_TANK_LDAR_SEEPAGE`
- `SCN_ONLINE_MONITORING_KEY_UNIT`

医疗机构突出医废、医疗废水和放射诊疗；加油站突出油气回收、地下储罐和土壤地下水；水泥/石灰石膏突出粉尘颗粒物；涂料、印刷、人造革等突出 VOCs、LDAR、危废和罐区。

## 必须 ESO/ETO 现场确认的边界

- `1512` 在本地 GB/T 4754-2017 注释中为白酒制造，现有 JSON 写作啤酒制造，需确认是否应改为 `1513`。
- `1521` 是碳酸饮料制造，若业务意图是泛饮料制造，不应只用单一小类代表全部饮料。
- `1371`、`3311` 的许可类型高度依赖锅炉、工业炉窑、表面处理、水处理等通用工序，不能仅靠行业代码定型。
- `2211`、`2231` 存在中类/代表性小类下沉问题，需确认覆盖范围。
- `UNKNOWN` 不是否定，而是现场确认入口；默认画像必须由环评、批复、排污许可、台账和现场事实修正。
