function updateTitles(icon, title, subtitle) {

    const favicon = document.getElementById('favicon');
    favicon.href = "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>" + icon + "</text></svg>";

    document.title = title;

    const headerTitle = document.getElementById('theTitle');
    headerTitle.textContent = icon + " " + title;


    const headerSubtitle = document.getElementById('theSubtitle');
    headerSubtitle.textContent = subtitle;

}

async function readMarkdownAsHTML(filename) {
    const response = await fetch(filename + "?v=" + Date.now());

    if (!response.ok) {
        throw new Error(`Error al cargar ${filename}: ${response.status} ${response.statusText}`);
    }

    const markdownText = await response.text();
    const body = markdownText.split('<!-- BODY -->')[1];
    const htmlContent = marked.parse(body);

    return htmlContent;
}

async function readConfFromJSON(filename) {
    const response = await fetch(filename + "?v=" + Date.now());

    if (!response.ok) {
        throw new Error(`Error al cargar ${filename}: ${response.status} ${response.statusText}`);
    }

    const json = await response.json();
    return json;
}

async function loadReadme() {
    try {
        const conf = await readConfFromJSON("assets/conf.json");
        const htmlContent = await readMarkdownAsHTML("README.md");

        // Insertar el contenido HTML
        document.getElementById('content').innerHTML = htmlContent;
        document.getElementById('content').classList.remove('loading');
        document.getElementById('header').classList.remove('hide');

        // Actualizar los títulos
        updateTitles(conf.icon, conf.title, conf.subtitle);

        // title.style.display = 'none';
        // subtitle.style.display = 'none';

    } catch (error) {
        console.error('Error:', error);
        document.getElementById('content').innerHTML = `
                    <div class="error">
                        <h3>❌ ${error.message}</h3>
                        <p><strong>Possible solutions:</strong></p>
                        <ul>
                            <li>✅ Make sure a thefile exists in the same directory</li>
                            <li>🌐 Run the HTML from a web server (not as a local file)</li>
                            <li>⚙️ Verify that the web server is configured to serve .md files</li>
                            <li>🔒 Check the permissions of the file</li>
                        </ul>
                    </div>
                `;

        document.getElementById('content').classList.remove('loading');
    }
}

// Cargar el README cuando se carga la página
window.addEventListener('load', loadReadme);