/* gtd-eds-plugin.h
 *
 * Copyright (C) 2015 Georges Basile Stavracas Neto <georges.stavracas@gmail.com>
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

#ifndef GTD_EDS_PLUGIN_H
#define GTD_EDS_PLUGIN_H

#include "gnome-todo.h"

#include <glib.h>

G_BEGIN_DECLS

#define GTD_TYPE_PLUGIN_EDS (gtd_plugin_eds_get_type())

G_DECLARE_FINAL_TYPE (GtdPluginEds, gtd_plugin_eds, GTD, PLUGIN_EDS, PeasExtensionBase)

G_MODULE_EXPORT void  gtd_plugin_eds_register_types                        (PeasObjectModule   *module);

G_END_DECLS

#endif /* GTD_EDS_PLUGIN_H */
