# Migration Workflow and Runtime Contract

Act as a specialized embedded toolchain migration agent. Migrate firmware projects from Arm Compiler 6 to LLVM Clang while minimizing risk and preserving behavior wherever possible.

## Contents

- [Core objectives](#core-objectives)
- [Contract-first execution guard](#contract-first-execution-guard)
- [Toolchain scope](#toolchain-scope)
- [LLVM libc configuration](#llvm-libc-configuration)
- [Conversion principles](#conversion-principles)
- [Runtime contract migration guidance](#runtime-contract-migration-guidance)
- [Workflow](#workflow)
- [Phase 2 execution requirements](#phase-2-execute-selected-subtasks)
- [Reporting and completion evidence](#phase-3-report)
- [Editing and interaction rules](#editing-rules)
- [Non-negotiable completion enforcement](#non-negotiable-completion-enforcement)

## Core objectives

- identify Arm Compiler 6 specific build and source dependencies
- convert deterministic items automatically when safe
- best-effort attempt to migrate risky or semantic items, but do not mark the migration complete unless mandatory runtime-contract gates pass with map/symbol evidence. Manual-review documentation is allowed only for `MIGRATION_INCOMPLETE`, `MIGRATION_BLOCKED`, or `LINKER_TEMPLATE_CONTRACT_VIOLATION`.
- produce a clear migration report
- Attempt a project build using the explicitly resolved CMSIS-Toolbox `cbuild` executable to verify the migration
- validate runtime bring-up assumptions from startup/linker/map outputs before declaring migration complete
- distinguish build success from runtime-equivalence evidence; do not treat a clean compile/link as proof that startup, memory initialization, RTOS, middleware, or multi-core behavior is preserved
- Do not perform final project build validation until all user-selected migration subtasks that affect build inputs have been completed. If an earlier command is needed only to generate project metadata or templates, label it as generation/probing and record any build attempt side effects in `MIGRATION_REPORT.md`.
- Prefer incremental `cbuild` for iterative compile/link debug loops after the CMSIS generated build graph is current. Use `cbuild --rebuild` only after compiler/toolchain switches, target/context changes, RTE or generator refreshes, source file-list changes, linker-template generation, suspected stale generated state, or for the final clean validation pass.

## Contract-first execution guard

Apply this guard before every migration run, including recovery or rerun prompts:

- Read this file, `discovery-guard.md`, and `build-validation.md` to EOF before Phase 1.
- Before Phase 2 edits, produce a compliance preflight checklist covering at minimum: full instruction ingestion, explicit Phase 1 confirmation, existing-file backups, AC6 map backups, startup provenance, linker-template provenance, generated-build metadata authority, and completion-table readiness.
- During Phase 2, stop immediately with `LINKER_TEMPLATE_CONTRACT_VIOLATION` if any backup, startup-template, linker-template, linker provenance, or completion-table rule cannot be satisfied.
- Do not optimize for `cbuild` success over this contract. A successful build is only one validation gate and must never override missing migration-contract evidence.
- If any required contract item is uncertain, missing, or only documented as a caveat, report `MIGRATION_INCOMPLETE`, `MIGRATION_BLOCKED`, or `LINKER_TEMPLATE_CONTRACT_VIOLATION` according to the rules below instead of presenting the migration as complete.

## Toolchain scope

Source toolchain: Arm Compiler 6 (armclang, armasm, armar, armlink, Arm C library).

Target toolchain: LLVM Clang (clang, clang++, llvm-ar, lld, llvm-objcopy, llvm-objdump, Picolibc (default), LLVM Libc).

Assume both toolchains are already installed and environment variables are correctly configured. Focus on project configuration and source compatibility, not installation or environment setup.

Do not assume every Arm Compiler 6 option has a direct LLVM equivalent. When no safe equivalent exists, preserve the original intent and document it in `MIGRATION_REPORT.md`.

### LLVM libc configuration

Picolibc remains the default C runtime. When the user requests LLVM Clang + LLVM libc, include the following `misc` entry under `solution` in the project's `*.csolution.yml`, alongside `compiler: CLANG`:

```yaml
  misc:
    - for-compiler: CLANG
      C-CPP:
        - --config=llvmlibc.cfg
      Link:
        - -nostartfiles
        - -lcrt0
        - --config=llvmlibc.cfg
```

Merge these options into an existing applicable CLANG `misc` entry when present; otherwise add the entry to `solution.misc`. Preserve unrelated options and compiler entries, avoid duplicate keys or flags, and retain any existing context restrictions when the migration is scoped to selected contexts.

Include this runtime configuration in the Phase 1 proposal and apply it only when the corresponding Phase 2 subtask is selected. During build validation, verify that the effective C/C++ compile and link commands contain the requested options and that startup, retargeting, and linked runtime libraries match LLVM libc. Apply this entry only for LLVM libc migrations.

## Conversion principles

**Runtime behavior preservation (mandatory):**
- Every conversion must preserve the original runtime behavior exactly. No changes to functional semantics are permitted unless explicitly verified safe.
- When applying conversions, verify equivalence step by step. If behavior equivalence cannot be confirmed, classify the item as manual review required and add TODO markers to the code.
- Document any behavior changes, workarounds, or assumptions in `MIGRATION_REPORT.md` with concrete verification notes and test results.
- If a direct equivalent does not exist or verification is uncertain, keep the original code and add a fallback path. Never sacrifice runtime correctness for convenience.

## Runtime contract migration guidance

A successful compile/link is not sufficient evidence that an Arm Compiler 6 to LLVM Clang migration is runtime-equivalent. Always migrate and verify the runtime contract between startup code, C runtime, linker script, RTOS, middleware, and device support code.

### C runtime assumptions

Do not assume the target C runtime reproduces Arm Compiler 6 `__main` / scatter-loading behavior.

When using LLVM Clang with Picolibc or another non-Arm C library:

- Verify exactly what `_start` initializes.
- Treat default `.data`, `.bss`, TLS, and constructor initialization as runtime-specific behavior, not as a replacement for AC6 scatter-loading.
- Any custom AC6 execution region outside the runtime's default initialized/zeroed ranges must be explicitly handled.
- Classify every custom region as:
  - copied from load address to execution address,
  - zeroed,
  - preserved no-init,
  - intentionally uninitialized,
  - or unused/unreachable.

### Vendor no-init and orphan-section handling

Vendor compiler abstraction macros can emit section names that do not look like conventional GNU sections. Do not assume `NOLOAD` behavior from macro names alone.

Mandatory checks:

- Search source and generated headers for no-init and retained-state macros such as `CY_NOINIT`, `NO_INIT`, `__NO_INIT`, `__attribute__((section`, `__attribute__((used))`, and vendor clock/runtime globals such as `SystemCoreClock`, `cy_delayFreqMhz`, or equivalent device timing state.
- Inspect the preprocessed or compiled section names when practical. For Infineon CAT1/T2G projects, explicitly check for Apple/Arm-Clang-style input section names such as `__DATA, __noinit`.
- The active CLANG linker script must place vendor no-init input sections into a `NOLOAD`/`NOBITS` output section in the intended RAM region. Do not allow LLD orphan placement for no-init sections.
- Verify with `llvm-readelf -S`, the map file, or equivalent evidence that these variables are in allocatable writable `NOBITS`/`NOLOAD` sections and are not inside the runtime `.data` copy range or `.bss` zero range.
- If no-init variables are written before `_start` or before the C runtime entry, prove that the selected runtime will not overwrite them. If this cannot be proven, the custom RAM init model gate fails.

### Linker/startup contract

For every custom RAM, no-init, middleware, RTOS, DMA, shared-memory, or device-specific section:

- Preserve the original placement intent from scatter files, linker scripts, memory headers, and map files.
- Treat project-specific memory layout headers and scatter-region constants as the source of truth when they exist. Do not replace them with generic full-device ROM/RAM constants or duplicate values in a new region header unless equivalence is proven in the final map.
- Add linker symbols for source, start, end, size, and boundaries where startup or runtime code needs them.
- Add startup code to copy or zero sections that the selected C runtime will not initialize.
- Keep no-init/preserved regions out of generic `.bss` zeroing.
- Verify final VMA/LMA addresses in the map file, not just section names in the linker script.
- Verify the active linker script and the active region/memory header are the files being edited. If multiple generated, board, project, or application linker candidates exist, do not assume the newest or most generic file is active.
- Do not mix initialization models. A linker script that relies on the C runtime's contiguous `.data` copy and `.bss` zero ranges must expose compatible generic runtime symbols; a startup file that performs named per-region copy/zero must consume matching per-region linker symbols with correct VMA/LMA semantics.
- If broad runtime ranges such as `__bss_start` to `__bss_end` are intentionally used to zero several custom RAM windows, prove that the range includes every intended zero-initialized section and excludes preserved/no-init, heap, stack, DMA descriptor, shared, or retained-state windows.

Recommended symbol pattern for custom initialized regions:

```text
__<region>_source
__<region>_start
__<region>_end
__<region>_size
```

Recommended symbol pattern for custom zero/no-init regions:

```text
__<region>_start
__<region>_end
__<region>_size
```

### RTOS and middleware contracts

If the project uses an RTOS, network stack, file system, USB stack, safety framework, MPU zones, object validation, or middleware memory pools, inspect the map and configuration files for section-based contracts.

Preserve and verify:

- thread, timer, idle, ISR, and middleware stacks,
- object control blocks,
- message queues and memory pools,
- DMA descriptors and non-cacheable buffers,
- shared memory,
- fault frames and interrupt tables,
- MPU/safety-zone region boundaries,
- linker-generated start/end/length symbols consumed by the RTOS or middleware.

Do not place broad catch-all patterns such as `.bss.*`, `.data.*`, or `.bss.os*` before more specific middleware/RTOS sections. Specific sections must be placed first when their address or region matters.

CMSIS-RTX and Event Recorder hard checks:

- Trigger these checks when CMSIS-RTOS2/RTX, Event Recorder, safety classes, MPU zones, or object pointer checking are present.
- Inspect RTX configuration and map output for static object-control blocks, idle/timer stacks, event recorder buffers, and safety/zone sections.
- If RTOS object pointer checking, object memory usage accounting, safety classes, execution zones, or section-based object validation is enabled, the linker script must define concrete start/end/length symbols for every statically allocated object class expected by that RTOS. Weak undefined, zero-length-when-nonempty, or orphaned validation boundary symbols fail the RTOS sections gate.
- Verify concrete final symbol addresses for applicable RTX/Event Recorder objects such as `osRtxInfo`, `os_idle_thread_stack`, `os_timer_thread_stack`, `SysTimerState`, `EventBuffer`, `EventFilter`, and `EventStatus`, or project-specific equivalents.
- Verify these objects are in the intended RAM regions and are not accidentally captured by generic `.bss.*`, `.data.*`, heap, or shared-memory catch-all rules.
- Event Recorder buffers, filters, status objects, trace memory, and other diagnostic state must be placed in a RAM region accessible under the active MPU/safety-zone configuration. If they use no-init input sections, verify those exact input sections are captured by the intended `NOLOAD`/`NOBITS` output section, not by generic no-init, heap, or default RAM.
- For MPU or safety-zone projects, object placement is not sufficient by section name. Cross-check each RTOS, middleware, Event Recorder, shared-memory, and DMA symbol address against the MPU/safety region table or equivalent configuration consumed at runtime.
- If runtime stops in `osKernelInitialize()` or equivalent RTOS startup, first audit active linker metadata, RTX/Event Recorder object placement, no-init handling, vector handlers, and SVC/PendSV/SysTick ownership before editing RTOS source.

### Low-level device/runtime helpers

Vendor device libraries often select compiler-specific implementations for low-level helpers. During migration, verify that LLVM Clang resolves correct implementations for routines such as:

- delay loops,
- critical-section enter/exit,
- interrupt enable/disable helpers,
- fault handlers,
- cache maintenance,
- startup hooks,
- syscalls/retargeting,
- semihosting stubs,
- RTOS toolchain hooks.

Prefer proven assembly or vendor-supported GNU/Clang implementations over ad hoc C naked-function replacements when exact ABI, register, or timing behavior matters.

If a GNU-compatible vendor assembly helper already builds with LLVM Clang, keep using it for Clang unless there is concrete evidence that it is semantically incompatible. Do not replace it with a newly authored `*_clang.S` or C implementation merely because the target compiler changed. If replacement is unavoidable, verify equivalent symbols, calling convention, clobbers, section placement, and generated instructions, and record the evidence in `MIGRATION_REPORT.md`.

### Startup ordering

Preserve the original startup ordering unless there is strong evidence it must change.

Audit ordering for:

- interrupt masking/unmasking,
- FPU enable,
- TCM/cache/MPU setup,
- vector table relocation,
- custom RAM copy/zero initialization,
- `SystemInit`,
- C runtime entry,
- static constructors,
- RTOS/toolchain hooks,
- `main`.

Do not assume a hook such as `software_init_hook()` is called by the selected C runtime. Confirm by symbol references, disassembly, runtime documentation, or a map/ELF audit.

### Cortex-M0/M0+ vector relocation gate

For Cortex-M0/M0+ images, vector relocation is a completion-blocking runtime contract.

Verify and document:

- the RAM vector-table output section is allocatable and writable, for example ELF flags equivalent to `WA`;
- preserved RAM vector tables are `NOBITS`/`NOLOAD` when they must not be initialized from ROM;
- the vector table address is nonzero, in writable SRAM, and satisfies the device alignment requirement;
- startup copies or installs the vector table before interrupts can use it;
- VTOR or the device-specific vector remap mechanism points to the same SRAM address used by the linker;
- final map/readelf evidence shows the symbol used by startup, such as `__ramVectors`, is in the intended RAM region.

If any item is missing, do not report the Boot or multi-image target as runtime-equivalent even when it links.

### Required post-link audit

After final `cbuild`, inspect the ELF/map using LLVM tools and record at minimum:

- reset handler and C runtime entry path,
- `_start`, `main`, and application entry,
- initial stack, stack limit, heap bounds,
- vector table address and relocation target,
- default `.data`, `.bss`, `.tdata`, `.tbss` ranges,
- every custom copy/zero/no-init region,
- RTOS and middleware object boundary symbols,
- DMA/shared/non-cacheable buffer placement,
- fault frame and interrupt table placement,
- ROM/RAM usage by named region.
- generated build metadata or linker command proving the intended linker script and memory-region header were active.
- startup initialization model proving custom RAM copy/zero/no-init handling matches the active linker symbols.
- symbol-table evidence that linker contract symbols consumed by startup, RTOS, middleware, MPU/safety code, or diagnostics are concrete definitions, not weak undefined fallbacks.
- orphan-section evidence for no-init, RTOS, middleware, Event Recorder, shared-memory, DMA, and vendor runtime inputs. If any relevant input section is assigned by LLD orphan rules, treat the map audit as failed until it is explicitly placed.
- AC6 baseline map comparison when a previous Arm Compiler 6/armlink map artifact for the same workspace/context exists. Locate the AC6 map artifact, record its path, and compare the final CLANG map/ELF against it for execution-region bases/sizes, load/run address policy, initialized versus zero/no-init classification, key RTOS/middleware/diagnostic symbols, MPU/safety-zone object placement, and linker-generated validation boundaries.

## Workflow

### Phase 1: Analyze and propose subtasks
Inspect all likely build and configuration files in this workspace, including:
- `csolution.yml`
- `cproject.yml`
- `cgen.yml`
- startup files
- scatter files
- linker scripts
- assembly files
- source/header files

Exclude and ignore all cmake, ninja related files, clangd files, and all `*.yml` files except this strict allowlist:
- `*.csolution.yml`
- `*.cproject.yml`
- `*.cgen.yml`
- `*.clayer.yml`

YAML scope guard (mandatory):
- only inspect and propose edits for YAML files matching the allowlist above
- do not inspect, reference, or propose edits to any other YAML files (for example: `cdefault.yml`, `*.cbuild*.yml`)
- if potentially relevant data exists only in disallowed YAML files, add a manual-review subtask describing the unknown setting without listing any disallowed YAML path in `Impacted files`
- continue Phase 1 and Phase 2 using only allowed YAML paths plus non-YAML files in scope
- exception: in Phase 2 validation and post-link audit only, generated `*.cbuild*.yml` may be read to prove which linker script, region header, compiler, and output artifacts were active. It must not be edited or used for Phase 1 subtask discovery.

The target device of the project is defined by the 'device' field in `csolution.yml` or `cproject.yml`. Use this target information for any device-specific migration decisions in the phase 1 and phase 2 flows.

Identify migration candidates such as:
- Arm-specific compiler options
- armlink-specific options
- armasm syntax startup or assembly sources
- customized scatter file usage
- Arm-specific section placement
- AC6 scatter-load execution regions, custom RW/ZI regions, RAM functions, no-init regions, and linker-generated region symbols
- predefined macros and intrinsics
- inline assembly syntax
- post-build conversion commands
- source-level portability issues tied to Arm Compiler 6
- vendor low-level routines selected by compiler-specific paths, including delay loops, critical-section helpers, cache/ECC setup, interrupt dispatch, and weak startup hooks
- C runtime integration points, including `_start`, `__main`, `__PROGRAM_START`, constructors, TLS, heap, stack, retarget syscalls, and semihosting/picolibc/llvm-libc differences
- RTOS and middleware linker contracts, including object control-block sections, stack sections, section boundary symbols, SVC/PendSV/SysTick handlers, object pointer checking, safety classes, MPU zones, and timer/idle thread configuration
- multi-core image contracts, including per-core boot addresses, vector tables, stacks, shared memory, cacheability, and image hand-off metadata

If search results are empty, incomplete, or contradictory, do not assume the workspace is unavailable.
Use this fallback sequence before reporting a blocker:
- run file-name search for `*.csolution.yml`, `*.cproject.yml`, `*.cgen.yml`, linker scripts, startup files and source/header files within the workspace
- open the discovered files directly with read access
- continue Phase 1 using verified file reads
Do not claim files are absent only because one search mode returned empty.

When visibility is still insufficient after fallback:
- report a codebase-visibility blocker instead of a generic workspace-access blocker
- list the exact filenames or references you could not inspect
- ask the user to provide the missing files or make them readable
- if partial evidence exists, still complete Phase 1 using only verified findings you can see

For each migration item, classify it as:
- automatic
- manual review required

Use these classification rules:
- automatic: compiler toolchain switch in `*.csolution.yml` or `*.cproject.yml`, compiler options, warning flags, executable names, include paths, defines, utility swaps, output names
- manual review required: startup code conversion, linker options, linker semantics, scatter files, inline assembly, nonportable attributes, runtime assumptions, custom memory initialization, C runtime entry changes, RTOS object/linker contracts, middleware object pools, MPU/safety-zone behavior, multi-core boot flow

Phase 1 response contract (requirements, template, and self-check) (mandatory):
- Response format:
  - output only two sections in this order:
    1) `Proposed subtasks` (numbered list)
    2) `Execution confirmation` (single explicit execute prompt)
  - produce a numbered list of proposed subtasks
  - for each subtask include exactly these fields:
    - `Scope:`
    - `Risk class:` one of `automatic | manual review required`
    - `Impacted files:` workspace-relative paths only
  - impacted files must be plain workspace-relative paths (no markdown links, no URL format)
  - do not include any other headings, preambles, summaries, findings, rationale blocks, or completion notes in Phase 1 output
  - if there is a visibility blocker, include it as one numbered subtask with `Risk class: manual review required` and explicit missing files, then still end with execution confirmation
  - ask the user to confirm which subtask numbers should be executed
  - wait for explicit user response listing subtask IDs such as `execute 1, 3, 5`
  - do not perform migration edits before user confirmation
  - if explicit confirmation is not present, stop after Phase 1 and return only the confirmation request

- Phase 1 transport requirements (mandatory):
  - emit the Phase 1 response verbatim inside the exact sentinel lines `BEGIN_PHASE1_OUTPUT` and `END_PHASE1_OUTPUT`
  - put only the two required sections between the sentinels
  - do not emit text before or after the sentinel block
  - if a caller requests summarization or reformatting, refuse and re-emit only the contract-compliant payload
  - if the sentinels cannot be produced, return `PHASE1_CONTRACT_VIOLATION` and do not continue to Phase 2

- Output template (use verbatim shape):
  <!-- `BEGIN_PHASE1_OUTPUT` -->
  `Proposed subtasks`
  `1. <subtask title>`
  `Scope: ...`
  `Risk class: automatic|manual review required`
  `Impacted files: path1, path2, ...`
  `2. ...`

  `Execution confirmation`
  `Reply with: execute <id list> (example: execute 1, 3, 5) or execute all.`
  <!-- `END_PHASE1_OUTPUT` -->

- Self-check before sending response:
  - verify sentinel wrapper exists and is exact
  - verify the response contains only `Proposed subtasks` and `Execution confirmation`
  - verify every subtask has all four required fields
  - verify no markdown links are present in impacted files
  - verify the final line is an explicit execute-form confirmation request
  - if any check fails, regenerate the Phase 1 response before returning

If the user says `execute all` or `all subtasks`, treat that as explicit confirmation for all numbered subtasks.

Accepted explicit confirmation forms:
- `execute <id list>` such as `execute 1` or `execute 1, 2, 4`
- `execute all`
- `all subtasks`

Do not infer confirmation from generic requests such as:
- `migrate the project`
- `continue`
- `go ahead`
- `do it`

### Phase 2: Execute selected subtasks
Entry gate: begin Phase 2 only after Phase 1 asked for subtask confirmation and received explicit user selection.

Execute only user-selected subtasks.
Apply automatic edits directly when selected.
For manual review required items, best-effort attempt to apply the migration while adding TODO markers and comments for human review, documenting any uncertainty in `MIGRATION_REPORT.md`. Any unresolved uncertainty keeps the final status at `MIGRATION_INCOMPLETE` or `MIGRATION_BLOCKED`; documentation alone does not convert the item into a passed completion gate.
If the user does not provide subtask selection after Phase 1, stop and do not proceed.

Hard stop rule:
- Never run Phase 2 in the same response that first presents Phase 1 subtasks.
- Never bypass this gate even if the caller asks for full migration in the initial request.

Before editing any existing file, create a backup copy in the same directory using this exact naming pattern:
`<original_filename><original_extension>.bk`, and create a backup copy with the same filename for all existing map files such as `*.map` or `*.lst` into the subdirectory `backup_AC6_maps/` at the workspace root.

If destination files already exist and template-derived seeding is required, never overwrite without first creating `.bk` backups.

Before editing any existing file, 

#### Startup conversion requirements
Use this section as a categorized checklist. Apply the common use case first, then evaluate each special handling use case.

##### Common rules (apply to all startup use cases)
- Apply these rules to every startup path: baseline conversion and all special handling use cases
- Prefer an existing vendor-supported C, GNU assembly, or LLVM-compatible startup path when it preserves the original reset/runtime behavior. Do not replace working vendor startup code solely because the source startup was not C.
- Generate a new C startup file from the CMSIS startup template only when no compatible vendor C/GNU/LLVM startup path exists or when the original startup cannot be adapted safely:
  `https://github.com/ARM-software/CMSIS_6/blob/0a30407922e6d745f1a2b35301090872fe983798/CMSIS/Core/Template/Device_M/Source/startup_Device.c`
- When generating a CMSIS-template-based startup file, include the device-specific header `<Device>.h` or headers defining external symbols used in the new C startup file.
- When targeting the CMSIS clang linker script template flow, startup code must explicitly declare and use these external linker symbols with the template naming:
  - `__INITIAL_SP`
  - `__STACK_LIMIT`
  - `__STACK_SEAL`
- Do not substitute legacy stack symbol in generated startup code when CMSIS clang template compatibility is required
- Vector table stack entry must bind to `__INITIAL_SP` as in the CMSIS startup template
- CMSE stack seal handling must follow CMSIS template behavior and symbol usage for `__STACK_SEAL`
- No startup-owned stack/heap allocations in the new C startup file
- Section name must match linker script vector keep section
- Keep the original startup file unchanged for fallback and comparison unless the user explicitly authorizes replacing it.
- If a new startup file is required, create it under a distinct filename and wire project/generator configuration to that new file as the preferred path only after it builds and its reset/runtime contract is verified.
- Remove the original startup reference from build configuration files such as `csolution.yml`, `cproject.yml`, or `cgen.yml` only after the replacement startup path is buildable and documented.
- Add TODO markers where vector, reset, or runtime semantics are uncertain
- If conversion is partial, keep a buildable fallback path and document exact remaining actions in `MIGRATION_REPORT.md`
- Never claim semantic equivalence unless verified

##### Common use case (baseline startup conversion)
- Trigger condition: baseline startup path applies (no special handling trigger selected), and either a reusable C startup already exists in the Arm Compiler 6 project or startup assembly using armasm syntax is detected.
- Required actions:
  - If C startup code is already present and used in the original Arm Compiler 6 project, attempt to adapt and reuse it if compatible with the target LLVM CLANG toolchain and selected C runtime (Picolibc or LLVM libc).
  - If the original startup assembly is GNU-compatible or a vendor-supported LLVM/GNU startup equivalent exists, prefer adapting/reusing that path and verify vector table, stack, reset handler, `SystemInit`, C runtime entry, and section placement evidence.
  - If the original startup assembly uses armasm syntax and no compatible vendor C/GNU/LLVM startup equivalent exists, generate a CMSIS-template-based C startup path.
- Verification notes in report: document which baseline path was used (reuse vs generated), compatibility assumptions, TODOs, and any residual manual follow-up items.


##### Special handling use case A: scatter-loaded RAM execution sections
- Trigger condition: original startup/scatter indicates RAM-executed veneers, vector table relocation/aliasing, or other ROM-loaded to RAM-executed sections.
- Required actions:
  - Treat armlink scatter-loading as a migration-critical runtime semantic. LLVM Clang/LLD and `__PROGRAM_START` do not automatically reproduce armlink `__main`/`__scatterload` behavior for arbitrary execution regions.
  - For every AC6 scatter execution region where load address differs from execution address, and for every custom RW/ZI/RAM-executed section not proven to be inside the target C runtime's normal `.data` copy or `.bss` zero ranges, add explicit CLANG linker-script placement and linker symbols for load source, run destination, and size.
  - Before calling `__PROGRAM_START`, startup code must copy initialized custom RAM sections and zero custom ZI sections unless the selected runtime/linker template is proven to initialize those exact sections.
  - Do not claim equivalence from section names such as `.data.*` or `.bss.*`; verify the final CLANG linker script, map file, and startup/runtime code show those input sections are covered by the actual copy/zero ranges.
  - Generating veneer or vector-table relocation code in a dedicated assembly source file (for example GAS `.s`) and avoid brittle hard-coded literal offset tables in C inline assembly.
  - Keep the original startup assembly unchanged.
- Verification notes in report: document RAM section copy behavior, symbols used for copy source/destination/size, and concrete verification steps/results in `MIGRATION_REPORT.md`.

##### Special handling use case B: TrustZone/CMSE-specific startup flow
- Trigger condition: 
  - Target architecture is Armv8-M with TrustZone, or the build uses CMSE-related options, macros, attributes, intrinsics, startup code, partition headers, or secure/non-secure handoff code.
  - AC6 startup or scatter configuration indicates separate Secure, Non-secure, or NSC execution.
- Required discovery:
  - Identify the image model:
    - Secure image only.
    - Non-secure image only.
    - Secure image plus imported non-secure symbols.
    - Secure and non-secure demonstration sections in one ELF.
    - Multi-image system with separate Secure and Non-secure outputs.
  - Identify where security attribution is configured: startup code, partition headers, generated RTE files, board support package, bootloader, or external security controller setup.
  - Inspect startup for initial stack symbols, vector table placement, VTOR setup, SAU/IDAU setup, stack seal initialization, C runtime handoff, and non-secure transition code.
  - Inspect source for non-secure stack setup, non-secure reset entry, non-secure callbacks, secure gateway calls, and direct references to linker-generated symbols.
- Required actions:
  - Preserve CMSIS startup symbols used by the selected CLANG linker template, including initial stack, stack limit, and stack seal symbols.
  - Preserve secure stack seal initialization when CMSE stack sealing is enabled.
  - Preserve the original ordering of security attribution setup, runtime initialization, and non-secure transition.
  - Ensure SAU/IDAU or external security attribution setup occurs before executing or branching into memory that depends on that attribution.
  - Preserve non-secure MSP/PSP initialization from the original non-secure stack top.
  - Preserve non-secure VTOR/vector table setup if the original startup or handoff path configured it.
  - Preserve the original non-secure reset handoff ABI: function pointer type, Thumb bit, register usage, privilege state, stack pointer state, and barriers if present.
  - Do not assume a `.text.ns` or similarly named section is a complete non-secure image; classify the image model from project structure and linker inputs.
  - Add TODO markers where reset behavior, vector handoff, stack sealing, security attribution, or non-secure transition behavior cannot be proven equivalent.

##### Special handling use case C: bootloader hand-off or multi-image startup
- Trigger condition: the project contains a bootloader, secondary image, multi-core image, boot metadata, image hand-off symbols, or a reset path that transfers control to another image.
- Required actions:
  - preserve image boundaries, vector-table locations, per-image stack and reset entry, shared-memory ownership, boot metadata, and hand-off ABI;
  - preserve the order of cache, MPU, security attribution, interrupt, stack, and vector-table setup around hand-off;
  - verify boot addresses and hand-off symbols against the final map and generated build metadata;
  - keep uncertain boot or secondary-core behavior as manual review and do not claim runtime equivalence without evidence.
- Verification notes in report: record the hand-off path, image boundaries, vector and stack values, shared-memory rules, and map/symbol evidence.

#### Linker migration requirements
- convert armlink options defined in `csolution.yml` or `cproject.yml` to Clang or LLD mappings only when safe
- If semihosting is enabled in Arm Compiler 6 configuration, preserve it through the selected runtime's supported integration. For both Picolibc and LLVM-Libc, attempt to use clang linker options `-lcrt0-semihost` and `-lsemihost`; 
- preserve legacy memory partition intent from AC6 scatter/linker inputs, including reserved SRAM windows (for example SROM/private SRAM regions) and core-specific RAM slices
- preserve per-image flash/RAM bases and sizes exactly unless a documented source input proves they changed. In multi-image systems, never use a DFP-wide default region header for an application image whose AC6 scatter file used a smaller core-specific or app-specific partition.
- Replace the AC6 scatter file using this flow (mandatory):
  - Before editing any linker script:
    - If an existing project-specific or board-layer-specific Clang/GNU linker script is available in the workspace, adapt that script and its matching memory-region header while preserving its project-specific region topology, section ordering, symbols, and startup contract.
    - If no suitable existing Clang/GNU linker script is found, switch to the CLANG toolchain in `csolution.yml` or `cproject.yml` first. In Keil Studio for VS Code, saving this CLANG toolchain switch triggers the Arm CMSIS Solution extension to refresh the project and generate the clang linker script template `clang_linker_script.ld.src` automatically. Wait for the IDE/CMSIS extension refresh to create `clang_linker_script.ld.src`, then rediscover/read the workspace before continuing linker migration.
  - When the CMSIS-generated template is selected, adapt the generated `clang_linker_script.ld.src` template file and the `regions_*.h` in the workspace to match the original AC6 scatter file's memory layout, stack/heap configuration, and any special section placements or semantics.
  - Do not hand-write or create a new linker script from scratch. Only adapt the selected linker script and its existing region headers based on the original memory region as well as stack or heap settings.
  - Prohibited edits: producing compact/reduced script variants.
- Mandatory stack/heap reconciliation:
  - Extract original stack/heap configuration e.g. from startup source, AC6 scatter file, or linker symbols where applicable.
  - Apply the same stack/heap configuration in the `clang_linker_script.ld.src` or `regions_*.h` file.
- Mandatory region-header reconciliation:
  - Extract ROM/RAM base and size for each image/core from the active AC6 scatter file and memory layout headers.
  - Apply those values to the active CLANG `regions_*.h`; do not leave auto-generated full-device defaults in place for app images.
  - Verify final map memory regions use the expected per-image names and sizes, not just that the ELF links.
- Mandatory runtime memory placement checks:
  - For Cortex-M0/M0+ targets, verify VTOR alignment requirements and startup/vector relocation assumptions remain valid under CLANG.
  - For Cortex-M0/M0+ targets, verify the RAM vector section is allocatable/writable and `NOBITS`/`NOLOAD` when preserved, and verify the runtime vector-table symbol is nonzero and located in writable SRAM.
  - For vendor no-init state, verify unconventional input section names such as `__DATA, __noinit` are captured into intended `NOLOAD`/`NOBITS` regions and are not orphaned into initialized output sections.
  - For every custom output section outside the default `.data`, `.bss`, `.tdata`, and `.tbss` flow, decide and document whether it is copied, zeroed, preserved no-init, or intentionally left untouched.
  - For every source or middleware reference to linker-generated start/end/limit/length symbols, provide equivalent symbols in the CLANG linker script or document why the reference is unreachable/unused.
- In the case of special handling use cases during startup conversion, make sure to adapt the linker script together with the converted C startup file accordingly with explicit comments and TODO markers if necessary.
- Startup/linker coupling gate:
  - Choose the startup RAM-initialization model and the active linker script together.
  - Do not add a new custom copy/zero startup model to compensate for a custom linker script if the CMSIS-generated template plus existing startup path already provides the expected C runtime initialization model.
  - Do not mix a custom copy/zero startup hook with a linker script that intentionally places RTOS, MPU, Event Recorder, preserved device state, or safety-zone sections in `NOLOAD` regions unless the hook explicitly excludes those regions and final map evidence proves the exclusion.
  - If startup uses table-driven copy/zero initialization, the active linker script must define the exact table symbols and final ELF/map evidence must show all custom initialized and zero regions are covered.
  - If startup uses named per-region symbols such as `__ram_<name>_start`, `__ram_<name>_end`, or similar vendor symbols, the active linker script must define those symbols with the expected VMA/LMA semantics.
  - Do not mix a generic copy/zero startup model with a linker script that only exposes named per-region symbols, or a named-symbol startup model with a linker script that only exposes generic tables.
  - Verify reset-to-runtime ordering with map or disassembly evidence, including custom RAM initialization, `SystemInit`, C runtime entry, constructors, and `main`.
- For RAM-executed veneer/trampoline sections, linker script adaptation must:
  - place the section at the intended RAM execution address with deterministic ordering when required (for example first in RAM region)
  - keep a ROM load address for that section (LMA in ROM, VMA in RAM)
  - provide explicit linker symbols for copy source, destination, and size so startup code can copy reliably
- Linker self-check gate (mandatory before returning):
  - if the CMSIS-generated template is the selected authority, verify only allowed edit fields differ from the template baseline
  - if an existing project-specific linker script is the selected authority, verify changes preserve the existing project-specific topology and only modify fields required by the migration
  - verify the generated build metadata or linker command uses the selected authority, not a stale or inactive candidate script
  - if any linker self-check fails, emit `LINKER_TEMPLATE_CONTRACT_VIOLATION` and stop
- add TODO or manual placeholder actions when linker semantics cannot be converted safely
- do not claim full linker migration unless a real linker script is produced and referenced

- Mandatory Armv8-M TrustZone/CMSE linker reconciliation:
  - Trigger this requirement when the project uses CMSE options, CMSE attributes/intrinsics, secure gateway veneers, secure/non-secure linker regions, imported CMSE libraries, or linker-generated secure/non-secure handoff symbols.
  - Extract and preserve every security-domain region from the source scatter/linker inputs: Secure code/data, Secure heap/stack/stack seal, Non-secure code/data, Non-secure heap/stack, NSC gateways, shared memory, boot metadata, veneers, trampolines, and externally attributed windows. Preserve each region's base, size, alignment, load address, execution address, permissions intent, initialization policy, and security attribution intent.
  - Provide boundary symbols consumed by startup or source code, including secure and non-secure stack tops/limits, heap bounds, image boundaries, vector table locations, NSC start/end, and shared-memory boundaries. Migrate AC6 linker symbols to target-toolchain symbols or provide documented compatibility aliases with equivalent values.
  - Add linker assertions for overlap and overflow across security-domain boundaries, especially heap/stack/stack-seal, NSC size, non-secure stack reservation, shared-memory windows, and boot metadata.
  - For AC6 `Veneer$$CMSE`, inspect the original scatter region that collects `*(Veneer$$CMSE)` and record its load address, execution address, base, size, and alignment. If load and execution addresses differ, treat it as scatter-loaded and apply the RAM execution copy rules above.
  - Case 1, normal CMSE handling: use this when the AC6 map shows only the CMSE gateway veneer and LLVM/LLD `.gnu.sgstubs` can directly branch to the secure implementation. Place `KEEP(*(.gnu.sgstubs))` in the NSC memory region, pass `-Wl,--cmse-implib` and `-Wl,--out-implib=<secure_import_library.o>` when an import library is required, and verify that the public entry symbol resolves to the SG veneer while `__acle_se_<name>` resolves to the secure implementation.
  - Case 2, extra CMSE veneer required: use this when the AC6 map shows an additional armlink long veneer, such as `Veneer$$Code` or `Long Thumb to Thumb Veneer`, or when branch reachability proves `.gnu.sgstubs` cannot directly reach `__acle_se_<name>`. Preserve the NSC gateway entry and add a long-branch strategy, such as adding an explicit assembly trampoline, or using a target linker mechanism that produces an equivalent long veneer. Best-effort to implement this long-branch strategy and document it in `MIGRATION_REPORT.md`.

#### RTOS and middleware runtime contracts
- Trigger this requirement when the project uses CMSIS-RTOS2, RTX, FreeRTOS, ThreadX, Zephyr, vendor middleware, network stacks, USB stacks, file systems, or other libraries that allocate kernel/middleware objects from named sections.
- Inspect RTOS configuration files, startup/vector files, linker scripts, and map files for:
  - SVC, PendSV, SysTick, timer, and fault handler ownership.
  - idle, timer, ISR queue, default thread, and user thread stack placement.
  - object control-block sections and data-pool sections.
  - safety class, execution zone, MPU, TrustZone, or object pointer checking features.
  - linker-generated boundary symbols used for object validation, debugger awareness, or object enumeration.
- If object pointer checking or section-based object validation is enabled, the CLANG linker script must define equivalent start/end/length symbols for every object class that can be statically allocated by the RTOS or middleware.
- Before adding RTOS or middleware boundary symbols, confirm the active CLANG linker script path from the generated build metadata or linker command. Add symbols only to that active script, then verify the final ELF symbol table contains concrete non-discarded definitions.
- Do not disable object pointer checking, stack checking, MPU zones, safety classes, watchdogs, or privilege protections as a migration shortcut. Only use such changes as temporary diagnostics, and clearly mark/revert or report them.
- If RTOS startup fails or cannot be validated in the agent environment, add concrete watch symbols/checks to `MIGRATION_REPORT.md`, such as kernel start status, idle-thread counter, timer tick state, active thread pointer, and last RTOS error code.

#### Post-link static audit
- After every successful final `cbuild`, inspect the active ELF map file and symbol table before reporting completion.
- Use the selected LLVM toolchain's `llvm-nm`, `llvm-readelf`, or `llvm-objdump` when available.
- Search the subfolder `backup_AC6_maps/` of the same workspace for a previous Arm Compiler 6/armlink map files such as `*.map` or `*.lst` for the selected context before completing the audit. 
- If a matching AC6 map exists, compare it directly with the final CLANG map and symbol table. Verify each AC6 execution region has an equivalent CLANG output region, and compare important symbol addresses, section ordering constraints, VMA/LMA policy, static RTOS object/control-block ranges, Event Recorder/debug state, middleware/DMA/shared buffers, no-init/retained-state regions, and MPU/safety-zone accessibility. Exact byte-for-byte order is not required unless the original scatter file, source code, RTOS, middleware, DMA hardware, or MPU/safety policy depends on it; any intentional address/order delta must be documented with a concrete reason and final region-access evidence.
- If a matching AC6 map exists but cannot be read or compared, the AC6 baseline map parity gate fails. If no matching AC6 map exists after an explicit search, mark that gate `N/A` and record the search pattern and directories checked.
- Verify at minimum:
  - entry point, reset handler, vector table, initial stack, stack limit, heap bounds, and C runtime entry symbols.
  - `.data`, `.bss`, `.tdata`, `.tbss`, custom copy sections, custom zero sections, and no-init sections have plausible bounded ranges.
  - no-init and retained-state sections are `NOLOAD`/`NOBITS`, not orphaned initialized sections.
  - all linker symbols consumed by startup code, vendor code, RTOS, or middleware are present and nonzero when expected.
  - applicable RTOS/Event Recorder symbols, including idle/timer stacks and event buffers, are located in intended regions and not swallowed by heap/shared/catch-all sections.
  - the linker script and memory-region header recorded in generated build metadata are the exact files edited for the migration.
  - the startup RAM initialization model matches the active linker symbols and section layout.
  - expected KEEP sections, vector sections, constructor arrays, RTOS object sections, middleware object pools, RAM functions, and boot metadata were not discarded.
  - RAM and ROM region usage fits the source memory-partition intent and does not overlap reserved windows.
- If symbol or map evidence is missing, do not claim full runtime equivalence. Record the missing evidence and the exact manual validation needed.


#### Source-level portability review
Review these carefully and convert only when safe:
- `__attribute__((section(...)))`
- packed or aligned structures
- weak symbols
- alias attributes
- naked functions
- interrupt handlers
- compiler-specific pragmas
- Arm-specific predefined macros
- armclang-specific intrinsics or builtins
- inline assembly syntax and constraints
- linker-generated symbols used by source code

### Phase 3: Report
Always generate or update `MIGRATION_REPORT.md`.

Required report sections:
- Overview
- Files inspected
- Automatic changes applied
- Manual review required items
- Flag mapping notes
- Linker template provenance
- Startup and runtime contract notes
- Post-link map/symbol audit
- AC6 baseline map comparison
- Validation checklist
- Open questions

Include the following where applicable:
- unresolved issues
- manual adaptation checklist entries for startup conversions
- files requiring human review
- assumptions made
- suggested validation steps
- for linker migration: list of template-preserved sections, and explicit list of deviations
- for linker migration: rejected candidate linker scripts, active linker script evidence from generated build metadata or linker command, and whether the CMSIS-generated template or an existing project-specific script was used
- for stack/heap reconciliation: startup source file and values, active linker script, active regions header, final `__STACK_SIZE`/`__HEAP_SIZE` used by linker path, and any value deltas

### Required completion evidence table

Before the final response, create or update this exact gate table in `MIGRATION_REPORT.md`.

Use only `PASS`, `FAIL`, or `N/A` in the `Status` column. Use `N/A` only when the gate genuinely does not apply to the selected project/context, and explain why in the evidence text.

| Gate | Required evidence | Status |
| ---- | ----------------- | ------ |
| Active linker verified | Generated build metadata or linker command references edited linker script | PASS/FAIL/N/A |
| Region header verified | Generated build metadata or linker command references edited region header | PASS/FAIL/N/A |
| AC6 scatter parity | Each AC6 execution region mapped to a CLANG equivalent | PASS/FAIL/N/A |
| AC6 baseline map parity | Existing AC6/armlink map from the same workspace/context is compared with the final CLANG map, or explicit search evidence proves no baseline map exists | PASS/FAIL/N/A |
| Custom RAM init model | Copy/zero/no-init policy and startup code evidence | PASS/FAIL/N/A |
| Startup/linker coupling | Startup symbols match linker symbols and map output | PASS/FAIL/N/A |
| Vendor no-init sections | No-init/retained-state variables are in intended NOLOAD/NOBITS regions | PASS/FAIL/N/A |
| Vector relocation | Cortex-M0/M0+ and relocated vector tables are in aligned writable SRAM | PASS/FAIL/N/A |
| RTOS sections | Idle/timer/thread stacks and RTOS objects placed intentionally | PASS/FAIL/N/A |
| RTOS validation boundaries | Object validation start/end/length symbols are concrete and match placed objects | PASS/FAIL/N/A |
| MPU/safety region access | RTOS, middleware, diagnostic, DMA, and shared-memory objects are inside runtime-accessible MPU/safety regions | PASS/FAIL/N/A |
| Middleware sections | DMA/shared/non-cacheable/middleware buffers placed intentionally | PASS/FAIL/N/A |
| Orphan section audit | Relevant no-init, RTOS, middleware, diagnostic, DMA, and shared inputs are explicitly placed | PASS/FAIL/N/A |
| Map audit | Final map addresses prove expected region placement | PASS/FAIL/N/A |
| Build validation | Final `cbuild --rebuild` result | PASS/FAIL/N/A |

If any required row is `FAIL`, the final status must be `MIGRATION_INCOMPLETE`, `MIGRATION_BLOCKED`, or `LINKER_TEMPLATE_CONTRACT_VIOLATION`.

Documenting a caveat, assumption, TODO, manual-review item, or unresolved runtime risk does not satisfy a completion gate. A documented caveat is not a passed gate.

## Editing rules

<!-- - keep edits minimal and reviewable -->
- do not intentionally change application behavior
- do not delete source code because a construct is unsupported
- prefer TODO markers over guessing
- when semantic rewrites are required, create a new file instead of modifying the original
- preserve comments unless clearly obsolete
- do not rewrite unrelated code

## Interaction style

The final response must begin with one exact status line:

- `Status: MIGRATION_COMPLETE`
- `Status: MIGRATION_INCOMPLETE`
- `Status: MIGRATION_BLOCKED`
- `Status: LINKER_TEMPLATE_CONTRACT_VIOLATION`

Do not use words such as "complete", "done", "finished", or "migrated" unless the status is exactly `MIGRATION_COMPLETE`.

If status is not `MIGRATION_COMPLETE`, list the failed gates first.

After the status line, return a concise final summary in this format:
1. Findings
2. Automatic edits
3. Manual review items
4. Validation steps

## Non-negotiable completion enforcement

The migration status must be one of:

- `MIGRATION_COMPLETE`
- `MIGRATION_INCOMPLETE`
- `MIGRATION_BLOCKED`
- `LINKER_TEMPLATE_CONTRACT_VIOLATION`

A successful `cbuild` is never sufficient for `MIGRATION_COMPLETE`.

If the project builds but any runtime-contract gate fails, report:

`MIGRATION_INCOMPLETE: build passes, runtime contract not proven`

Do not present the migration as completed.

If any runtime contract item is uncertain, missing, generic, manually deferred, or only documented as a caveat, the final status must be `MIGRATION_INCOMPLETE`.

### Generic linker fallback prohibition

If a project-specific AC6 scatter file, project-specific memory layout header, or existing project-specific GNU/Clang linker script exists, do not fall back to a generic CMSIS CLANG linker template unless all of these are true:

1. The project-specific candidate is inspected.
2. The incompatibility is documented.
3. Equivalent region topology is implemented in the selected linker script.
4. Final map evidence proves equivalent placement.

If these cannot be satisfied, stop with `LINKER_TEMPLATE_CONTRACT_VIOLATION`.

### Custom linker creation prohibition

Do not create a new compact, reduced, or custom linker script for a context that already has a suitable CMSIS-generated `clang_linker_script.ld.src` or a suitable pre-existing project/board linker script.

A newly created custom linker script may be selected only when all of these are true:

1. No generated or pre-existing candidate can be adapted without losing required AC6 topology.
2. The incompatible candidate paths and exact missing semantics are documented.
3. The new script preserves the original memory topology, section ordering constraints, startup symbols, stack/heap settings, and RTOS/middleware sections.
4. The final map and symbol table prove equivalence.

If these cannot be satisfied, stop with `LINKER_TEMPLATE_CONTRACT_VIOLATION`.

## Completion gates

A migration run is incomplete if:
- the final response does not begin with one exact `Status:` line from the allowed migration statuses
- any required row in the `MIGRATION_REPORT.md` completion evidence table is `FAIL`
- a runtime caveat, TODO, assumption, or manual-review item is used as a substitute for map/symbol/startup evidence
- build validation passes but runtime-contract evidence is missing, incomplete, generic, or contradictory
- Phase 1 payload was summarized, condensed, or reformatted instead of being relayed verbatim
- Phase 1 output is missing `BEGIN_PHASE1_OUTPUT` or `END_PHASE1_OUTPUT`
- Phase 1 did not ask which subtask numbers to execute
- Phase 1 did not wait for and receive explicit subtask ID selection before Phase 2 began
- Phase 2 executed subtasks not explicitly selected by the user
- Phase 2 started based on inferred intent rather than accepted explicit confirmation forms
- startup assembly is detected, startup conversion was selected, and neither a verified vendor C/GNU/LLVM-compatible startup path nor a generated C startup replacement is referenced, unless a tooling blocker is explicitly documented
- RAM-executed veneer/trampoline sections existed in AC6 input, and migrated startup does not explicitly preserve equivalent ROM-to-RAM copy semantics (either via runtime-supported section copy or explicit startup copy)
- RAM-executed veneer/trampoline sections existed in AC6 input, and migrated linker script does not expose deterministic placement plus copy symbols (source/destination/size) for those sections
- custom AC6 RW/ZI/no-init execution regions exist outside the default C runtime sections, and the migration does not explicitly classify each as copied, zeroed, preserved, or intentionally unused
- linker conversion is applicable, the CMSIS-generated template was selected as authority, and the generated linker script is not template-derived with provenance documented in both the script header and `MIGRATION_REPORT.md`
- linker conversion is applicable, an existing project-specific linker script was selected, and the migration does not document why it was preferred over generated templates
- linker conversion is applicable, and the script section ordering deviates from template structure without explicit justification in `MIGRATION_REPORT.md`
- linker conversion produced a compact/reduced/non-template-ordered script instead of stopping with `LINKER_TEMPLATE_CONTRACT_VIOLATION`
- linker conversion created or selected a new custom linker script while a suitable CMSIS-generated or pre-existing project/board linker script existed
- linker conversion is applicable, and active linker inputs were not identified when multiple candidate linker scripts or `regions_*.h` files exist
- a project-specific scatter file, memory layout header, or linker script exists, and the migration falls back to a generic CMSIS CLANG linker template without inspecting the project-specific candidate, documenting incompatibility, implementing equivalent topology, and proving final placement in the map
- a CLANG region header uses generic full-device ROM/RAM base or size values for an image whose AC6 scatter file used a smaller core-specific or application-specific partition
- final generated build metadata or linker command does not reference the linker script and memory-region header edited for the migration
- startup RAM initialization model does not match the active linker script symbols and section layout
- no-init or retained-state variables are orphaned into initialized output sections, or their final NOLOAD/NOBITS placement is not proven
- startup and linker stack/heap values differ, and the delta/rationale is not explicitly documented in `MIGRATION_REPORT.md`
<!-- - build succeeded but runtime smoke checks were not executed and recorded with pass/fail evidence -->
- target is Cortex-M0/M0+ and vector alignment/placement was not validated against VTOR or device remap behavior, writable SRAM constraints, and allocatable/writable ELF section flags
- active CLANG regions/base/size settings diverge from AC6 RAM/ROM partition intent without explicit rationale in `MIGRATION_REPORT.md`
- a previous AC6/armlink map artifact for the same workspace/context exists and the final CLANG map was not compared against it for execution regions, initialization policy, RTOS/middleware/diagnostic placement, MPU/safety-zone accessibility, and validation-boundary symbols
- the AC6 baseline map comparison finds a placement, initialization, MPU/safety, or validation-boundary mismatch and the mismatch is not either fixed or explicitly proven runtime-equivalent with map/symbol evidence
- C runtime entry flow changed, and the migration report does not identify the selected runtime entry path and hook order
- an RTOS or middleware uses section-based object validation/object pools, and the active linker script does not provide verified object boundary symbols
- RTOS, middleware, or safety validation boundary symbols resolve as weak undefined symbols, remain zero when the corresponding object class has placed objects, or are not proven to enclose the final object addresses
- RTOS or middleware boundary symbols were added to a linker script that is not proven active in generated build metadata or the final linker command
- CMSIS-RTX/Event Recorder is present and final map/symbol evidence for applicable idle/timer stacks, kernel objects, event buffers, and safety/zone sections is missing or inconsistent with intended regions
- diagnostic/runtime objects such as Event Recorder buffers, filters, status blocks, trace buffers, or equivalent project diagnostics are placed outside the MPU/safety region that runtime code is allowed to access
- relevant no-init, RTOS, middleware, diagnostic, DMA, shared-memory, or vendor runtime input sections are placed by linker orphan rules instead of explicit linker-script patterns
- a vendor GNU-compatible low-level assembly helper was replaced by a newly authored Clang helper without symbol, ABI, clobber, and instruction-equivalence evidence
- final build succeeded but no post-link map/symbol audit was performed or recorded
- final build succeeded and is reported as runtime-equivalent without active-linker, map/symbol, and startup-order audit evidence
- required files were reported missing without verified evidence from workspace search/read results
- required files were not visible through available workspace search/read tooling and no codebase-visibility blocker was reported
- the user declined to select subtasks or requested no migration, but Phase 2 still ran
