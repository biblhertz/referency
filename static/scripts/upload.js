let dropArea;

// ************************ Drag and drop ***************** //
window.onload = function () {
  dropArea = document.getElementById("drop-area");
  // Prevent default drag behaviors
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  // Highlight drop area when item is dragged over it
  ["dragenter", "dragover"].forEach((eventName) => {
    dropArea.addEventListener(eventName, highlight, false);
  });
  ["dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, unhighlight, false);
  });

  // Handle dropped files
  dropArea.addEventListener("drop", handleDrop, false);
};

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function highlight(e) {
  dropArea.classList.add("highlight");
}

function unhighlight(e) {
  dropArea.classList.remove("highlight");
}

function handleDrop(e) {
  var files = e.dataTransfer.files;
  if (checkFileType(files[0].type)) {
    let fileInput = document.querySelector('input[type="file"]');
    fileInput.files = files;
    previewFile(files[0]);
  } else alert("Please select a word file");
}

function showLoading() {
  let fileInput = document.querySelector('input[type="file"]');
  if (fileInput.files.length === 1) {
    document.querySelector(".form-container").style = "display:none !important";
    document.querySelector(".loading").style = "display:block !important";
  }
}

function showLoadingService() {
    document.querySelector(".container").style = "display:none !important";
    document.querySelector(".loading").style = "display:block !important";
}

function handleFile(file) {
  console.log(file);
  if (checkFileType(file.type) || checkFileName(file.name)) {
    previewFile(file);
  } else alert("Supported types are: doc,docx,odt and tei xml.");
}

function checkFileType(type) {
  switch (type) {
    case "application/vnd.oasis.opendocument.text":
      return true;
    case "doc":
      return true;
    case "docx":
      return true;
    case "text/xml":
      return true;
    default:
      return false;
  }
}
function checkFileName(name) {
  let rightType = name.split('.').pop();
  switch (rightType) {
    case "doc":
      return true;
    case "docx":
      return true;
    case "odt":
      return true;
    case "xml":
      return true;
    default:
      return false;
  }
}
function previewFile(file) {
  if (document.getElementById("gallery").children.length != 0) {
    document.getElementById("gallery").innerHTML = "";
  }
  let img = document.createElement("img");
  let fileInfo = document.createElement("div");
  fileInfo.innerHTML =
    "<h1>" + file.name + "</h1><h1>" + humanFileSize(file.size) + "</h1>";
  img.src = "../static/img/loading_file.png";
  document.getElementById("gallery").appendChild(img);
  document.getElementById("gallery").appendChild(fileInfo);
}

/**
 * Format bytes as human-readable text.
 *
 * @param bytes Number of bytes.
 * @param si True to use metric (SI) units, aka powers of 1000. False to use
 *           binary (IEC), aka powers of 1024.
 * @param dp Number of decimal places to display.
 *
 * @return Formatted string.
 */
function humanFileSize(bytes, si = false, dp = 1) {
  const thresh = si ? 1000 : 1024;

  if (Math.abs(bytes) < thresh) {
    return bytes + " B";
  }

  const units = si
    ? ["kiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    : ["kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
  let u = -1;
  const r = 10 ** dp;

  do {
    bytes /= thresh;
    ++u;
  } while (
    Math.round(Math.abs(bytes) * r) / r >= thresh &&
    u < units.length - 1
  );

  return bytes.toFixed(dp) + " " + units[u];
}
