include(cmu_call)

function(foo)
  message(STATUS "foo called")
endfunction()

function(foo_1)
  message(STATUS "foo_1 called")
endfunction()

function(bar)
  message(STATUS "bar called ${ARGN}")
endfunction()

# EXPECTED: -- foo called
cmu_call(foo 1 2 3)

# EXPECTED: -- foo_1 called
set(id 1)
cmu_call(foo_${id} 1 2 3)

# EXPECTED: -- bar called 1;2;3
cmu_call(bar 1 2 3)

# EXPECTED: -- bar called 1;2 3
cmu_call(bar 1 "2 3")
