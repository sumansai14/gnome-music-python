class AlbumArtCache:
    def getFromUri(self, uri, artist, album, width, height, callback) {
        if uri == None:
            return
        if self.requested_uris[uri] == undefined:
            self.requested_uris[uri] = [[callback, width, height]]
        elif self.requested_uris[uri].length > 0:
            self.requested_uris[uri].append([callback, width, height])
            return

        key = self._keybuilder_funcs[0].call(self, artist, album)
        filename = Gio.File.new_for_uri(uri)

        filename.read_async(300, None, self._fileReadSync)

    def self_fileReadSync(self, source, res):
        try:
            stream = file.read_finish(res)
            path = GLib.build_filenamev([self.cacheDir, key])

            try:
                streamInfo = stream.query_info('standard::content-type', None)
                contentType = streamInfo.get_content_type()

                if contentType == 'image/png':
                    path += '.png'
                elif contentType == 'image/jpeg':
                    path += '.jpeg'
                else:
                    print('Thumbnail is not in a supported format, not caching')
                    stream.close(None)
                    return
            except:
                print('Failed to query thumbnail content type (%s), assuming JPG')
                path += '.jpeg'
                return

            newFile = Gio.File.new_for_path(path)

            newFile.replace_async(None, false, Gio.FileCreateFlags.REPLACE_DESTINATION,
                300, None, self.newFileReadAsync)
        except:
            print (error)

    def _newFileReadAsync(self, new_file, res, error):
        outstream = new_file.replace_finish(res)
        outstream.splice_async(stream, Gio.IOStreamSpliceFlags.NONE, 300, None,
            self_spliceAsync, None)

    def _spliceAsync(self, outstream, res, error):
        if outstream.splice_finish(res) > 0) {
           for i in self.requested_uris[uri]:
               callback = self.requested_uris[uri][i][0]
               width = self.requested_uris[uri][i][1]
               height = self.requested_uris[uri][i][2]

               pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, height, width, true)
               callback(pixbuf, path)
           del self.requested_uris[uri]
