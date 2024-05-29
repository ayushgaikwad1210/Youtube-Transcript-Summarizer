/*
    This script is responsible for the functionality of the Youtube Transcript Summarizer Chrome extension's popup.
    When the "Summarize" button is clicked, it sends a request to the Flask server to fetch the summarized transcript
    of the currently active YouTube video. The maximum length of the summary is fixed to 200 words and the selected language can be specified.
    The summary is then displayed in the popup.
*/
const summarizeBtn = document.getElementById("summarize");
const downloadBtn = document.getElementById("download");

summarizeBtn.addEventListener("click", function() {
    summarizeBtn.disabled = true;
    summarizeBtn.innerHTML = "Summarizing...";
    downloadBtn.style.display = "none";
    chrome.tabs.query({ currentWindow: true, active: true }, function(tabs) {
        var url = tabs[0].url;
        var language = document.getElementById("language").value || "en"; // Default language is English
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:5000/summary?url=" + url + "&language=" + language, true);
        xhr.onload = function() {
            var text = xhr.responseText;
            const output = document.getElementById("output");
            if (xhr.status === 404) {
                output.innerHTML = "No subtitles available for this video";
            } else {
                output.innerHTML = text;
                downloadBtn.style.display = "block"; // Show download button
                downloadBtn.addEventListener("click", function() {
                    // Trigger download action
                    downloadSummary(text);
                });
            }
            summarizeBtn.disabled = false;
            summarizeBtn.innerHTML = "Summarize";
        }
        xhr.send();
    });
});

function downloadSummary(summaryText) {
    // Create a new Blob object
    var blob = new Blob([summaryText], { type: "text/plain;charset=utf-8" });
    // Create a temporary anchor element
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    // Set the file name
    a.download = "summary.txt";
    // Append the anchor to the body
    document.body.appendChild(a);
    // Click the anchor to trigger download
    a.click();
    // Remove the anchor from the body
    document.body.removeChild(a);
}
