import gi
import logging

gi.require_version('Gtd',  '1.0')
gi.require_version('Peas', '1.0')

from gi.repository import Gio, GLib, GObject, Gtd, Gtk, Peas
from gettext import gettext as _


from taskc.simple import TaskdConnection


logger = logging.getLogger("gnome-todo-plugin:"+__name__)

def get_tasks():
    tc = TaskdConnection()
    tc = TaskdConnection.from_taskrc()
    resp = tc.pull()
    return resp


class TaskDManager(GObject.Object):

    def __init__(self):
        GObject.Object.__init__(self)

        manager = Gtd.Manager.get_default()

        manager.connect('list-added', self._setup_list)

        for tasklist in manager.get_task_lists():
            self._setup_list(manager, tasklist)

    def _setup_list(self, manager, tasklist):
        tasklist.connect('task-added', self._task_added)
        for task in tasklist.get_tasks():
            task.connect('notify::complete', self._task_complete)

    def _task_added(self, tasklist, task):
        task.connect('notify::complete', self._task_complete)

    def _task_complete(self, task, data):
        logger.info(task.get_title())
        logger.info("%s, %s", task, data)


class TaskwarriorPopover(Gtk.Popover):
    def __init__(self, button):
        Gtk.Popover.__init__(self, relative_to=button)

        button.set_popover(self)

        self._setup_listbox()

    def _setup_listbox(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                       spacing=6,
                       border_width=12)
        vbox.add(Gtk.Image.new_from_icon_name('face-embarrassed-symbolic',
                                              Gtk.IconSize.DIALOG))
        vbox.add(Gtk.Label(label=_("No task completed today")))
        vbox.show_all()

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.listbox.set_placeholder(vbox)
        self.listbox.get_style_context().add_class('background')

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                       spacing=6,
                       border_width=18)
        vbox.add(Gtk.Label(label='<b>' + _("Today") + '</b>',
                           use_markup=True,
                           hexpand=True,
                           xalign=0))
        vbox.add(self.listbox)
        vbox.show_all()

        self.add(vbox)


class TaskwarriorPlugin(GObject.Object, Gtd.Activatable):

    preferences_panel = GObject.Property(type=Gtk.Widget, default=None)

    def __init__(self):
        GObject.Object.__init__(self)
        logging.basicConfig(level=logging.DEBUG)
        self.header_button = Gtk.MenuButton()
        self.header_button.set_halign(Gtk.Align.END)
        self.header_button.set_label('TASKD SYNC')
        self.header_button.show_all()

        self.header_button.get_style_context().add_class('image-button')

        self.manager = TaskDManager()
        self.popover = TaskwarriorPopover(self.header_button)
        logger.info(get_tasks().data)
        # self.manager = Gtd.Manager.get_default()
    # def _score_changed(self, manager, score, task):
    #     print(score)
    #     self.header_button.set_label(str(score))

    # def setup(self):
    #     for tasklist in self.manager.get_task_lists():
    #         for task in tasklist.get_tasks():
    #             print(task.get_description())

    def do_activate(self):
        pass

    def do_deactivate(self):
        pass

    def do_get_header_widgets(self):
        return [self.header_button]

    def do_get_panels(self):
        return None

    def do_get_preferences_panel(self):
        return None

    def do_get_providers(self):
        return None
