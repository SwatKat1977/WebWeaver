console.log("Inspector script injected.");

// Global buffered state
window.__INSPECT_MODE = window.__INSPECT_MODE || false;
window.__FORCE_INSPECT_MODE = window.__FORCE_INSPECT_MODE || false;
window.__RECORD_MODE = window.__RECORD_MODE || false;

window.__recorded_actions = window.__recorded_actions || [];
window.__recorded_outgoing = window.__recorded_outgoing || [];

function now() { return Date.now(); }

// Restore Inspect Mode after navigation only if requested
if (window.__FORCE_INSPECT_MODE === true) {
    window.__INSPECT_MODE = true;
}

// Disable inspect mode if not used
if (window.__FORCE_INSPECT_MODE === false) {
    window.__INSPECT_MODE = false;
}

function getCssSelector(el) {
    if (el.id) return "#" + el.id;
    if (el.className)
        return el.tagName.toLowerCase() + "." +
               el.className.trim().replace(/\s+/g, ".");
    return el.tagName.toLowerCase();
}

function getXPath(el) {
    if (el.id) return `//*[@id="${el.id}"]`;
    const parts = [];
    while (el && el.nodeType === 1) {
        let index = 1;
        let sibling = el.previousSibling;
        while (sibling) {
            if (sibling.nodeType === 1 && sibling.nodeName === el.nodeName) index++;
            sibling = sibling.previousSibling;
        }
        parts.unshift(el.nodeName + "[" + index + "]");
        el = el.parentNode;
    }
    return "/" + parts.join("/");
}

// --------------------
// Hover highlight (INSPECT MODE ONLY)
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
// CLICK listener
// --------------------
// --------------------
// CLICK listener
// --------------------
document.addEventListener("click", function(e) {

    // INSPECT MODE → block click + send element info
    if (window.__INSPECT_MODE === true) {
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
    }

    // RECORD MODE → record, and for links delay navigation slightly
    if (window.__RECORD_MODE === true) {
        const el = e.target;
        const ev = {
            type: "click",
            selector: getCssSelector(el),
            xpath: getXPath(el),
            x: e.clientX,
            y: e.clientY,
            time: now()
        };

        window.__recorded_actions.push(ev);
        window.__recorded_outgoing.push(ev);

        // If the click was on (or inside) a link, delay navigation
        const link = el.closest ? el.closest("a[href]") : null;
        if (link && link.href) {
            // Stop the browser from navigating *right now*
            e.preventDefault();
            const url = link.href;

            console.log("Recorded link click, delaying navigation to:", url);

            // Give Python's 100ms poll loop time to read __recorded_outgoing
            setTimeout(() => {
                window.location.href = url;
            }, 200);
        }
    }

}, true);


// --------------------
// INPUT listener (RECORD MODE ONLY)
// --------------------
document.addEventListener("input", function(e) {
    if (!window.__RECORD_MODE) return;

    const el = e.target;
    if (!el) return;

    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
        const ev = {
            type: "input",
            selector: getCssSelector(el),
            xpath: getXPath(el),
            value: el.value,
            time: now()
        };
        window.__recorded_actions.push(ev);
        window.__recorded_outgoing.push(ev);
    }
}, true);

// --------------------
// Hover listeners
// --------------------
document.addEventListener("mouseover", hoverListener, true);
document.addEventListener("mouseout", outListener, true);
