---
name: cmsis-stream
description: This skill must be used to create new components for CMSIS Stream. It generates the Python description and C++ wrapper for a component.
---

# CMSIS Stream

## Target & Persona

- **Role:** Software Developer and CMSIS Stream Component Integrator.
- **Objective:** Generate the Python description and C++ wrapper for a new CMSIS Stream component from the user's specification, so the user can implement its functionality in the generated files.

### When to use this skill

When the user needs to create a new component for CMSIS Stream, they can use this skill to generate the Python description and C++ wrapper for the component. This skill will help the user to quickly create the necessary files and structure for the new component, allowing them to focus on implementing the functionality rather than setting up the project.

## Prerequisites & Context

- **Expected input:** The component specification listed below and the destination folders for the generated Python description and C++ wrapper. Update `__init__.py` in the specified Python folder to import the new component.
- **Dependencies:** The generated files use the CMSIS Stream Python package, the CMSIS Stream C++ headers, and `cg_enums.h` and `app_config.hpp` supplied by the integrating project. Generation requires the component specification and destination folders; it does not require a generated graph or a C++ build environment. Optional Python import checks require an available Python environment containing the CMSIS Stream package.
- **Portability:** Generate descriptions and wrappers for the CMSIS Stream APIs described below. Device, compiler, build-system, debugger, and RTOS choices come from the input project; this skill does not select them. Confirm the project's CMSIS Stream API supports the required component features.

Each component is self-contained so it can easily be plugged into a CMSIS Stream graph. Generate it from the user's specification; the Python and C++ destination folders determine where to write its files. Knowing or inspecting other components is not a prerequisite.

## Execution Steps (Strict Workflow)

1. **Analysis:** Obtain the Python and C++ destination folders and gather the component specification, including the Python and C++ class names, ports, types, lengths, parameters, visibility, events, and state. Ask for missing details before generating files.
2. **Processing:** Generate the Python description and C++ wrapper using the rules below, and update the Python package's `__init__.py` to import the new component.
3. **Validation:** Compare both files with the confirmed specification and the Python and C++ requirements below. Perform the available checks in Validation Resources and report any checks that could not be completed.
4. **Formatting:** Store the files in the specified Python and C++ destination folders using the specified class names. Report the generated files, the import update, validation results, and any functionality the user must implement.

### Standard workflow for using this skill

1. The user will provide the necessary information about the new component, such as its name, C++ class name, and any other relevant details.
2. The skill will generate the Python description and C++ wrapper for the component.
3. The user can then implement the functionality of the component in the generated files.

If the user does not provide all the necessary information, the skill will ask for the missing details before proceeding with the generation of the files.
Don't make any assumptions about the component and ask for all the necessary information to create a complete and accurate description of the component.

You can use following template to ask for the necessary information from the user:
```text
Python class: DSP
C++ class: DSP
Python destination folder: user-specified path
C++ destination folder: user-specified path
Ports: 1 dataflow input i, 1 dataflow output o
Types: i=F32, o=F32 (specify a fixed type or variable for each dataflow port)
Lengths: i=variable, o=variable (specify a fixed sample count or variable for each dataflow port)
Parameters: none or default (for no parameter), or list of initialization parameter names
Visible: no
State: no
Events: list of names or default (for no new event introduced)
Sends events without event output ports: no
```
The name of the ports are given in the description (i and o in the above template) but the user can choose other names if they want. The type and length of the ports can be fixed or variable. If they are variable, it means that the component can work with different types and lengths and those information will be passed as arguments to the constructor of the component.

### Information needed from the user to describe the component

- Destination folders: Where to generate the Python description and C++ wrapper.
- Component name: The name of Python class for the new component.
- C++ class name: The name of the C++ class that will be generated for the component.
- Number of inputs and output ports
- For each port : is it a dataflow port or event port
- For a dataflow port, the data type and the size of the data (in number of samples) if this number cannot been changed. If it can be changed it will be a variable
- If events are used, the node may introduce new events and the user should provide the name of the new events.
- Whether the component must send events without event output ports, including events sent to the application; this determines whether an explicit `evtQueue` constructor argument is needed.
- The user must say if the component has parameters than can be set at initialization
- The user must say if the component is visible from the outside world
- The user must specify if the component has a state that must be managed during context switches


### Python description for the component

The Python description must be generated in the folder containing all Python descriptions. Generally it is named `nodes` and contain a `__init__.py` file.
The `__init__.py`  must be updated to import the new component.

If the name of the component is `MyComponent`, the Python description must be named `MyComponent.py` .

The component file must include CMSIS Stream definitions from the CMSIS Stream python package:
```python
from cmsis_stream.cg.scheduler import *
```

The component file must contain a class named `MyComponent`. The class must have an `__init__` method that initializes the component and defines its ports, parameters, events, and state if necessary. The class must have an `typeName` property that returns the C++ class name as a string.

If the class only has event ports, it inherits from `BaseNode`.
If the class has some dataflow ports it must inherit from `GenericSink` if those dataflow ports are only input ports, from `GenericSource` if those dataflow ports are only output ports, and from `GenericNode` if those dataflow ports are both input and output ports.

The `__init__` method must define the dataflow port using:
- `self.addInput(inputPortName,theType,inLength)`
- `self.addOutput(outputPortName,theType,inLength)`

The input port name is generally named `i` or in case of several input ports `i1`, `i2`, etc. The output port name is generally named `o` or in case of several output ports `o1`, `o2`, etc.
The type is defined with `CType(DT)` where `DT` as defined by CMSIS Stream can be : 
- F64
- F32
- F16
- Q31
- Q15
- Q7
- UINT32
- UINT16
- UINT8
- SINT32
- SINT16
- SINT8

Those types are generally passed as argument of the constructor if the port can work with different types. If the type is fixed, it can be directly defined in the component description.
The length is also generally passed as argument of the constructor if the port can work with different lengths. If the length is fixed, it can be directly defined in the component description.

If the component has parameters, they must be defined in the `__init__` method using  `self.addVariableArg(f"params->{name}")`.
It will add a new argument to the C++ constructor and code generated by CMSIS Stream will automatically set the value of this argument to the value of the variable `params->{name}` where name is the name of the node instantiating this component.

`self.addVariableArg` must be added after defining all the ports.

If the port is an event port, it can be defined with:
`self.addEventInput()` or `self.addEventOutput()`

Those functions take an optional argument `nb` if several event inputs or event outputs must be created. It is also possible to use those functions several times to create several event inputs or outputs.

The parent class supports some optional named parameters in the constructor.
- `identified` that can be `True` or `False`
- `selectors` that can be set to a list of strings to define event names recognized by the component

Pass `identified=True` to the parent constructor when the user specifies `Visible: yes`, and `identified=False` when the user specifies `Visible: no`. Do not rely on the parent constructor's default. If the integrating runtime requires identification for context switching, clarify that requirement with the user instead of silently changing the requested visibility.

If the component has no event output port but must still be able to send events, the Python should define a new argument for the C++ constructor
```python
self.addVariableArg("evtQueue")
```

The name `evtQueue` is special and will be used by the code generator to set the value of this argument to the pointer of the EventQueue that is used internally by the component to send events.

A component can send events to the application so it may need to send events even if it has no event output ports.

### C++ description for the component

Generate a new header file for the component in the folder containing all C++ descriptions. 
The header file uses the C++ name defined during description of the component and is named `MyComponent.hpp` if the C++ class name is `MyComponent`.

The generated file will contain the definition for the C++ component.

The file must start with
```C++
#pragma once



#include "cg_enums.h"
#include "app_config.hpp"
#include "StreamNode.hpp"
#include "GenericNodes.hpp"


using namespace arm_cmsis_stream;
```

If the component has any dataflow port then it will be implemented as a template. If the component has no dataflow port then it will be defined as a normal class inheriting from public StreamNode.

Select the C++ dataflow base class according to the number of dataflow input and output ports. Event ports do not count toward this selection. Set its template parameters according to the type and length of each dataflow port.

| Dataflow inputs | Dataflow outputs | C++ base class |
| --- | --- | --- |
| 1 | 1 | `GenericNode` |
| 1 | 2 | `GenericNode12` |
| 1 | 3 | `GenericNode13` |
| 2 | 1 | `GenericNode21` |
| 3 | 1 | `GenericNode31` |
| 1 | 0 | `GenericSink` |
| 0 | 1 | `GenericSource` |

Use a matching base class from the applicable `GenericNodes.hpp` when it provides another required layout. Do not append extra template arguments to a class whose signature does not support that port count.

If the default header does not provide the required layout, generate a custom C++ dataflow base class extending `NodeBase`, the C++ dataflow base declared in `GenericNodes.hpp`. This allows components with additional input or output dataflow ports. Define the typed FIFO references, constructor arguments, and buffer-access methods for the required ports, preserving the input-before-output ordering. Keep any required custom base in the generated component header; do not modify the CMSIS Stream headers.

Python `GenericNode` supports any number of dataflow input and output ports, so additional ports do not require extending a Python base class. The custom-base guidance above applies only to C++, where the dataflow base is named `NodeBase`. Keep the Python port description and the C++ FIFO and template layout consistent.

The template arguments are as follow:
- The list of inputs come first
- The list of output follows

For each port, the template has two arguments:
- A typename for the sample type
- An int for the number of samples processed by the port (consumed or produced)

If the component has any dataflow port, it must implement the `int run()` method that will be called by the CMSIS Stream scheduler to process the data. The `run` method must read the input data from the input ports, process it, and write the output data to the output ports. Generate the required method skeleton and identify the functionality the user must complete.

If state must be managed during context switches, the component must also publicly inherit from the applicable runtime's `ContextSwitch` interface, in addition to its component base class. Generate the following method declarations or skeletons, leaving their state-management functionality for the user to implement:

```C++
int pause() override;
int resume() override;
```

Use the interface signatures supported by the integrating runtime. Do not invent state-saving or state-restoration behavior, and report that these methods remain unimplemented.

If the component has any event output port, it must implement the 
```C++
void subscribe(int outputPort,StreamNode &dst,int dstPort)
```

and must define protected member variables of type `EventOutput` for each event output.

The argument of the constructor are the FIFOs for the input, followed by the FIFOs for the output and followed by an EventQueue if there is any event output port. 

Example:
```C++
DebugSink(FIFOBase<IN> &dst,EventQueue *queue)
```

If the component defines any new event, it must define a static array to make a link between global ID of the event and a local ID.
Example:
```C++
public:
  enum selector {selMessage=0};
  static std::array<uint16_t,1> selectors;
```

If the component needs any parameter, it can take as last argument of the constructor a parameter struct. For instance:
```C++
  DebugSource(FIFOBase<IN> &src, emptySourceParams_t &params)
```

If the component has any input event port, it must implement the processEvent method:
```C++
cg_status processEvent(int dstPort,Event &&evt) final
```

The return type must match the declaration in `StreamNode.hpp`. The generated method must return an appropriate `cg_status` when its event-handling functionality is implemented.

Testing for a event defined by the component is done with the `selectors` array. 

Example:
```C++
 if (evt.event_id == selectors[selMessage])
```

If the event is a default event as define in `cg_enums.h` CMSIS stream header then the test can use directly the global ID since this ID will not change for different graphs:
Example:
```C++
 if (evt.event_id == kValue)
```

To process an event, some convenience functions are defined in the CMSIS Stream headers. For instance
```C++
if (evt.wellFormed<float>())
{
                evt.apply<float>(&DebugEvtSink::messageReceived, *this);
}
```

In this example, the function messageReceived has type:
```C++
void messageReceived(float v)
```

If the node has no output event port but must still be able to send events, it can define an internal event queue and use it to send events. In this case, the constructor of the component must take as argument a pointer to an EventQueue and store it in a member variable. The component can then create events and push them to the queue to send them to other components.

In that case the EventQueue argument is the first after the dataflow FIFO arguments.
It is defined in the Python by using the specific argument `evtQueue` in the `addVariableArg` function as described in the previous section. And the C++ constructor will have an argument named `EventQueue *queue` and the component will store this pointer in a member variable to use it to send events when needed.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not assume component properties or invent CMSIS Stream APIs, event names, parameter definitions, state-management behavior, paths, or validation results. Ask the user for all missing information needed to generate a complete and accurate component description.
- **Portability:** CMSIS Stream components are portable but rely on an OS-specific runtime for events.
- **Critical blockers:** Stop generation when the component specification or destination folders are missing or ambiguous, or the required API behavior cannot be established. If a Python import check is unavailable, report that limitation and do not claim it passed.
- **Scope:** Generate the requested Python description and C++ wrapper and update the existing Python package import. The user can then implement the component's functionality in the generated files. Do not treat a generated wrapper as proof that the algorithm is implemented or functionally validated.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

- A Python file named after the component's Python class, such as `MyComponent.py`, in the specified Python destination folder, generally `nodes`.
- An update to that folder's `__init__.py` importing the new component.
- A C++ header named after the component's C++ class, such as `MyComponent.hpp`, in the specified C++ destination folder.
- Both files must satisfy the applicable port, type, length, parameter, visibility, event, and state requirements confirmed with the user, including all relevant Python and C++ rules above.
- A concise report of the files generated, the import update, checks performed, checks that remain unavailable, and functionality left for the user to implement.

## Validation Resources

Use the confirmed component specification and the applicable CMSIS Stream Python package and C++ headers as the validation resources. When available, use a configured Python environment for import checks; do not invent installation commands. Validate C++ structure against the documented API without compiling it. Validation does not require inspecting other components.

1. **Specification and file checks:** Verify the Python and C++ class names, destination folders, filenames, and `__init__.py` import. Compare every requested port, fixed or variable type and length, parameter, visibility setting, event, and state requirement with both generated files.
2. **Python checks:** When a configured Python environment is available, import the new component through its package and instantiate it with representative arguments from the confirmed specification. Otherwise, review these requirements structurally and report that the import check was not performed. Verify its base class, `typeName`, dataflow and event ports, the `identified` value corresponding to the requested visibility, `selectors` settings when used, and variable constructor arguments. Confirm ports are defined before `self.addVariableArg` calls and that `evtQueue` is supplied when the user requests events without event output ports.
3. **C++ checks:** Verify the required header preamble, the base class for the dataflow port count, template arguments, FIFO references, constructor argument order, and applicable `run`, `subscribe`, `EventOutput`, `selectors`, and `processEvent` definitions. For a custom `NodeBase` extension, check that its FIFO and buffer-access layout agrees with the Python ports. Verify that `processEvent` returns `cg_status` and matches `StreamNode.hpp`. Check component-defined events through their local selectors, default events through the IDs in `cg_enums.h`, and event-queue storage and use when required. For stateful components, verify `ContextSwitch` inheritance and the `int pause()` and `int resume()` method skeletons. Do not compile the generated C++ code; focus on structural and syntactic correctness and report the limits of those checks. Compilation and functional testing are follow-on work after the user completes the functionality and integrates the component into a CMSIS Stream graph generated from Python.
4. **Result reporting:** Record the checks and their results. Identify missing validation dependencies and incomplete functionality the user must implement. Python import success and C++ structural review do not prove functional behavior, event delivery, or context-switch state handling.
