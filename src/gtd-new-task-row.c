/* gtd-new-task-row.c
 *
 * Copyright (C) 2017 Georges Basile Stavracas Neto <georges.stavracas@gmail.com>
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

#include "gtd-manager.h"
#include "gtd-new-task-row.h"
#include "gtd-provider.h"
#include "gtd-task.h"
#include "gtd-task-list.h"

#include <math.h>

struct _GtdNewTaskRow
{
  GtkListBoxRow       parent;

  GtkEntry           *entry;
  GtkImage           *list_color_icon;
  GtkLabel           *list_name_label;
  GtkWidget          *list_selector_button;
  GtkSizeGroup       *sizegroup;
  GtkListBox         *tasklist_list;
  GtkPopover         *tasklist_popover;

  GtdTaskList        *selected_tasklist;

  GtdManager         *manager;
};

G_DEFINE_TYPE (GtdNewTaskRow, gtd_new_task_row, GTK_TYPE_LIST_BOX_ROW)

enum
{
  ENTER,
  EXIT,
  CREATE_TASK,
  NUM_SIGNALS
};

enum
{
  PROP_0,
  N_PROPS
};

static guint          signals [NUM_SIGNALS] = { 0, };

/*
 * Auxiliary methods
 */

static gboolean
gtd_new_task_row_focus_in_event (GtkWidget     *widget,
                                 GdkEventFocus *event)
{
  GtdNewTaskRow *self = GTD_NEW_TASK_ROW (widget);

  gtd_new_task_row_set_active (self, TRUE);

  return GDK_EVENT_PROPAGATE;
}

static cairo_surface_t*
get_circle_surface_from_color (GdkRGBA *color,
                               gint     size)
{
  cairo_surface_t *surface;
  cairo_t *cr;

  surface = cairo_image_surface_create (CAIRO_FORMAT_ARGB32, size, size);
  cr = cairo_create (surface);

  cairo_set_source_rgba (cr,
                         color->red,
                         color->green,
                         color->blue,
                         color->alpha);
  cairo_arc (cr, size / 2.0, size / 2.0, size / 2.0, 0., 2 * M_PI);
  cairo_fill (cr);
  cairo_destroy (cr);

  return surface;
}

static void
set_selected_tasklist (GtdNewTaskRow *self,
                       GtdTaskList   *list)
{
  cairo_surface_t *surface;
  GtdManager *manager;
  GdkRGBA *color;

  manager = gtd_manager_get_default ();

  /* NULL list means the default */
  if (!list)
    list = gtd_manager_get_default_task_list (manager);

  if (!g_set_object (&self->selected_tasklist, list))
    return;

  color = gtd_task_list_get_color (list);
  surface = get_circle_surface_from_color (color, 12);

  gtk_image_set_from_surface (self->list_color_icon, surface);
  gtk_label_set_label (self->list_name_label, gtd_task_list_get_name (list));

  cairo_surface_destroy (surface);
  gdk_rgba_free (color);
}

/*
 * Callbacks
 */

static void
default_tasklist_changed_cb (GtdNewTaskRow *self)
{
  set_selected_tasklist (self, NULL);
}

static void
entry_activated_cb (GtdNewTaskRow *self)
{
  GtdProvider *provider;
  GtdTask *new_task;

  /* Cannot create empty tasks */
  if (gtk_entry_get_text_length (self->entry) == 0)
    return;

  provider = gtd_task_list_get_provider (self->selected_tasklist);

  new_task = gtd_provider_generate_task (provider);
  gtd_task_set_title (new_task, gtk_entry_get_text (self->entry));

  g_signal_emit (self, signals[CREATE_TASK], 0, new_task, self->selected_tasklist);

  gtk_entry_set_text (self->entry, "");
}

static void
tasklist_selected_cb (GtkListBox    *listbox,
                      GtkListBoxRow *row,
                      GtdNewTaskRow *self)
{
  GtdTaskList *list;

  list = g_object_get_data (G_OBJECT (row), "tasklist");

  set_selected_tasklist (self, list);

  gtk_popover_popdown (self->tasklist_popover);
  gtk_entry_grab_focus_without_selecting (self->entry);
}

static void
update_tasklists_cb (GtdNewTaskRow *self)
{
  GList *tasklists, *l;

  gtk_container_foreach (GTK_CONTAINER (self->tasklist_list),
                         (GtkCallback) gtk_widget_destroy,
                         NULL);

  tasklists = gtd_manager_get_task_lists (self->manager);

  for (l = tasklists; l != NULL; l = l->next)
    {
      GtkWidget *row, *box, *icon, *name, *provider;
      cairo_surface_t *surface;
      GdkRGBA *color;

      box = g_object_new (GTK_TYPE_BOX,
                          "orientation", GTK_ORIENTATION_HORIZONTAL,
                          "spacing", 12,
                          "margin", 6,
                          NULL);

      /* Icon */
      color = gtd_task_list_get_color (l->data);
      surface = get_circle_surface_from_color (color, 12);
      icon = gtk_image_new_from_surface (surface);

      gtk_container_add (GTK_CONTAINER (box), icon);

      /* Tasklist name */
      name = g_object_new (GTK_TYPE_LABEL,
                           "label", gtd_task_list_get_name (l->data),
                           "xalign", 0.0,
                           "hexpand", TRUE,
                           NULL);

      gtk_container_add (GTK_CONTAINER (box), name);

      /* Provider name */
      provider = g_object_new (GTK_TYPE_LABEL,
                               "label", gtd_provider_get_description (gtd_task_list_get_provider (l->data)),
                               "xalign", 0.0,
                               NULL);
      gtk_style_context_add_class (gtk_widget_get_style_context (provider), "dim-label");
      gtk_size_group_add_widget (self->sizegroup, provider);
      gtk_container_add (GTK_CONTAINER (box), provider);

      /* The row itself */
      row = gtk_list_box_row_new ();
      gtk_container_add (GTK_CONTAINER (row), box);
      gtk_container_add (GTK_CONTAINER (self->tasklist_list), row);

      g_object_set_data (G_OBJECT (row), "tasklist", l->data);

      gtk_widget_show_all (row);

      cairo_surface_destroy (surface);
      gdk_rgba_free (color);
    }

  g_list_free (tasklists);
}

static void
gtd_new_task_row_get_property (GObject    *object,
                               guint       prop_id,
                               GValue     *value,
                               GParamSpec *pspec)
{
  G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
}

static void
gtd_new_task_row_set_property (GObject      *object,
                               guint         prop_id,
                               const GValue *value,
                               GParamSpec   *pspec)
{
  G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
}

static void
gtd_new_task_row_dispose (GObject *object)
{
  GtdNewTaskRow *self = GTD_NEW_TASK_ROW (object);

  if (self->manager)
    {
      g_signal_handlers_disconnect_by_func (self->manager,
                                            update_tasklists_cb,
                                            self);

      g_signal_handlers_disconnect_by_func (self->manager,
                                            default_tasklist_changed_cb,
                                            self);

      self->manager = NULL;
    }

  g_clear_object (&self->selected_tasklist);

  G_OBJECT_CLASS (gtd_new_task_row_parent_class)->dispose (object);
}

static void
gtd_new_task_row_class_init (GtdNewTaskRowClass *klass)
{
  GObjectClass *object_class = G_OBJECT_CLASS (klass);
  GtkWidgetClass *widget_class = GTK_WIDGET_CLASS (klass);

  object_class->dispose = gtd_new_task_row_dispose;
  object_class->get_property = gtd_new_task_row_get_property;
  object_class->set_property = gtd_new_task_row_set_property;

  widget_class->focus_in_event = gtd_new_task_row_focus_in_event;

  /**
   * GtdNewTaskRow::enter:
   *
   * Emitted when the row is focused and in the editing state.
   */
  signals[ENTER] = g_signal_new ("enter",
                                 GTD_TYPE_NEW_TASK_ROW,
                                 G_SIGNAL_RUN_LAST,
                                 0,
                                 NULL,
                                 NULL,
                                 NULL,
                                 G_TYPE_NONE,
                                 0);

  /**
   * GtdNewTaskRow::exit:
   *
   * Emitted when the row is unfocused and leaves the editing state.
   */
  signals[EXIT] = g_signal_new ("exit",
                                GTD_TYPE_NEW_TASK_ROW,
                                G_SIGNAL_RUN_LAST,
                                0,
                                NULL,
                                NULL,
                                NULL,
                                G_TYPE_NONE,
                                0);

  /**
   * GtdNewTaskRow::create-task:
   *
   * Emitted when the row wants the parent widget to create a new task.
   * If the task list is %NULL, assume the default task list of the
   * default provider.
   */
  signals[CREATE_TASK] = g_signal_new ("create-task",
                                       GTD_TYPE_NEW_TASK_ROW,
                                       G_SIGNAL_RUN_LAST,
                                       0,
                                       NULL,
                                       NULL,
                                       NULL,
                                       G_TYPE_NONE,
                                       2,
                                       GTD_TYPE_TASK,
                                       GTD_TYPE_TASK_LIST);

  gtk_widget_class_set_template_from_resource (widget_class, "/org/gnome/todo/ui/new-task-row.ui");

  gtk_widget_class_bind_template_child (widget_class, GtdNewTaskRow, entry);
  gtk_widget_class_bind_template_child (widget_class, GtdNewTaskRow, list_color_icon);
  gtk_widget_class_bind_template_child (widget_class, GtdNewTaskRow, list_name_label);
  gtk_widget_class_bind_template_child (widget_class, GtdNewTaskRow, list_selector_button);
  gtk_widget_class_bind_template_child (widget_class, GtdNewTaskRow, sizegroup);
  gtk_widget_class_bind_template_child (widget_class, GtdNewTaskRow, tasklist_list);
  gtk_widget_class_bind_template_child (widget_class, GtdNewTaskRow, tasklist_popover);

  gtk_widget_class_bind_template_callback (widget_class, entry_activated_cb);
  gtk_widget_class_bind_template_callback (widget_class, tasklist_selected_cb);

  gtk_widget_class_set_css_name (widget_class, "taskrow");
}

static void
gtd_new_task_row_init (GtdNewTaskRow *self)
{
  GtdManager *manager = gtd_manager_get_default ();

  gtk_widget_init_template (GTK_WIDGET (self));

  g_signal_connect_swapped (manager,
                            "list-added",
                            G_CALLBACK (update_tasklists_cb),
                            self);

  g_signal_connect_swapped (manager,
                            "list-changed",
                            G_CALLBACK (update_tasklists_cb),
                            self);

  g_signal_connect_swapped (manager,
                            "list-removed",
                            G_CALLBACK (update_tasklists_cb),
                            self);

  g_signal_connect_swapped (manager,
                            "notify::default-task-list",
                            G_CALLBACK (default_tasklist_changed_cb),
                            self);

  self->manager = manager;

  set_selected_tasklist (self, NULL);
}

GtkWidget*
gtd_new_task_row_new (void)
{
  return g_object_new (GTD_TYPE_NEW_TASK_ROW, NULL);
}

gboolean
gtd_new_task_row_get_active (GtdNewTaskRow *self)
{
  g_return_val_if_fail (GTD_IS_NEW_TASK_ROW (self), FALSE);

  return gtk_widget_has_focus (GTK_WIDGET (self->entry));
}

void
gtd_new_task_row_set_active (GtdNewTaskRow *self,
                             gboolean       active)
{
  g_return_if_fail (GTD_IS_NEW_TASK_ROW (self));

  if (active)
    {
      gtk_widget_grab_focus (GTK_WIDGET (self->entry));
      g_signal_emit (self, signals[ENTER], 0);
    }
}

void
gtd_new_task_row_set_show_list_selector (GtdNewTaskRow *self,
                                         gboolean       show_list_selector)
{
  g_return_if_fail (GTD_IS_NEW_TASK_ROW (self));

  gtk_widget_set_visible (self->list_selector_button, show_list_selector);
}
