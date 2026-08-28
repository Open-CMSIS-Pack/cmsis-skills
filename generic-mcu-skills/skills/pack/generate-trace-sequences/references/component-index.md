# Component asset index

Read this file first, then load only the selected component assets. Every path below is relative to the skill root, not to this `references/` directory. The XML assets are canonical semantic templates for both PDSC and `cbuild-run` output; use the selected output contract to render them and do not create parallel YAML assets.

| Asset | Use when | Required verified facts |
|---|---|---|
| `assets/components/etb.xml` | ETB is the trace sink | ETB base address and AP |
| `assets/components/etf.xml` | ETF is a FIFO or circular-buffer sink | ETF base address and AP |
| `assets/components/etr.xml` | ETR is the trace-buffer sink | ETR base address, AP, buffer address/size, and AXI controls |
| `assets/components/catu.xml` | CATU is present on an ETR trace-buffer route | CATU base address, AP, mode, translation addresses, AXI control, and interrupt setting |
| `assets/components/tpiu.xml` | SWO is emitted by a TPIU, or synchronous TPIU output is used | TPIU base address, AP, and output mode |
| `assets/components/swo.xml` | a separately documented SWO component with its own base address is used | SWO base address, AP, clocks |
| `assets/components/funnel.xml` | a trace funnel is on the selected path | base address, AP, input mask |
| `assets/components/replicator.xml` | a replicator is on the selected path | base address, AP, output filters |

Select `etr.xml` and `catu.xml` independently. Omit `catu.xml` unless the verified route implements CATU.
