from gi.repository import Gtk

class ViewContainer(Gtk.Stack):
    def __init__(self, title, headerBar, selectionToolbar, useStack):
        Gtk.Stack.__init__(self, transition_type=Gtk.StackTransitionType.CROSSFADE)
        self._grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self._iconWidth = -1
        self._iconHeight = 128
        self._offset = 0
        self._adjustmentValueId = 0
        self._adjustmentChangedId = 0
        self._scrollbarVisibleId = 0
        self._model = Gtk.ListStore.new([
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GdkPixbuf.Pixbuf,
            GObject.TYPE_OBJECT,
            GObject.TYPE_BOOLEAN,
            GObject.TYPE_INT,
            GObject.TYPE_STRING,
            GObject.TYPE_BOOLEAN,
            GObject.TYPE_BOOLEAN
        ])
        self.view = Gd.MainView(
            shadow_type=Gtk.ShadowType.NONE
        )
        self.view.set_view_type(Gd.MainViewType.ICON)
        self.view.set_model(self._model)
        self.selectionToolbar = selectionToolbar
        box = new Gtk.Box({orientation: Gtk.Orientation.VERTICAL})
        box.pack_start(self.view, True, True, 0)
        if useStack:
            self.stack = Gd.Stack(
                transition_type=Gd.StackTransitionType.SLIDE_RIGHT,
            )
            dummy = Gtk.Frame(visible=False)
            self.stack.add_named(dummy, "dummy")
            self.stack.add_named(_box, "artists")
            self.stack.set_visible_child_name("dummy")
            self._grid.add(self.stack)
        else:
            self._grid.add(box)

        self._loadMore = new Widgets.LoadMoreButton(self._getRemainingItemCount)
        box.pack_end(self._loadMore.widget, False, False, 0)
        self._loadMore.widget.connect("clicked", self.populate)
        self.view.connect('item-activated', self._onItemActivated)
        self._cursor = None
        self.headerBar = headerBar
        self.headerBar._selectButton.connect('toggled', self._onHeaderBarToggled)

        headerBar._cancelButton.connect('clicked', self._onCancelButtonClicked)

        self.title = title
        self.add(self._grid)

        self.show_all()
        self._items = []
        self._loadMore.widget.hide()
        self._connectView()
        self._symbolicIcon = albumArtCache.makeDefaultIcon(self._iconHeight, self._iconWidth)

        self._init = False
        grilo.connect('ready', _onGriloReady)
        self.header_bar.connect('state-changed', self._onStateChanged)
        self.view.connect('view-selection-changed', self._onViewSelectionChanged)

    def _onHeaderBarToggled(self, button):
        if button.get_active():
            self.view.set_selection_mode(True)
            self.header_bar.setSelectionMode(True)
            self.selection_toolbar.eventbox.set_visible(True)
            self.selection_toolbar._add_to_playlist_button.sensitive = False
        else:
            self.view.set_selection_mode(False)
            self.header_bar.setSelectionMode(False)
            self.selection_toolbar.eventbox.set_visible(False)

    def _onCancelButtonClicked(self, button):
        self.view.set_selection_mode(False)
        headerBar.setSelectionMode(False)

    def _onGriloRead(self):
        if self.headerBar.get_stack().get_visible_child() == self and self._init == False)
            self._populate()
        self.headerBar.get_stack().connect('notify::visible-child',
            self._onHeaderBarVisible)

    def _onHeaderBarVisible(self, widget, param):
        if self == widget.get_visible_child() and !self._init:
            self._populate()

    def _onViewSelectionChanged(self):
        items = self.view.get_selection()
        self.selectionToolbar._add_to_playlist_button.sensitive = items.length > 0

    def _populate(self):
        self._init = True
        self.populate()

    def _onStateChanged(self):
        pass

    def _connectView(self):
        self._adjustmentValueId = self.view.vadjustment.connect(
            'value-changed',
            self._onScrolledWinChange)

        self._adjustmentChangedId = self.view.vadjustment.connect(
            'changed',
            self._onScrolledWinChange)

        self._scrollbarVisibleId = self.view.get_vscrollbar().connect(
            'notify::visible',
            self._onScrolledWinChange)

        self._onScrolledWinChange()


    def _onScrolledWinChange(self):
        vScrollbar = self.view.get_vscrollbar()
        adjustment = self.view.vadjustment
        revealAreaHeight = 32

        #if there's no vscrollbar, or if it's not visible, hide the button
        if !vScrollbar or !vScrollbar.get_visible():
            self._loadMore.setBlock(True)
            return

        value = adjustment.value
        upper = adjustment.upper
        page_size = adjustment.page_size

        end = False
        #special case self values which happen at construction
        if (value == 0) && (upper == 1) && (page_size == 1):
            end = False
        else:
            end = !(value < (upper - page_size - revealAreaHeight))
        if self._getRemainingItemCount() <= 0:
            end = False
        self._loadMore.setBlock(!end)

    def populate:
        pass

    def _addItem(self, source, param, item):
        if item != None:
            self._offset += 1
            iter = self._model.append()
            artist = "Unknown"
            if item.get_author() != None;
                artist = item.get_author()
            if item.get_string(Grl.METADATA_KEY_ARTIST) != None;
                artist = item.get_string(Grl.METADATA_KEY_ARTIST)
            if (item.get_title() == None) and (item.get_url() != None):
                item.set_title (extractFileName(item.get_url()))
            try:
                if item.get_url():
                    self.player.discoverer.discover_uri(item.get_url())
                self._model.set(
                        iter,
                        [0, 1, 2, 3, 4, 5, 7, 8, 9, 10],
                        [toString(item.get_id()), "", item.get_title(), artist, self._symbolicIcon, item, -1, nowPlayingIconName, False, False]
                    )
            except:
                print("failed to discover url " + item.get_url())
                self._model.set(
                        iter,
                        [0, 1, 2, 3, 4, 5, 7, 8, 9, 10],
                        [toString(item.get_id()), "", item.get_title(), artist, self._symbolicIcon, item, -1, errorIconName, False, True]
                    )
            }
            GLib.idle_add(300, lambda item,iter: self._updateAlbumArt, item, iter)

    def _getRemainingItemCount(self):
        count = -1
        if self.countQuery != None:
            cursor = tracker.query(self.countQuery, None)
            if cursor != None and cursor.next(None):
                count = cursor.get_integer(0)
        return count - self._offset

    def _updateAlbumArt(self,item, iter):
        albumArtCache.lookupOrResolve(item, self._iconWidth, self._iconHeight, _albumArtCacheLookUp)
        return False

    def _albumArtCacheLookUp(self, icon):
        if icon:
            self._model.set_value(iter, 4, albumArtCache.makeIconFrame(icon))
        else:
            self._model.set_value(iter, 4, None)
            self.emit("album-art-updated")

    def _addListRenderers(self):
        pass

    def _onItemActivated(self, widget, id, path):
        pass

#Class for the Empty View
class Empty(Gtk.Stack):
    def __init__(self, headerBar, player):
        Gtk.Stack.__init__(self, transition_type=Gtk.StackTransitionType.CROSSFADE)
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/music/NoMusic.ui')
        widget = builder.get_object('container')
        self.add(widget)
        self.show_all()

class Albums(ViewContainer):
    def __init__(self, HeaderBar, selectionToolbar, player):
        ViewContainer.__init__("Albums", headerBar,selectionToolbar)
        self.view.set_view_type(Gd.MainViewType.ICON)
        self.countQuery = Query.album_count
        self._albumWidget = new Widgets.AlbumWidget(player)
        self.add(self._albumWidget)
        self.headerBar.setState (1)

    def _onStateChanged(self, widget):
        if self.headerBar.get_stack() != None and
            self == self.headerBar.get_stack().get_visible_child())
            self.visible_child = self._grid

    def _onItemActivated(self, widget, id, path):
        iter = self._model.get_iter (path)[1]
        title = self._model.get_value (iter, 2)
        artist = self._model.get_value (iter, 3)
        item = self._model.get_value (iter, 5)
        self._albumWidget.update (artist, title, item, self.headerBar,self.selectionToolbar)
        self.headerBar.setState (0)
        self.headerBar.header_bar.title = title
        self.headerBar.header_bar.sub_title = artist
        self.visible_child = self._albumWidget

    def populate(self):
        if grilo.tracker != None:
            grilo.populateAlbums (self._offset, self._addItem, None)

class Songs(ViewContainer):
    def __init__(self, headerBar, selectionToolbar, player):
        ViewContainer.__init__("Songs", headerBar, selectionToolbar)
        self.countQuery = Query.songs_count
        self._items = {}
        self.isStarred = None
        self.view.set_view_type(Gd.MainViewType.LIST)
        self.view.get_generic_view().get_style_context().add_class("songs-list")
        self._iconHeight = 32
        self._iconWidth = 32
        self._symbolicIcon = albumArtCache.makeDefaultIcon(self._iconHeight, self._iconWidth)
        self._addListRenderers()
        self.player = player
        self.player.connect('playlist-item-changed', Lang.bind(self, self.updateModel))

    def _onItemActivated(self, widget, id, path):
        iter = self._model.get_iter(path)[1]
        if self._model.get_value(iter, 8) != errorIconName:
            self.player.setPlaylist("Songs", None, self._model, iter, 5)
            self.player.setPlaying(True)

    def updateModel(self, player, playlist, currentIter):
        if playlist != self._model:
            return False
        if self.iterToClean:
            self._model.set_value(self.iterToClean, 10, False)

        self._model.set_value(currentIter, 10, True)
        self.iterToClean = currentIter.copy()
        return False

    def _addItem(self, source, param, item):
        if item != None:
            self._offset += 1
            iter = self._model.append()
            if (item.get_title() == None) && (item.get_url() != None):
                item.set_title (extractFileName(item.get_url()))
            try:
                if item.get_url():
                    self.player.discoverer.discover_uri(item.get_url())
                self._model.set(
                        iter,
                        [5, 8, 9, 10],
                        [item, nowPlayingIconName, false, false]
                    )
            except:
                print("failed to discover url " + item.get_url())
                self._model.set(
                        iter,
                        [5, 8, 9, 10],
                        [item, errorIconName, False, True]
                    )

    def _addListRenderers(self):
        listWidget = self.view.get_generic_view()
        cols = listWidget.get_columns()
        cells = cols[0].get_cells()
        cells[2].visible = False
        nowPlayingSymbolRenderer = new Gtk.CellRendererPixbuf()
        columnNowPlaying = new Gtk.TreeViewColumn()
        nowPlayingSymbolRenderer.xalign = 1.0
        columnNowPlaying.pack_start(nowPlayingSymbolRenderer, False)
        columnNowPlaying.fixed_width = 24
        columnNowPlaying.add_attribute(nowPlayingSymbolRenderer, "visible", 10)
        columnNowPlaying.add_attribute(nowPlayingSymbolRenderer, "icon_name", 8)
        listWidget.insert_column(columnNowPlaying, 0)

        titleRenderer = new Gtk.CellRendererText(xpad=0)
        listWidget.add_renderer(titleRenderer, self._onListWidgetTitleRender)
        starRenderer = new Gtk.CellRendererPixbuf(xpad=32)
        listWidget.add_renderer(starRenderer, self._onListWidgetStarRender)
        durationRenderer = Gd.StyledTextRenderer(xpad=32)
        durationRenderer.add_class('dim-label')
        listWidget.add_renderer(durationRenderer, self._onListWidgetDurationRender)
        artistRenderer = Gd.StyledTextRenderer(xpad=32)
        artistRenderer.add_class('dim-label')
        artistRenderer.ellipsize = Pango.EllipsizeMode.END
        listWidget.add_renderer(artistRenderer, self._onListWidgetArtistRender)
        typeRenderer = Gd.StyledTextRenderer(xpad: 32)
        typeRenderer.add_class('dim-label')
        typeRenderer.ellipsize = Pango.EllipsizeMode.END
        listWidget.add_renderer(typeRenderer, self._onListWidgetTypeRender)

    def _onListWidgetTitleRender(self, col, cell, model, iter):
        item = model.get_value(iter,5)
        titleRenderer.xalign = 0.0
        titleRenderer.yalign = 0.5
        titleRenderer.height = 48
        titleRenderer.ellipsize = Pango.EllipsizeMode.END
        titleRenderer.text = item.get_title()

    def _onListWidgetStarRender(self, col, cell, model, iter):
        showstar = model.get_value(iter, 9)
        if(showstar):
            starRenderer.icon_name = starIconName
        else:
            starRenderer.pixbuf = None

    def _onListWidgetDurationRender(self, col, cell, model, iter) {
        item = model.get_value(iter, 5)
        if item:
            duration = item.get_duration ()
            minutes = parseInt(duration / 60)
            seconds = duration % 60
            time = None
            if seconds < 10:
                time =  minutes + ":0" + seconds
            else:
                time = minutes + ":" + seconds
            durationRenderer.xalign = 1.0
            durationRenderer.text = time

    def _onListWidgetArtistRender(self, col, cell, model, iter):
        item = model.get_value(iter, 5)
        if item:
            artistRenderer.ellipsize = Pango.EllipsizeMode.END
            artistRenderer.text = item.get_string(Grl.METADATA_KEY_ARTIST)

    def _onListWidgetTypeRender(self, coll, cell, model, iter):
        item = model.get_value(iter, 5)
        if item:
            typeRenderer.ellipsize = Pango.EllipsizeMode.END
            typeRenderer.text = item.get_string(Grl.METADATA_KEY_ALBUM)

    def populate(self):
        if grilo.tracker != None:
            grilo.populateSongs (self._offset, lambda: self._addItem, None)


class Playlist(ViewContainer):
    def __init__(self, headerBar, selectionToolbar, player)
        ViewContainer.__init__("Playlists", headerBar, selectionToolbar)

class Artists (ViewContainer):
    def __init__(self, headerBar, selectionToolbar, player):
        ViewContainer.__init__("Artists", headerBar, selectionToolbar, True)
        self.player = player
        self._artists = {}
        self.countQuery = Query.artist_count
        self._artistAlbumsWidget = Gtk.Frame(
            shadow_type=Gtk.ShadowType.NONE
        )
        self.view.set_view_type(Gd.MainViewType.LIST)
        self.view.set_hexpand(False)
        self._artistAlbumsWidget.set_hexpand(True)
        self.view.get_style_context().add_class("artist-panel")
        self.view.get_generic_view().get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self._grid.attach(new Gtk.Separator({orientation: Gtk.Orientation.VERTICAL}), 1, 0, 1, 1)
        self._grid.attach(self._artistAlbumsWidget, 2, 0, 2, 2)
        self._addListRenderers()
        if Gtk.Settings.get_default().gtk_application_prefer_dark_theme:
            self.view.get_generic_view().get_style_context().add_class("artist-panel-dark")
        else:
            self.view.get_generic_view().get_style_context().add_class("artist-panel-white")
        self.show_all()

    def _populate(self, widget, param):
        selection = self.view.get_generic_view().get_selection()
        if !selection.get_selected()[0]:
            self._allIter = self._model.append()
            self._artists["All Artists".toLowerCase()] = {"iter": self._allIter, "albums": []}
            self._model.set(
                self._allIter,
                [0, 1, 2, 3],
                ["All Artists", "All Artists", "All Artists", "All Artists"]
            )
            selection.select_path(self._model.get_path(self._allIter))
            self.view.emit('item-activated', "0", self._model.get_path(self._allIter))
        self._init = True
        self.populate()

    def _addListRenderers(self):
        listWidget = self.view.get_generic_view()

        cols = listWidget.get_columns()
        cells = cols[0].get_cells()
        cells[2].visible = False

        typeRenderer = Gd.StyledTextRenderer(xpad: 0)
        typeRenderer.ellipsize = 3
        typeRenderer.xalign = 0.0
        typeRenderer.yalign = 0.5
        typeRenderer.height = 48
        typeRenderer.width = 220
        listWidget.add_renderer(typeRenderer, lambda col, cell, model, iter:
                typeRenderer.text = model.get_value(iter, 0)
        )


    def _onItemActivated(self, widget, id, path):
        children = self._artistAlbumsWidget.get_children()
        for (i=0 i<children.length i++)
            self._artistAlbumsWidget.remove(children[i])
        iter = self._model.get_iter (path)[1]
        artist = self._model.get_value (iter, 0)
        albums = self._artists[artist.toLowerCase()]["albums"]
        self.artistAlbums = None
        if self._model.get_string_from_iter(iter) == self._model.get_string_from_iter(self._allIter):
            self.artistAlbums = Widgets.AllArtistsAlbums(self.player)
        else:
            self.artistAlbums = Widgets.ArtistAlbums(artist, albums, self.player)
        self._artistAlbumsWidget.add(self.artistAlbums)

    def _addItem(self, source, param, item):
        self._offset += 1
        if :item == None:
            return
        artist = "Unknown"
        if item.get_author() != None:
            artist = item.get_author()
        if item.get_string(Grl.METADATA_KEY_ARTIST) != None:
            artist = item.get_string(Grl.METADATA_KEY_ARTIST)
        if self._artists[artist.toLowerCase()] == undefined:
            iter = self._model.append()
            self._artists[artist.toLowerCase()] = {"iter": iter, "albums": []}
            self._model.set(
                iter,
                [0, 1, 2, 3],
                [artist, artist, artist, artist]
            )

        self._artists[artist.toLowerCase()]["albums"].append(item)
        self.emit("artist-added")
    },

    def populate(self):
        if grilo.tracker != None:
            grilo.populateArtists(self._offset, lambda: self._addItem, None)
            #FIXME: We're emitting self too early, need to wait for all artists to be filled in

