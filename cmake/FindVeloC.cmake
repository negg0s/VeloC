# FindVeloC.cmake
# Locates VeloC compiler executable and standard include paths for CMake projects

find_program(VELOC_COMPILER
    NAMES veloc veloc.bat python
    PATHS "D:/VeloC"
    DOC "Path to VeloC compiler driver"
)

find_path(VELOC_INCLUDE_DIR
    NAMES veloc.h veloc_core.h
    PATHS "D:/VeloC/include"
    DOC "Path to VeloC include directory"
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(VeloC
    REQUIRED_VARS VELOC_COMPILER VELOC_INCLUDE_DIR
)

if(VeloC_FOUND)
    set(VELOC_INCLUDE_DIRS ${VELOC_INCLUDE_DIR})
    if(NOT TARGET VeloC::Core)
        add_library(VeloC::Core INTERFACE IMPORTED)
        set_target_properties(VeloC::Core PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${VELOC_INCLUDE_DIR}"
            INTERFACE_COMPILE_OPTIONS "-mavx2;-mfma;-fwrapv"
        )
    endif()

    function(veloc_add_executable target)
        cmake_parse_arguments(ARG "" "" "SOURCES" ${ARGN})
        add_executable(${target} ${ARG_SOURCES})
        target_link_libraries(${target} PRIVATE VeloC::Core)
    endfunction()
endif()
