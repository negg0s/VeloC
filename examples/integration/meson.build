project('veloc_integration', 'cpp',
  version : '1.0.0',
  default_options : ['warning_level=3', 'cpp_std=c++20'])

veloc_inc = include_directories('../../include')

executable('host_meson_app',
  'main.cpp',
  include_directories : veloc_inc,
  cpp_args : ['-mavx2', '-mfma', '-fwrapv']
)
