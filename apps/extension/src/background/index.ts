// Background service worker for Prompt Advisor extension

chrome.runtime.onInstalled.addListener(() => {
  // Create context menu item for selected text
  chrome.contextMenus.create({
    id: "optimize-selection",
    title: "Optimize Selected Prompt",
    contexts: ["selection"]
  });

  // Create context menu item on action icon (right-click)
  chrome.contextMenus.create({
    id: "open-side-panel",
    title: "Open Prompt Advisor Side Panel",
    contexts: ["action"]
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (!tab || !tab.windowId) return;

  if (info.menuItemId === "optimize-selection") {
    const selectedText = info.selectionText;
    if (selectedText) {
      // Store the selection in local storage for the side panel to consume
      await chrome.storage.local.set({ pendingSelection: selectedText });
      
      // Open the side panel inside the current window context
      try {
        await chrome.sidePanel.open({ windowId: tab.windowId });
      } catch (err) {
        console.error("Failed to open side panel via context menu:", err);
      }
    }
  } else if (info.menuItemId === "open-side-panel") {
    try {
      await chrome.sidePanel.open({ windowId: tab.windowId });
    } catch (err) {
      console.error("Failed to open side panel via action context:", err);
    }
  }
});
