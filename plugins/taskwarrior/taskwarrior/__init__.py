import gi
import logging
import uuid
import datetime
import json

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


class TaskwarriorProvider(Gtd.Object, Gtd.Provider):
    name = GObject.Property(type=str, default="taskwarrior")
    id = GObject.Property(type=str, default="taskwarrior")
    icon = GObject.Property(type=Gio.Icon)
    enabled = GObject.Property(type=bool, default=True)
    description = GObject.Property(type=str, default="a client for taskd")
    UUID_NAMESPACE = "d9e2c023-85ef-4df4-bff5-b917b40aac27"

    def __init__(self):
        Gtd.Object.__init__(self)
        self.lists = []

    def do_get_description(self):
        tc = TaskdConnection.from_taskrc()
        return "TaskWarrior on {}".format(tc.server)

    @GObject.Property(type=Gtd.TaskList)
    def default_task_list(self):
        return self.lists[0]

    def do_get_name(self):
        return self.name

    def do_get_id(self):
        return "taskwarrior"

    def do_get_icon(self):
        return self.icon

    def do_get_task_lists(self):
        twtasks = get_tasks()
        return twtasks

    def do_get_enabled(self):
        return self.enabled

    def do_create_task(self, task):
        logger.info("do_create_task: %s", task.get_title())
        self.send(task)

    def send(self, task):
        "Take a Gnome To-do task and convert and send it to taskd"
        twjson = self.to_twjson(task)
        tc = TaskdConnection()
        tc = TaskdConnection.from_taskrc()
        finalized = "\n\n"+json.dumps(twjson) # no synckey support yet
        tc.put(finalized)
        logger.info(twjson)

    def to_twjson(self, task):
        task_date = "%Y%m%dT%H%M%SZ"
        out = dict()
        out['description'] = task.get_title()
        out['status'] = "completed" if task.get_complete() else "pending"
        out['uuid'] = str(uuid.uuid5(
            uuid.UUID(self.UUID_NAMESPACE), task.get_title()))
        created = task.get_creation_date()
        if created:
            logging.info("Got creation_date: %s", created)
            out['entry'] = datetime.datetime.utcfromtimestamp(created.to_unix()).strftime(
                task_date)  # if you run this after 2038 here be dragons?
        else:
            out['entry'] = datetime.datetime.now().strftime(task_date)
        # if i['due_date_utc']:
        #     out['due'] = datetime.datetime.strptime(i['due_date_utc'][:-6], todoist_date).strftime(task_date)
        out['modified'] = out['entry']
        return out

    def do_update_task(self, task):
        logger.info("do_update_task: %s", task.get_title())
        self.send(task)

    def do_remove_task(self, task):
        pass

    def do_create_task_list(self, gtdlist):
        """TW doesn't really have tasklists so idk what to do here entirely
        Looks like we're expected to emit a signal tho?"""
        logger.info(gtdlist.get_name())
        self.lists.append(gtdlist)
        self.emit("list-added", gtdlist)


    def do_update_task_list(self, list):
        pass


class TaskwarriorPlugin(GObject.Object, Gtd.Activatable):

    preferences_panel = GObject.Property(type=Gtk.Widget, default=None)

    def __init__(self):
        GObject.Object.__init__(self)
        logging.basicConfig(level=logging.DEBUG)
        self.header_button = Gtk.MenuButton()
        self.header_button.set_halign(Gtk.Align.END)
        self.header_button.set_label('Taskd Sync')
        self.header_button.show_all()

        self.header_button.get_style_context().add_class('image-button')

        self.manager = TaskDManager()
        self.popover = TaskwarriorPopover(self.header_button)

        self.provider = TaskwarriorProvider()
        # logger.info(get_tasks().data)

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
        return [self.provider]
