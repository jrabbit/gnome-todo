/* gtd-plugin-dark-theme.h
 *
 * Copyright (C) 2016 Georges Basile Stavracas Neto <georges.stavracas@gmail.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef GTD_PLUGIN_DARK_THEME_H
#define GTD_PLUGIN_DARK_THEME_H

#include <glib.h>
#include <gnome-todo.h>

G_BEGIN_DECLS

#define GTD_TYPE_PLUGIN_DARK_THEME (gtd_plugin_dark_theme_get_type())

G_DECLARE_FINAL_TYPE (GtdPluginDarkTheme, gtd_plugin_dark_theme, GTD, PLUGIN_DARK_THEME, PeasExtensionBase)

G_MODULE_EXPORT void gtd_plugin_dark_theme_register_types        (PeasObjectModule   *module);

G_END_DECLS

#endif /* GTD_PLUGIN_DARK_THEME_H */
