document.getElementById("scrape").addEventListener("click", async () => {
    const url = document.getElementById("url").value;
    const description = document.getElementById("description").value;
    const format = document.getElementById("format").value;

    // Show loading message
    document.getElementById("output").innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Scraping and parsing...</p>
        </div>
    `;

    try {
        // Send request to the FastAPI backend
        const response = await fetch("http://localhost:8000/scrape_and_parse/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                url: url,
                parse_description: description,
                output_format: format,
            }),
        });

        const data = await response.json();

        if (data.status === "success") {
            // Display parsed data preview for Excel as an HTML table
            let previewData = "";
            if (format === "excel" && data.preview) {
                previewData = `<div style="overflow: auto; max-height: 300px; border: 1px solid #ccc; padding: 5px;">
                ${data.preview}
                </div>`; // Use the HTML table for preview
            } else {
                previewData = `<textarea class="form-control" readonly>${data.data}</textarea>`;
            }

            document.getElementById("output").innerHTML = `
                <p>Parsed data preview:</p>
                ${previewData}
                <button id="download" class="btn btn-success w-100 mt-3">Download ${format.toUpperCase()}</button>
            `;

            // Add download functionality
            document.getElementById("download").addEventListener("click", () => {
                let blob;
                if (format === "excel") {
                    // Decode base64 string for Excel
                    const byteCharacters = atob(data.data);
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }
                    const byteArray = new Uint8Array(byteNumbers);
                    blob = new Blob([byteArray], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
                } else {
                    blob = new Blob([data.data], {
                        type: format === "json" ? "application/json" :
                               format === "xml" ? "application/xml" :
                               "text/csv",
                    });
                }

                const link = document.createElement("a");
                link.href = URL.createObjectURL(blob);
                link.download = `parsed_data.${format === "excel" ? "xlsx" : format}`;
                link.click();
            });
        } else {
            document.getElementById("output").innerHTML = `<p style="color: red;">${data.message}</p>`;
        }
    } catch (error) {
        document.getElementById("output").innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
});
