console.log("Inspector script injected.");

window.__INSPECT_MODE = window.__INSPECT_MODE || false;
window.__FORCE_INSPECT_MODE = window.__FORCE_INSPECT_MODE || false;
window.__recorded_actions = window.__recorded_actions || [];

// Persist inspect mode only if FORCE MODE is active
if (window.__FORCE_INSPECT_MODE === true) {
    console.log("Re-enabling inspect mode after page load");
    window.__INSPECT_MODE = true;
}

// If the user has stopped inspect mode, ensure it STAYS OFF
if (window.__FORCE_INSPECT_MODE === false) {
    window.__INSPECT_MODE = false;
}

function now() { return Date.now(); }

function getCssSelector(el) {
    if (el.id) return "#" + el.id;
    if (el.className)
        return el.tagName.toLowerCase() + "." + el.className.trim().replace(/\s+/g, ".");
    return el.tagName.toLowerCase();
}

function getXPath(el) {
    if (el.id) return `//*[@id="${el.id}"]`;
    const parts = [];
    while (el && el.nodeType === 1) {
        let index = 1;
        let sib = el.previousSibling;
        while (sib) {
            if (sib.nodeType === 1 && sib.nodeName === el.nodeName) index++;
            sib = sib.previousSibling;
        }
        parts.unshift(el.nodeName + "[" + index + "]");
        el = el.parentNode;
    }
    return "/" + parts.join("/");
}

// --------------------
// Hover highlight
// --------------------
function hoverListener(e) {
    if (!window.__INSPECT_MODE) return;
    e.target.__old_outline = e.target.style.outline;
    e.target.style.outline = "2px solid red";
}

function outListener(e) {
    if (!window.__INSPECT_MODE) return;
    e.target.style.outline = e.target.__old_outline || "";
    delete e.target.__old_outline;
}

// --------------------
// Click recording
// --------------------
document.addEventListener("click", function(e) {
    if (!window.__INSPECT_MODE) return;

    e.preventDefault();
    e.stopPropagation();

    const el = e.target;

    window.__selenium_clicked_element = {
        tag: el.tagName.toLowerCase(),
        id: el.id,
        class: el.className,
        text: el.innerText,
        css: getCssSelector(el),
        xpath: getXPath(el)
    };

    window.__recorded_actions.push({
        type: "click",
        selector: getCssSelector(el),
        xpath: getXPath(el),
        x: e.clientX,
        y: e.clientY,
        time: now()
    });

    console.log("Click recorded:", window.__recorded_actions.at(-1));
}, true);

// --------------------
// Text input recording
// --------------------
document.addEventListener("input", function(e) {
    const el = e.target;
    if (!el) return;

    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
        window.__recorded_actions.push({
            type: "input",
            selector: getCssSelector(el),
            xpath: getXPath(el),
            value: el.value,
            time: now()
        });

        console.log("Input recorded:", window.__recorded_actions.at(-1));
    }
}, true);

// --------------------
// Attach hover listeners
// --------------------
document.addEventListener("mouseover", hoverListener, true);
document.addEventListener("mouseout", outListener, true);
