NULL =

hicolor_icon16dir = $(datadir)/icons/hicolor/16x16/apps
hicolor_icon16_DATA = hicolor/16x16/apps/org.gnome.Todo.png
hicolor_icon22dir = $(datadir)/icons/hicolor/22x22/apps
hicolor_icon22_DATA = hicolor/22x22/apps/org.gnome.Todo.png
hicolor_icon32dir = $(datadir)/icons/hicolor/32x32/apps
hicolor_icon32_DATA = hicolor/32x32/apps/org.gnome.Todo.png
hicolor_icon48dir = $(datadir)/icons/hicolor/48x48/apps
hicolor_icon48_DATA = hicolor/48x48/apps/org.gnome.Todo.png
hicolor_icon256dir = $(datadir)/icons/hicolor/256x256/apps
hicolor_icon256_DATA = hicolor/256x256/apps/org.gnome.Todo.png
hicolor_icon512dir = $(datadir)/icons/hicolor/512x512/apps
hicolor_icon512_DATA = hicolor/512x512/apps/org.gnome.Todo.png
hicolor_iconsymbolicdir = $(datadir)/icons/hicolor/symbolic/apps
hicolor_iconsymbolic_DATA = hicolor/symbolic/apps/org.gnome.Todo-symbolic.svg
hicolor_icon_files = \
	$(hicolor_icon16_DATA) \
	$(hicolor_icon22_DATA) \
	$(hicolor_icon32_DATA) \
	$(hicolor_icon48_DATA) \
	$(hicolor_icon256_DATA) \
	$(hicolor_icon512_DATA) \
	$(hicolor_iconsymbolic_DATA) \
	hicolor/org.gnome.Todo.svg

gtk_update_icon_cache = gtk-update-icon-cache -f -t $(datadir)/icons/hicolor

install-data-hook: update-icon-cache
uninstall-hook: update-icon-cache
update-icon-cache:
	@-if test -z "$(DESTDIR)"; then \
		echo "Updating Gtk icon cache."; \
		$(gtk_update_icon_cache); \
	else \
		echo "*** Icon cache not updated.  After (un)install, run this:"; \
		echo "***   $(gtk_update_icon_cache)"; \
	fi


EXTRA_DIST = \
	$(hicolor_icon_files) \
	meson.build \
	$(NULL)

-include $(top_srcdir)/git.mk
