function isValidHttpUrl(string) {
    // https://stackoverflow.com/questions/5717093/check-if-a-javascript-string-is-a-url
    let url;
    
    try {
      url = new URL(string);
    } catch (_) {
      return false;  
    }
  
    return url.protocol === "http:" || url.protocol === "https:";
}

function isValidCardlistUrl(urlString) {
    let validCubeHosts = ["dreamborn.ink", "lorcana.gg"];
    if (!isValidHttpUrl(urlString)) {
        return false;
    } 

    let url = new URL(urlString);
    if (!validCubeHosts.includes(url.host)) {
        return false;
    }
    
    return true;
}

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
    console.error(errorText);
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
        popToastNotification(`Failed. Error Code: ${xhr.status}`, true);
        return;
    }
    errorResponse = JSON.parse(xhr.responseText);
    if (!errorResponse.lcc_error) {
        console.log("not lcc_error");
        showGenericError(xhr.status);
        popToastNotification(`Failed. Error Code: ${xhr.status}`, true);
        return;
    }

    // lcc error case
    showError("Error: " + errorResponse.user_facing_message);
    popToastNotification(`${errorResponse.user_facing_message}`, true);
    console.log("Error: " + errorResponse.user_facing_message);
}

function popToastNotification(textContent, isError=false) {
    let popup = document.createElement("div");
    popup.textContent = textContent;
    popup.style.position = "fixed";
    popup.style.bottom = "20px";
    popup.style.right = "20px";
    popup.style.backgroundColor = "lightgreen";
    popup.style.padding = "10px";
    popup.style.borderRadius = "5px";
    popup.style.boxShadow = "0 0 10px rgba(0, 0, 0, 0.1)";
    if (isError) {
        popup.style.backgroundColor = "lightcoral";
    }
    document.body.appendChild(popup);

    setTimeout(() => {
        document.body.removeChild(popup);
    }, 10000);
}

function request(url, data, onSuccessHandler, onErrorHandler, verb='POST') {
    var xhr = new XMLHttpRequest();
    xhr.open(verb, url, true);
    if (data) {
        xhr.setRequestHeader("Content-Type", "application/json");
    }
    xhr.onreadystatechange = function () {
        if (xhr.readyState !== 4) {
            return;
        }
        
        // success
        if (xhr.status < 300 && xhr.status >= 200) {
            console.log("responseText: " + xhr.responseText);
            if (onSuccessHandler) {
                onSuccessHandler(xhr.responseText);
            }
            return;
        } 

        // error
        if (xhr.status >= 300) {
            handleNon200Response(xhr);
            console.log(xhr.statusText)
            if (onErrorHandler) {
                onErrorHandler(xhr);
            }
        }
    };
    xhr.send(data);
}