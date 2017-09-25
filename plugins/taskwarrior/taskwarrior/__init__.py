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
    INBOX_NAME = "TW inbox"
    def __init__(self):
        Gtd.Object.__init__(self)
        self.lists = []
        self.create_inbox()

    def create_inbox(self):
        new_list = Gtd.TaskList.new(self)
        new_list.set_name(self.INBOX_NAME)
        # inbox = manager.create_task_list(new_list)
        tc = TaskdConnection.from_taskrc()
        tasks = tc.pull().data
        for task in tasks:
            # make task into gtdtask
            logger.info(task)

            gtdtask = Gtd.Task.new() # This doesn't work until EDS deps are removed in gtd
            gtdtask.set_title("timmy")
            gtdtask.set_list(new_list)
            # manager = Gtd.Manager.get_default()
            # manager.create_task(gtdtask) # this triggers a push
            logger.info("saving task")
            new_list.save_task(gtdtask)
            # new_list.emit('task-added', gtdtask)
        self.lists.append(new_list)
        self.emit("list-added", new_list)

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
        self.icon = Gio.Icon.new_for_string('network-server-symbolic')
        return self.icon

    def do_get_task_lists(self):
        return self.lists

    def do_get_enabled(self):
        return self.enabled

    def do_create_task(self, task):
        logger.info("do_create_task: %s", task.get_title())
        self.send(task)

    def send(self, task):
        "Take a Gnome To-do task and convert and send it to taskd"
        twjson = self.to_twjson(task)
        tc = TaskdConnection.from_taskrc()
        finalized = "\n\n"+json.dumps(twjson)  # no synckey support yet
        tc.put(finalized)
        logger.info(twjson)

    def to_twjson(self, task):
        task_date = "%Y%m%dT%H%M%SZ"
        out = dict()
        out['description'] = task.get_title()
        out['status'] = "completed" if task.get_complete() else "pending"
        inlist = task.get_list().get_name()
        if inlist is not self.INBOX_NAME:
            out['project'] = inlist
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

    def delete_task(self, task):
        twjson = self.to_twjson(task)
        tc = TaskdConnection.from_taskrc()
        twjson["status"] = "deleted"
        finalized = "\n\n"+json.dumps(twjson)  # no synckey support yet
        tc.put(finalized)
        logger.info(twjson)


    def do_update_task(self, task):
        logger.info("do_update_task: %s", task.get_title())
        self.send(task)

    def do_remove_task(self, task):
        self.delete_task(task)

    def do_create_task_list(self, gtdlist):
        """TW doesn't really have tasklists so idk what to do here entirely
        Looks like we're expected to emit a signal tho?"""
        logger.info(gtdlist.get_name())
        gtdlist.set_is_removable(True)
        self.lists.append(gtdlist)
        self.emit("list-added", gtdlist)

    def do_update_task_list(self, gtdlist):
        self.emit("list-changed", gtdlist)

    def do_remove_task_list(self, gtdlist):
        "archive each task in tw"
        subtasks = gtdlist.get_tasks()
        if not subtasks:
            logger.info("Got to be lazy there were no tasks")
            self.emit("list-removed", gtdlist)
        else:
            for task in subtasks:
                self.delete_task(task)


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
