install_headers(
  'engine/gtd-manager.h',
  subdir: join_paths(meson.project_name(), 'engine')
)

interfaces_headers = files(
  'interfaces/gtd-activatable.h',
  'interfaces/gtd-panel.h',
  'interfaces/gtd-provider.h'
)

install_headers(
  interfaces_headers,
  subdir: join_paths(meson.project_name(), 'interfaces')
)

install_headers(
  'notification/gtd-notification.h',
  subdir: join_paths(meson.project_name(), 'notification')
)

enum_headers = files('gtd-enums.h')

headers = enum_headers + files(
  'gtd-object.h',
  'gtd-task.h',
  'gtd-task-list.h',
  'gtd-task-list-view.h',
  'gtd-timer.h',
  'gtd-types.h',
  'gtd-window.h',
  'gnome-todo.h'
)

install_headers(
  headers,
  subdir: meson.project_name()
)

sources = files(
  'engine/gtd-manager.c',
  'engine/gtd-plugin-manager.c',
  'interfaces/gtd-activatable.c',
  'interfaces/gtd-panel.c',
  'interfaces/gtd-provider.c',
  'notification/gtd-notification.c',
  'notification/gtd-notification-widget.c',
  'provider/gtd-provider-popover.c',
  'provider/gtd-provider-row.c',
  'provider/gtd-provider-selector.c',
  'views/gtd-list-selector.c',
  'views/gtd-list-selector-grid.c',
  'views/gtd-list-selector-grid-item.c',
  'views/gtd-list-selector-item.c',
  'views/gtd-list-selector-list.c',
  'views/gtd-list-selector-list-item.c',
  'views/gtd-list-selector-panel.c',
  'gtd-application.c',
  'gtd-arrow-frame.c',
  'gtd-dnd-row.c',
  'gtd-edit-pane.c',
  'gtd-empty-list-widget.c',
  'gtd-initial-setup-window.c',
  'gtd-new-task-row.c',
  'gtd-object.c',
  'gtd-plugin-dialog.c',
  'gtd-plugin-dialog-row.c',
  'gtd-task.c',
  'gtd-task-list.c',
  'gtd-task-list-view.c',
  'gtd-task-row.c',
  'gtd-timer.c',
  'gtd-window.c',
  'main.c'
)

sources += gnome.compile_resources(
  'gtd-resources',
  join_paths(data_dir, 'todo.gresource.xml'),
  source_dir: [
    data_dir,
    join_paths(meson.build_root(), 'plugins')
  ],
  c_name: 'todo',
  dependencies: plugins_confs,
  export: true
)

enum = 'gtd-enum-types'

sources += gnome.mkenums(
  enum,
  sources: enum_headers,
  c_template: enum + '.c.template',
  h_template: enum + '.h.template'
)

incs = [
  top_inc,
  include_directories(
    'engine',
    'provider',
    'notification',
    'interfaces',
    'views'
  )
]

cflags = [
  '-DPACKAGE_DATA_DIR="@0@"'.format(gnome_todo_pkgdatadir),
  '-DPACKAGE_LIB_DIR="@0@"'.format(gnome_todo_pkglibdir),
  '-DPACKAGE_LOCALE_DIR="@0@"'.format(gnome_todo_localedir),
  '-DPACKAGE_SRC_DIR="@0@"'.format(meson.current_source_dir()),
  '-DUI_DATA_DIR="@0@"'.format(join_paths(gnome_todo_pkgdatadir, 'style'))
]

ldflags = []

if host_machine.system().contains('linux')
  foreach ldflag: plugins_ldflags
    if cc.has_argument(ldflag)
      ldflags += ldflag
    endif
  endforeach
endif

gnome_todo = executable(
  meson.project_name(),
  sources,
  include_directories: incs,
  dependencies: gnome_todo_deps,
  c_args: cflags,
  link_with: plugins_libs,
  link_args: ldflags,
  install: true,
  install_dir: gnome_todo_bindir
)

libgtd = shared_library(
  'gtd',
  sources: sources,
  version: libversion,
  soversion: soversion,
  include_directories: incs,
  dependencies: gnome_todo_deps,
  c_args: cflags
)

libgtd_dep = declare_dependency(
  link_with: libgtd,
  include_directories: src_inc,
  dependencies: gnome_todo_deps
)

pkg.generate(
  libraries: libgtd,
  version: gnome_todo_version,
  name: 'Gnome To Do',
  description: 'Header and path for Gnome Todo Plugins',
  filebase: meson.project_name(),
  subdirs: meson.project_name(),
  variables: 'exec_prefix=' + gnome_todo_libexecdir,
  install_dir: join_paths(gnome_todo_libdir, 'pkgconfig')
)

if get_option('enable-introspection')
  gir_sources = files(
    'engine/gtd-manager.c',
    'engine/gtd-manager.h',
    'interfaces/gtd-activatable.c',
    'interfaces/gtd-activatable.h',
    'interfaces/gtd-panel.c',
    'interfaces/gtd-panel.h',
    'interfaces/gtd-provider.c',
    'interfaces/gtd-provider.h',
    'notification/gtd-notification.c',
    'notification/gtd-notification.h',
    'gtd-enums.h',
    'gtd-object.c',
    'gtd-object.h',
    'gtd-task.c',
    'gtd-task.h',
    'gtd-task-list.c',
    'gtd-task-list.h',
    'gtd-task-list-view.c',
    'gtd-task-list-view.h',
    'gtd-timer.c',
    'gtd-timer.h',
    'gtd-types.h',
    'gtd-window.c',
    'gtd-window.h'
  )

  gir_incs = [
    'Gio-2.0',
    'GObject-2.0',
    'Gtk-3.0'
  ]

  gir_extra_args = '--warn-all'

  gir_dir = join_paths(gnome_todo_datadir, '@0@-@1@'.format('gir', gnome_todo_gir_version))
  typelib_dir = join_paths(gnome_todo_libdir, '@0@-@1@'.format('girepository', gnome_todo_gir_version))

  gnome.generate_gir(
    gnome_todo,
    sources: gir_sources,
    namespace: gnome_todo_gir_namespace,
    nsversion: gnome_todo_gir_version,
    identifier_prefix: gnome_todo_gir_namespace,
    symbol_prefix: gnome_todo_gir_namespace.to_lower(),
    includes: gir_incs,
    include_directories: incs,
    extra_args: gir_extra_args,
    install: true,
    install_dir_gir: gir_dir,
    install_dir_typelib: typelib_dir
  )
endif
