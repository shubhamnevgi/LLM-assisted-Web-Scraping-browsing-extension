document.getElementById("scrape").addEventListener("click", async () => {
    const url = document.getElementById("url").value;
    const description = document.getElementById("description").value;
    const format = document.getElementById("format").value;

    // Insert progress UI: a progress bar and a timer display
    document.getElementById("output").innerHTML = `
        <div id="progress-container">
            <div class="progress">
                <div id="progress-bar" class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" 
                    style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
            </div>
            <p id="timer-display" class="mt-2">Elapsed Time: 0s</p>
        </div>
    `;

    // Start timer and progress simulation
    let startTime = Date.now();
    let estimatedTotalTime = 30000; // Estimated time (30 seconds). Adjust as needed.
    let progressInterval = setInterval(() => {
        let elapsed = Date.now() - startTime;
        let seconds = Math.floor(elapsed / 1000);
        document.getElementById("timer-display").innerText = `Elapsed Time: ${seconds}s`;
        // Simulate progress percentage up to 99% until complete.
        let percent = Math.min((elapsed / estimatedTotalTime) * 100, 99);
        percent = Math.floor(percent);
        let progressBar = document.getElementById("progress-bar");
        progressBar.style.width = percent + "%";
        progressBar.innerText = percent + "%";
    }, 500);

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

        // Clear the progress interval and set progress to 100%
        clearInterval(progressInterval);
        let progressBar = document.getElementById("progress-bar");
        progressBar.style.width = "100%";
        progressBar.innerText = "100%";

        if (data.status === "success") {
            let previewData = "";
            if (format === "excel" && data.preview) {
                previewData = `<div style="overflow: auto; max-height: 300px; border: 1px solid #ccc; padding: 5px;">
                    ${data.preview}
                    </div>`;
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
        clearInterval(progressInterval);
        document.getElementById("output").innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
});