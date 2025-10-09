<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="html" encoding="UTF-8" indent="yes"/>
    <xsl:template match="/">
        <html>
            <head>
                <title>Mini Spotify</title>
                <link rel="stylesheet" type="text/css" href="../static/style.css"/>
            </head>
            <body>
                <div class="container">
                    <!-- Header -->
                    <header class="header">
                        <div class="header-content">
                            <h1> Mini Spotify</h1>
                        </div>
                    </header>
                    
                    <!-- Sección de Artistas -->
                    <section class="section">
                        <h2> Artistas</h2>
                        <div class="artists-grid">
                            <xsl:for-each select="spotify/artistas/artista">
                                <div class="artist-card">
                                    <div class="artist-avatar">
                                        <xsl:value-of select="substring(nombre, 1, 1)"/>
                                    </div>
                                    <h3>
                                        <xsl:value-of select="nombre"/>
                                    </h3>
                                    <p class="country">📍
                                        <xsl:value-of select="pais"/>
                                    </p>
                                    <div class="artist-id">
                                        <xsl:value-of select="@id"/>
                                    </div>
                                </div>
                            </xsl:for-each>
                        </div>
                    </section>
                    
                    <!-- Sección de Álbumes -->
                    <section class="section">
                        <h2> Álbumes</h2>
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
                                            <xsl:value-of select="@id"/>
                                        </div>
                                    </div>
                                </div>
                            </xsl:for-each>
                        </div>
                    </section>
                    
                    <!-- Sección de Canciones -->
                    <section class="section">
                        <h2> Todas las Canciones</h2>
                        <div class="songs-list">
                            <div class="song-header">
                                <span>TÍTULO</span>
                                <span>ÁLBUM</span>
                                <span>GÉNERO</span>
                                <span>DURACIÓN</span>
                            </div>
                            <xsl:for-each select="spotify/canciones/cancion">
                                <div class="song-row">
                                    <div class="song-title">
                                        <span class="title">
                                            <xsl:value-of select="titulo"/>
                                        </span>
                                        <xsl:if test="featuring">
                                            <span class="featuring"> ft.
                                                <xsl:for-each select="/spotify/artistas/artista[@id=current()/featuring]">
                                                    <xsl:value-of select="nombre"/>
                                                </xsl:for-each>
                                            </span>
                                        </xsl:if>
                                    </div>
                                    <div class="song-album">
                                        <xsl:for-each select="/spotify/albumes/album[@id=current()/@album_id]">
                                            <xsl:value-of select="titulo"/>
                                        </xsl:for-each>
                                    </div>
                                    <div class="song-genre">
                                        <span class="genre-tag">
                                            <xsl:value-of select="genero"/>
                                        </span>
                                    </div>
                                    <div class="song-duration">
                                        <xsl:value-of select="duracion"/>
                                    </div>
                                </div>
                            </xsl:for-each>
                        </div>
                    </section>
                    
                    <!-- Sección del Formulario -->
                    <section class="section">
                        <h2> Añadir Nueva Canción</h2>
                        <form id="form-anadir-cancion" class="add-song-form">
                            <div class="form-row">
                                <label for="titulo">Título:</label>
                                <input type="text" id="titulo" required="required"/>
                            </div>
                            <div class="form-row">
                                <label for="artista_nombre">Artista:</label>
                                <input type="text" id="artista_nombre" required="required"/>
                            </div>
                            <div class="form-row">
                                <label for="album_titulo">Álbum:</label>
                                <input type="text" id="album_titulo" required="required"/>
                            </div>
                            <div class="form-row">
                                <label for="genero">Género:</label>
                                <input type="text" id="genero" required="required"/>
                            </div>
                            <div class="form-row">
                                <label for="duracion">Duración:</label>
                                <input type="text" id="duracion" placeholder="mm:ss" required="required"/>
                            </div>
                            <button type="submit">Añadir Canción</button>
                        </form>
                    </section>
                    
                    <footer class="footer">
                        <p> Mini-Spotify </p>
                    </footer>
                </div>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
