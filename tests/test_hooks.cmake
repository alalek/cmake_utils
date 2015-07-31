include(cmu_hooks)

function(foo)
  message(STATUS "foo called")
endfunction()

function(foo_1)
  message(STATUS "foo_1 called")
endfunction()

function(bar)
  message(STATUS "bar called ${ARGN}")
endfunction()

cmu_install_hook(hook1 foo)

# EXPECTED: -- foo called
cmu_call_hooks(hook1)

cmu_install_hook(hook1 foo_1)
# EXPECTED: -- foo called
# EXPECTED-NEXT: -- foo_1 called
cmu_call_hooks(hook1)

cmu_remove_hook(hook1 foo)
# EXPECTED: -- foo_1 called
cmu_call_hooks(hook1)

cmu_install_hook(hook1 bar)
# EXPECTED: -- foo_1 called
# EXPECTED-NEXT: -- bar called 1;2 3
cmu_call_hooks(hook1 1 "2 3")

# EXPECTED: -- bar called 1;2 3
# EXPECTED-NEXT: -- foo_1 called
cmu_call_hooks_reverse(hook1 1 "2 3")


macro(my_add_module_hook)
  if (module_name STREQUAL "module_to_hook")
    list(APPEND SOURCE_FILES my_src.cpp)
  endif()
endmacro()

cmu_install_hook(add_module my_add_module_hook)

function(add_module module_name)
  set(SOURCE_FILES "main.cpp")
  cmu_call_hooks(add_module)
  message(STATUS "Source files: ${SOURCE_FILES}")
endfunction()

# EXPECTED: -- Source files: main.cpp
add_module(module1)
# EXPECTED: -- Source files: main.cpp;my_src.cpp
add_module(module_to_hook)
