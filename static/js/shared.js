
// https://stackoverflow.com/questions/13405129/create-and-save-a-file-with-javascript
// Function to download data to a file
function download(data, filename, type) {
    var file = new Blob([data], {type: type});
    if (window.navigator.msSaveOrOpenBlob) // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
    else { // Others
        var a = document.createElement("a"),
                url = URL.createObjectURL(file);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function() {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);  
        }, 0); 
    }
}

function showError(errorText) {
    const errorTextElement = document.getElementById('errorText');
    errorTextElement.innerText = errorText;
    errorTextElement.style.display = 'block';
    errorTextElement.style.disabled = false;
}

function hideError() {
    const errorTextElement = document.getElementById('errorText');
    errorTextElement.innerText = "";
    errorTextElement.style.display = 'none';
    errorTextElement.style.disabled = true;
}

function showGenericError(httpStatus) {
    showError("An error occurred. HTTP Status: " + httpStatus);
}

function handleNon200Response(xhr) {
    console.log("content type: " + xhr.getResponseHeader('content-type'));
    if (xhr.getResponseHeader('content-type') !== 'application/json') {
        console.log("not application/json error");
        showGenericError(xhr.status);
        return;
    }
    errorResponse = JSON.parse(xhr.responseText);
    if (!errorResponse.lcc_error) {
        console.log("not lcc_error");
        showGenericError(xhr.status);
        return;
    }

    // lcc error case
    showError("Error: " + errorResponse.user_facing_message);
    console.log("Error: " + errorResponse.user_facing_message);
}