cmake_minimum_required(VERSION 3.13.4)

project(AQ3DC)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/AQ3DC")
set(EXTENSION_CATEGORY "Measures")
set(EXTENSION_CONTRIBUTORS "John Doe (AnyWare Corp.), Baptiste Baquero (UoM)")
set(EXTENSION_DESCRIPTION "This is an example of a simple extension")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/AQ3DC.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/AQ3DC/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(AQ3DC)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
