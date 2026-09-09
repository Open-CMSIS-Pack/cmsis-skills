---
name: cmsis-toolbox
description: This skill provides access to the CMSIS Toolbox, a collection of tools and libraries for Arm Cortex-M microcontrollers. It allows users to perform various tasks such as pack management, project generation, and build management using the CMSIS Toolbox command-line interface. It should be used when working with embedded applications that utilize CMSIS software packs and cmsis solution files.
---

# CMSIS Toolbox

## Requirements to use this skill
 * CMake 3.31.5 or higher
 * Ninja 1.12.0 or higher
 * CMSIS-Toolbox 2.0.0 or higher

## When to use this skill
 * When you need to install and manage CMSIS software packs in the host development environment.
 * When you need to orchestrate the build steps utilizing CMSIS tools and a CMake compilation process.
 * When you need to create build information for embedded applications that consist of one or more related projects.

## Standard workflow for using this skill
1. Check if a solution file is available for the project. If not, cancel the workflow.
2. Initialize the pack registry (if not already initialized).
3. Add the missing software packs to the registry.
4. Select a target type for the project if not already provided by the user
5. Build the solution using the `cbuild` command, specifying the solution file and the selected target type. Use the `--update-rte` and `--packs` options for the first build to ensure that all required packs are installed and the RTE is up-to-date. Only one configuration must be built : the one corresponding to the selected target set.
6. Set up the project for an IDE to enable features like code completion and debugging if working in an IDE environment.
7. Clean the build artifacts when necessary using the `cbuild --clean` command.

## Quick Reference

| Task | Command |
|------|----------|
| Initialize pack registry | `cpackget init https://www.keil.com/pack/index.pidx` |
| Update the pack registry | `cpackget update-index` |
| Build a solution | `cbuild <solution-name>.csolution.yml` |
| Add a new software pack to the registry | `cpackget add <pack-name>` |
| List pack required by the solution | `csolution list packs  <solution-name>.csolution.yml` |
| List devices | `csolution list devices` |
| List boards | `csolution list boards` |
| List solution dependencies | `csolution list dependencies <solution-name>.csolution.yml` |
| Setup the project for an IDE | `cbuild setup <solution-name>.csolution.yml --target database --active <target-set> --packs --skip-convert` |
| Clean the build artifacts | `cbuild --clean <solution-name>.csolution.yml` |


## How to initialize the pack registry if it was not initialized before

The first time CMSIS Toolbox is used, the pack registry needs to be initialized with the command below. This will download the pack index from the specified URL and populate the local pack registry with the available packs.

```bash
cpackget init https://www.keil.com/pack/index.pidx
```

## How to update the pack registry

To ensure that the local pack registry is up-to-date with the latest available packs, the following command can be used to update the pack index:

```bash
cpackget update-index
```

## How to register a toolchain for use by CMSIS Toolbox

Define an environment variable with following format: 
`<name>_TOOLCHAIN_<major>_<minor>_<patch>=<path/to/toolchain/binaries>`

Use the path to the directory containing the toolchain binaries (e.g., `armclang.exe` for Arm Compiler 6 on Windows). The version numbers should correspond to the toolchain version you are registering.

Example on windows: `set AC6_TOOLCHAIN_6_19_0=C:\Keil_v5\ARM\ARMCLANG\bin`

## How to build a project using CMSIS Toolbox

A solution file is used to build a project using CMSIS Toolbox. The solution file contains the build information for the project, including the toolchain, target, and build options.
Only one configuration should be built at a time, corresponding to the selected target set. 

* Build a solution using default settings : `cbuild <solution-name>.csolution.yml`
* Build a solution using a specific toolchain (AC6, GCC, CLANG) : `cbuild <solution-name>.csolution.yml --toolchain <toolchain>`
* Build a solution using a specific target `cbuild <solution-name>.csolution.yml --active <target-set>`


The solution file is generally in the root folder of the project and has a name in the format `<solution-name>.csolution.yml`. The solution file contains the build information for the project.

The `<target-set>` is the type entry of the target-types defined in the solution file. The solution file can contain multiple target-types, each with a different target name. The `--active` option is used to specify which target-type to build.

The first build should add the option `--update-rte` and `--packs`to ensure that all required packs are installed and the RTE is up-to-date. After the first build, the option can be omitted if there are no changes to the solution file or the pack registry.

`--update-rte` option will update the RTE (Run-Time Environment) files for the project. This is necessary when there are changes to the solution file or the pack registry that affect the RTE files.

`--packs` option will install any missing packs required by the solution. This is necessary when there are changes to the solution file or the pack registry that affect the required packs.

If used from an IDE context, the project should be set up for the IDE before building. This will ensure that the IDE has the necessary information about the project structure, dependencies, and build settings to provide features like code completion, error checking, and debugging.

## Setup the project for an IDE

In an IDE environment, this command downloads missing packs, creates build information files, and generates the file `compile_commands.json` for IntelliSense. 

```bash
cbuild setup <solution-name>.csolution.yml --target database --active <target-set> --packs --skip-convert
```

## How to add a new software pack to the registry
* Add a new software pack to the registry : `cpackget add <pack-name>`
* Add a new specific version of a software pack to the registry : `cpackget add <pack-name>@<version-number>`

Example: `cpackget add Arm::CMSIS@6.1.0`

## How to list installed software packs in the registry

List all installed software packs in the registry : `csolution list packs`

## How to list packs required by the solution

`csolution list packs  <solution-name>.csolution.yml`

## How to install missing packs required by the solution

```bash
csolution list packs <solution-name>.csolution.yml -m > packs.txt
cpackget update-index               # optional to ensure that pack index is up-to-date
cpackget add -f packs.txt
```
## Documentation for the CMSIS Toolbox 
* [CMSIS Toolbox Documentation](https://open-cmsis-pack.github.io/cmsis-toolbox/build-tools/)
