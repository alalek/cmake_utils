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
# EXPECTED: -- foo_1 called
cmu_call_hooks(hook1)

cmu_remove_hook(hook1 foo)
# EXPECTED: -- foo_1 called
cmu_call_hooks(hook1)

cmu_install_hook(hook1 bar)
# EXPECTED: -- foo_1 called
# EXPECTED: -- bar called 1;2 3
cmu_call_hooks(hook1 1 "2 3")

# EXPECTED: -- bar called 1;2 3
# EXPECTED: -- foo_1 called
cmu_call_hooks_reverse(hook1 1 "2 3")
