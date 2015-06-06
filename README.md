CMake utilities
===============

How to use
----------

1) For comfortable usage add `cmake/cmake_utils` into your project and update `CMAKE_MODULE_PATH`. For example:

```
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake/cmake_utils)
```

2) Include required module somewhere:

```
include(cmu_call) # include module that add indirect calls
include(cmu_hooks) # include module that add hooks functionality
```

Usage examples
--------------

### Indirect calls

```
cmu_call("${callback_function_name}" "${result}")
```

### Hooks

```
macro(my_add_module_hook)
  if (module_name STREQUAL "module_to_hook")
    list(APPEND SOURCE_FILES my_src.cpp)
  endif()
endmacro()

cmu_install_hook(add_module my_add_module_hook)

message(STATUS "... somewhere later ...")

function(add_module module_name)
  set(SOURCE_FILES "main.cpp")
  cmu_call_hooks(add_module) # only this line is injected instead of multiline hooks bodies
  message(STATUS "Source files: ${SOURCE_FILES}")
  # ...
endfunction()

add_module(module1) # bypass without changes
add_module(module_to_hook) # will add my_src.cpp to SOURCE_FILES
```
