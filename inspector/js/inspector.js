(function() {

    console.log("Inspector JS loaded (SPA-safe).");

    // Global flags
    window.__INSPECT_MODE = false;
    window.__selenium_clicked_element = null;

    function getXPath(el) {
        if (el.id) return '//*[@id="' + el.id + '"]';
        const parts = [];
        while (el && el.nodeType === Node.ELEMENT_NODE) {
            let index = 1, sibling = el.previousSibling;
            while (sibling) {
                if (sibling.nodeType === Node.ELEMENT_NODE &&
                    sibling.nodeName === el.nodeName) {
                    index++;
                }
                sibling = sibling.previousSibling;
            }
            parts.unshift(el.nodeName + "[" + index + "]");
            el = el.parentNode;
        }
        return "/" + parts.join("/");
    }

    function getCssSelector(el) {
        if (el.id) return "#" + el.id;
        if (el.className) {
            return el.tagName.toLowerCase() + "." +
                el.className.trim().replace(/\s+/g, ".");
        }
        return el.tagName.toLowerCase();
    }

    // Remove old listeners before re-attaching (important for SPA reloads)
    function clearListeners() {
        document.removeEventListener("mouseover", hoverListener, true);
        document.removeEventListener("mouseout", outListener, true);
        document.removeEventListener("click", clickListener, true);
    }

    function hoverListener(e) {
        if (!window.__INSPECT_MODE) return;
        e.target.style.outline = "2px solid red";
    }

    function outListener(e) {
        if (!window.__INSPECT_MODE) return;
        e.target.style.outline = "";
    }

    function clickListener(e) {
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
    }

    function attachListeners() {
        clearListeners(); // Important for SPA route changes
        document.addEventListener("mouseover", hoverListener, true);
        document.addEventListener("mouseout", outListener, true);
        document.addEventListener("click", clickListener, true);
        console.log("Inspector listeners attached.");
    }

    // Initial attach
    attachListeners();

    // SPA-safe automatic reattachment
    const observer = new MutationObserver((mutations) => {
        // Reattach listeners whenever the DOM changes significantly
        attachListeners();
    });

    observer.observe(document.documentElement, {
        childList: true,
        subtree: true
    });

})();
