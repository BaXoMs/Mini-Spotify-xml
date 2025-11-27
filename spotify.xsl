<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output method="html" doctype-system="about:legacy-doctype" encoding="UTF-8" indent="yes" />

    <xsl:key name="artistas-by-id" match="artista" use="@id" />
    <xsl:key name="albumes-by-id" match="album" use="@id" />

    <xsl:template match="/">
        <html>
            <head>
                <title>Mini Spotify</title>
                <link rel="stylesheet" type="text/css" href="/static/style.css"/>
            </head>
            <body>
                <div class="container">
                    <header class="header">
                        <h1>Mini Spotify</h1>
                    </header>

                    <!-- SECCIÓN DE FORMULARIOS -->
                    <section class="section">
                        <div class="add-song-form">
                            <form id="form-busqueda">
                                <!-- El ID input-busqueda es clave para el script -->
                                <input type="search" id="input-busqueda" placeholder="Buscar en Todas las Canciones..."/>
                            </form>
                            <hr/>
                            <form id="form-anadir-cancion">
                                <input type="text" id="titulo" placeholder="Título" required="required"/>
                                <input type="text" id="artista_nombre" placeholder="Artista" required="required"/>
                                <input type="text" id="album_titulo" placeholder="Álbum" required="required"/>
                                <input type="text" id="genero" placeholder="Género" required="required"/>
                                <input type="text" id="duracion" placeholder="Duración (mm:ss)" required="required"/>
                                <button type="submit">Guardar Canción</button>
                            </form>
                        </div>
                    </section>

                    <!-- 1. SECCIÓN TODAS LAS CANCIONES (Movida aquí arriba) -->
                    <!-- Le agregué id="seccion-canciones" para el scroll automático -->
                    <section class="section" id="seccion-canciones">
                        <h2>Todas las Canciones</h2>
                        <div id="songs-list-container" class="songs-list">
                            <div class="song-header">
                                <span>TÍTULO</span>
                                <span>ARTISTA / ÁLBUM</span>
                                <span>GÉNERO</span>
                                <span>DURACIÓN</span>
                                <span>ACCIONES</span>
                            </div>
                            <!-- Aquí se llenan las canciones con JS o XSL si lo agregas -->
                        </div>
                    </section>

                    <!-- 2. SECCIÓN ARTISTAS -->
                    <section class="section">
                        <h2>Artistas</h2>
                        <div class="artists-grid">
                            <xsl:for-each select="spotify/artistas/artista">
                                <div class="artist-card">
                                    <div class="artist-avatar">
                                        <xsl:value-of select="substring(nombre, 1, 1)"/>
                                    </div>
                                    <h3>
                                        <xsl:value-of select="nombre"/>
                                    </h3>
                                    <p class="country">📍                                        <xsl:value-of select="pais"/>
                                    </p>
                                    <div class="artist-id">
                                        <xsl:value-of select="@id"/>
                                    </div>
                                </div>
                            </xsl:for-each>
                        </div>
                    </section>

                    <!-- 3. SECCIÓN ÁLBUMES -->
                    <section class="section">
                        <h2>Álbumes</h2>
                        <div class="albums-grid">
                            <xsl:for-each select="spotify/albumes/album">
                                <div class="album-card">
                                    <div class="album-cover">
                                        <xsl:value-of select="substring(titulo, 1, 2)"/>
                                    </div>
                                    <div class="album-info">
                                        <h3>
                                            <xsl:value-of select="titulo"/>
                                        </h3>
                                        <p class="album-year">
                                            <xsl:value-of select="anio"/>
                                        </p>
                                        <div class="album-id">
                                            Artista: <xsl:value-of select="key('artistas-by-id', @artista_id)/nombre"/>
                                        </div>
                                    </div>
                                </div>
                            </xsl:for-each>
                        </div>
                    </section>

                </div>
                <script src="/static/script.js"></script>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>